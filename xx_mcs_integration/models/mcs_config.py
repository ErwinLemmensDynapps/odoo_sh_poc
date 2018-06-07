# coding=utf-8
from odoo import models, fields, api, _
from suds.client import Client
from suds.sax.element import Element
import xml.etree.ElementTree as ET
from odoo.exceptions import ValidationError as VE

import logging

_logger = logging.getLogger(__name__)


class mcs_config(models.Model):
    _name = 'mcs.config'

    name = fields.Char("Name")
    stock_picking_type_id = fields.Many2one("stock.picking.type", string="Warehouse (stock picking type)")
    website_ids = fields.Many2many("website")
    mcs_shop = fields.Char("Shop")
    mcs_url = fields.Char("URL")
    mcs_username = fields.Char("Username")
    mcs_pwd = fields.Char("Password")
    mcs_version = fields.Char("Version")

    def get_connection_info(self):
        client = Client(self.mcs_url)
        return client, self.mcs_username, self.mcs_pwd, self.mcs_version

    def get_message(self, elems, fails):
        messages = []
        if fails:
            messages.append("%s Fails:\n%s\n" % (len(fails), "\n".join(fails)))
        if elems:
            messages.append("%s Pickings MCS State Updated\n%s" % (len(elems), "\n".join(elems)))
        return "\n\n".join(messages) if messages else "Nothing to Update"

    def get_message_popup(self, message):
        model = "gdf.popup"
        popup = self.env[model].create({
            "name": "MCS Update",
            "desc": message,
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": model,
            "views": [[False, "form"]],
            "res_id": popup.id,
            "target": "new",
        }

    def get_order_xml(self, pickings):
        orders = Element("orders")
        for picking in pickings:
            orderid = Element("orderid").setText(picking.name)
            orders.append(orderid)
        return orders

    def get_purchase_xml(self, pickings):
        orders = Element("purchaseorders")
        for picking in pickings:
            orderid = Element("order_number").setText(picking.origin)
            orders.append(orderid)
        return orders

    def get_stock_xml(self, products):
        stock = Element("stock")
        for product in products:
            item = Element("item")
            stock.append(item)
            sku = Element("sku").setText(product.barcode)
            item.append(sku)
        return stock

    def eq(self, mcs_qty, odoo_qty, type_):
        mcs_qty = 0.0 if mcs_qty is None else type_(mcs_qty)
        odoo_qty = 0.0 if odoo_qty is None else type_(odoo_qty)
        if not mcs_qty and not odoo_qty:
            return True
        if not mcs_qty or not odoo_qty:
            return False
        return mcs_qty == odoo_qty

    def get_picking(self):
        return self.env['stock.picking'].search([
            ("mcs_state", "not in", ["not_sent", "completed"]),
            ("state", "not in", ["cancel", "done"]),
            ("mcs_config_id", "=", self.id),
        ])

    def mcs_order_status_check_update(self, is_cron):
        log_obj = self.env["mcs.log"]
        picking_obj = self.env['stock.picking']
        mcs_state_options = [k for k, v in picking_obj._columns["mcs_state"].selection]
        client, user, pwd, version = self.get_connection_info()
        orders = Element('orders')
        order = Element('order')
        orders.append(order)
        response_str = client.service.order_status(user, pwd, version, orders.__str__().decode("UTF-8"))
        response = ET.fromstring(response_str)
        response_orders = response.findall("order")
        updated_pickings = []
        fail_pickings = []
        for response_order in response_orders:
            response_orderid = response_order.find("orderid").text
            try:
                response_status = response_order.find("status").text
                if response_status not in mcs_state_options:
                    response_status = "unknown"
                picking = picking_obj.search([("name", "=", response_orderid)])
                if len(picking) == 1 and picking.mcs_state != response_status:
                    picking.write({
                        "mcs_state": response_status,
                    })
                    updated_pickings.append(picking.name)
            except Exception, e:
                log_obj.create({
                    "name": "In 'check update' for %s" % response_orderid,
                    "desc": e,
                })
                fail_pickings.append(response_orderid)

        if is_cron:
            _logger.info(
                self.get_message(updated_pickings, fail_pickings)
            )
        else:
            return self.get_message_popup(self.get_message(updated_pickings, fail_pickings))

    @api.model
    def mcs_cron_order_status_check_update(self):
        log_obj = self.env["mcs.log"]
        for rec in self.search([]):
            try:
                rec.mcs_order_status_check_update(True)
            except Exception, e:
                log_obj.create({
                    "name": "In 'cron_check_update'",
                    "desc": "For config %s:\n%s" % (rec.name, e),
                })

    @api.multi
    def mcs_button_order_status_check_update(self):
        return self.mcs_order_status_check_update(False)

    def mcs_order_status_check_all(self, is_cron):
        log_obj = self.env["mcs.log"]
        picking_obj = self.env['stock.picking']
        mcs_state_options = [k for k, v in picking_obj._columns["mcs_state"].selection]
        client, user, pwd, version = self.get_connection_info()
        pickings = self.get_picking().filtered(lambda x: x.picking_type_id.code != "incoming")
        if not pickings:
            if is_cron:
                _logger.info("No Outgoing Picking Found")
                return
            else:
                return self.get_message_popup("No Outgoing Picking Found for config %s" % self.name)
        orders = self.get_order_xml(pickings)
        response_str = client.service.driebm_soap_functie(user, pwd, "order_status_request", version,
                                                          orders.__str__().decode("UTF-8"))
        response = ET.fromstring(response_str)
        response_orders = response.findall("order")
        updated_pickings = []
        fail_pickings = []
        for response_order in response_orders:
            response_orderid = response_order.find("orderid").text
            try:
                response_status = response_order.find("status").find("line").text
                picking = picking_obj.search([("name", "=", response_orderid)])
                if len(picking) == 1 and response_status != "orderid not found":
                    if response_status not in mcs_state_options:
                        response_status = "unknown"
                    shipment = response_order.find("shipment")
                    shipment_method = shipment.find("shipment_method").text
                    carrier = self.env["delivery.carrier"].search([
                        ("third_party", "=", "mcs"),
                        # ("pricelist_ids.country_ids", "in", picking.partner_id.country_id.id),
                        ("name", "=", shipment_method)])
                    shipment_trackid = shipment.find("shipment_trackid").text
                    mcs_carrier_id = carrier and carrier.id or None
                    odoo_carrier_id = picking.carrier_id and picking.carrier_id.id or None
                    if not self.eq(picking.mcs_state, response_status, str) or not self.eq(picking.carrier_tracking_ref,
                                                                                           shipment_trackid,
                                                                                           str) or odoo_carrier_id != mcs_carrier_id:
                        picking.write({
                            "mcs_state": response_status,
                            "carrier_tracking_ref": shipment_trackid,
                            "carrier_id": mcs_carrier_id,
                        })
                        updated_pickings.append(picking.name)
            except Exception, e:
                log_obj.create({
                    "name": "In 'check_all' for %s" % response_orderid,
                    "desc": e,
                })
                fail_pickings.append(response_orderid)

        if is_cron:
            _logger.info(
                self.get_message(updated_pickings, fail_pickings)
            )
        else:
            return self.get_message_popup(self.get_message(updated_pickings, fail_pickings))

    def mcs_purchase_status_check_all(self, is_cron):
        log_obj = self.env["mcs.log"]
        picking_obj = self.env['stock.picking']
        client, user, pwd, version = self.get_connection_info()
        pickings = self.get_picking().filtered(lambda x: x.picking_type_id.code != "outbound")
        if not pickings:
            if is_cron:
                _logger.info("No Incoming Pickings Found")
                return
            else:
                return self.get_message_popup("No Incoming Pickings Found for config %s" % self.name)
        orders = self.get_purchase_xml(pickings)
        response_str = client.service.driebm_soap_functie(user, pwd, "get_asn", version,
                                                          orders.__str__().decode("UTF-8"))
        response = ET.fromstring(response_str)
        response_orders = response.findall("purchaseorders")[0].findall("purchaseorder")
        updated_pickings = []
        fail_pickings = []
        for response_order in response_orders:
            response_orderid = response_order.find("orderinfo").find("order_number").text
            try:
                response_status = response_order.find("orderinfo").find("status_code").text
                picking = picking_obj.search([("origin", "=", response_orderid), ('state', '=', 'assigned')])
                if len(picking) == 1 and response_status == "000010":
                    if not self.eq(picking.mcs_state, response_status, str):
                        picking.write({
                            "mcs_state": "completed",
                        })
                        updated_pickings.append(picking.name)
            except Exception, e:
                log_obj.create({
                    "name": "In 'check_purchase_status' for %s" % response_orderid,
                    "desc": e,
                })
                fail_pickings.append(response_orderid)

        if is_cron:
            _logger.info(
                self.get_message(updated_pickings, fail_pickings)
            )
        else:
            return self.get_message_popup(self.get_message(updated_pickings, fail_pickings))

    @api.model
    def mcs_cron_order_status_check_all(self):
        log_obj = self.env["mcs.log"]
        for rec in self.search([]):
            try:
                rec.mcs_order_status_check_all(True)
            except Exception, e:
                log_obj.create({
                    "name": "In 'cron_check_all'",
                    "desc": "For config %s:\n%s" % (rec.name, e),
                })

    @api.model
    def mcs_cron_purchase_status_check_all(self):
        log_obj = self.env["mcs.log"]
        for rec in self.search([]):
            try:
                rec.mcs_purchase_status_check_all(True)
            except Exception, e:
                log_obj.create({
                    "name": "In 'cron_check_purchases'",
                    "desc": "For config %s:\n%s" % (rec.name, e),
                })

    @api.multi
    def mcs_button_order_status_check_all(self):
        return self.mcs_order_status_check_all(False)

    @api.multi
    def mcs_button_purchase_status_check_all(self):
        return self.mcs_purchase_status_check_all(False)

    def mcs_validate_serials(self, picking, lines, type):
        product_skus = {}
        # for line in picking.move_lines.filtered(lambda l: l.product_id.track_outgoing):
        for line in picking.move_lines.filtered(lambda l: l.product_id.tracking != 'none'):
            product_skus[line.product_id.barcode] = product_skus.get(line.product_id.barcode, 0) + line.product_uom_qty
        for line in lines:
            if type == "incoming":
                sku = line.find("item_sku").text
            else:
                sku = line.find("sku").text
            if sku not in product_skus:
                continue
            product_skus[sku] -= 1
        return not any(product_skus.values())

    def mcs_transfer_lines(self, picking, lines):
        product_obj = self.env["product.product"]
        lot_obj = self.env["stock.production.lot"]
        stock_pack_obj = self.env["stock.pack.operation"]

        if not picking.pack_operation_ids:
            picking.do_prepare_partial()
        packop_orig = picking.pack_operation_ids[0]

        if picking.picking_type_id.code == "outgoing":
            mcs_only_track_products = {}
            # Loop over lines, lines are retrieved from the MCS response
            for line in lines:
                # search product based on sku
                sku = line.find("sku").text
                product = product_obj.search([("barcode", "=", sku)])
                # if not product.track_outgoing:
                if product.tracking == 'none':
                    mcs_only_track_products.update({
                        product.id: mcs_only_track_products.get(product.id, 0) + 1
                    })
                # lookup or create lot
                number = line.find("number").text
                lots = lot_obj.search([("name", "=", number), ("product_id", "=", product.id)])
                lot = lots[0] if lots else lot_obj.create({
                    "name": number,
                    "product_id": product.id,
                })
                packop_lots = self.env["stock.pack.operation.lot"].search([('lot_id', '=', lot.id)])
                packop_lot = packop_lots[0] if packop_lots else self.env["stock.pack.operation.lot"].create({
                    "lot_id": lot.id,
                })

                packop = picking.pack_operation_product_ids.filtered(lambda l: l.product_id.id == product.id)
                if packop_lot.id not in packop.pack_lot_ids.ids:
                    packop.write({'pack_lot_ids': [(4, packop_lot.id)],
                                  })
                packop.write({'qty_done': packop.qty_done + 1})

            for line in picking.move_lines.filtered(lambda l: l.product_id.tracking == 'none'):
                # remaining_qty = line.product_uom_qty - mcs_only_track_products.get(line.product_id.id, 0)
                remaining_qty = line.product_uom_qty
                if not remaining_qty:
                    continue
                packop = line.picking_id.pack_operation_ids.filtered(
                    lambda x, line=line: x.product_id.id == line.product_id.id)
                if packop:
                    packop.write({'qty_done': packop.qty_done + remaining_qty})
                else:
                    stock_pack_obj.create({'product_id': line.product_id.id,
                                           'product_uom_id': line.product_id.uom_id.id if line.product_id.uom_id else None,
                                           'picking_id': picking.id,
                                           'product_qty': remaining_qty,
                                           'qty_done': remaining_qty,
                                           'location_id': packop_orig.location_id.id,
                                           'location_dest_id': packop_orig.location_dest_id.id})

        else:
            for line in lines:
                sku = line.find("item_sku").text
                product = product_obj.search([("barcode", "=", sku)])
                delivered_qty = line.find("delivered_items").text
                # remaining_qty = line.product_uom_qty - mcs_only_track_products.get(line.product_id.id, 0)
                packop = picking.pack_operation_ids.filtered(lambda x, line=line: x.product_id.id == product.id)
                if packop:
                    packop.write({'qty_done': int(delivered_qty)})
                else:
                    stock_pack_obj.create({'product_id': line.product_id.id,
                                           'product_uom_id': line.product_id.uom_id.id if line.product_id.uom_id else None,
                                           'picking_id': picking.id,
                                           'product_qty': delivered_qty,
                                           'qty_done': delivered_qty,
                                           'location_id': packop_orig.location_id.id,
                                           'location_dest_id': packop_orig.location_dest_id.id})

        return picking.do_transfer()

    def mcs_process_transfer(self, is_cron):
        log_obj = self.env["mcs.log"]
        picking_obj = self.env["stock.picking"]

        client, user, pwd, version = self.get_connection_info()
        pickings = picking_obj.search([
            ("mcs_state", "=", "completed"),
            ("state", "=", "assigned"),
            ("mcs_config_id", "=", self.id),
        ])
        if not pickings:
            if is_cron:
                _logger.info("No Picking Found for config %s" % self.name)
                return
            else:
                return self.get_message_popup("No Picking Found")
        updated_pickings = []
        fail_pickings = []
        # loop over deliveries with mcs state completed. and get info from MCS
        for picking in pickings:
            new_env = self.env
            picking_env = picking.with_env(new_env)

            try:
                lines = False
                type = picking_env.picking_type_id.code
                if type != "incoming":
                    order = self.with_env(new_env).get_order_xml(picking_env)
                    response_str = client.service.driebm_soap_functie(user, pwd, "serie_order", version,
                                                                      order.__str__().decode("UTF-8"))
                    response = ET.fromstring(response_str)
                    serial = response.find("serial")
                    numbers = serial.find("numbers")
                    lines = numbers.findall("line")
                    if not self.with_env(new_env).mcs_validate_serials(picking_env, lines, type):
                        continue
                else:
                    order = self.with_env(new_env).get_purchase_xml(picking_env)
                    response_str = client.service.driebm_soap_functie(user, pwd, "get_asn", version,
                                                                      order.__str__().decode("UTF-8"))
                    response = ET.fromstring(response_str)
                    purchaseorders = response.find("purchaseorders").find("purchaseorder")
                    items = purchaseorders.find("items")
                    lines = items.findall("item")
                # Transfer the delivery
                self.with_env(new_env).mcs_transfer_lines(picking_env, lines)
                updated_pickings.append(picking_env.name)
                picking_env.env.cr.commit()
            except Exception, e:
                log_obj.create({
                    "name": "In 'transfer' for %s" % picking.name,
                    "desc": e,
                })

                fail_pickings.append(picking.name)
                picking.message_post(body=_('Error during transfer: %s') % e)
                picking.write({'mcs_state': 'exception'})
                picking_env.env.cr.rollback()
            finally:
                picking_env.env.cr.close()

        if is_cron:
            _logger.info(
                self.get_message(updated_pickings, fail_pickings)
            )
        else:
            return self.get_message_popup(self.get_message(updated_pickings, fail_pickings))

    @api.model
    def mcs_cron_process_transfer(self):
        log_obj = self.env["mcs.log"]
        for rec in self.search([]):
            try:
                rec.mcs_process_transfer(True)
            except Exception, e:
                log_obj.create({
                    "name": "In 'cron_process_transfer'",
                    "desc": "For config %s:\n%s" % (rec.name, e),
                })

    @api.multi
    def mcs_button_process_transfer(self):
        return self.mcs_process_transfer(False)

    def synchronize_stock(self, cr, uid, product_id, old_qty, new_qty, context):
        old_qty = 0.0 if old_qty is None else float(old_qty)
        new_qty = 0.0 if new_qty is None else float(new_qty)
        if old_qty == 0 and new_qty < 0:
            cr.close()
            return False
        elif new_qty < 0:
            new_qty = 0
        wizard = self.pool.get('stock.change.product.qty').create(cr, uid, {
            'product_id': product_id,
            'new_quantity': new_qty,
        }, context=context)
        self.pool.get('stock.change.product.qty').change_product_qty(cr, uid, [wizard], context)
        cr.commit()
        cr.close()


    @api.model
    def mcs_cron_stock_request(self):
        log_obj = self.env["mcs.log"]
        for rec in self.search([]):
            try:
                rec.mcs_button_stock_request()
            except Exception, e:
                log_obj.create({
                    "name": "In 'mcs_cron_stock_request'",
                    "desc": "For config %s:\n%s" % (rec.name, e),
                })

    @api.multi
    def mcs_button_hello_world(self):
        try:
            client, user, pwd, version = self.get_connection_info()
            message = "Hello World Test with MCS was a Success\n%s" % client.service.HelloWorld()

            product = self.env["product.product"].search([("type", "=", "product")], limit=1)
            stock = self.get_stock_xml(product)
            response_str = client.service.stock_request(user, pwd, version, stock.__str__().decode("UTF-8"))
            response = ET.fromstring(response_str)
            message += "\n\nERROR:\n%s" % response.text if response.tag == "ERROR" else "\n\nLogin Sucess !"
        except Exception, e:
            message = "Hello World Test with MCS has Failed\n%s" % e
        return self.get_message_popup(message)
