# coding=utf-8
from odoo import models, fields, api, _
from suds.client import Client
from suds.sax.element import Element
import xml.etree.ElementTree as ET
from odoo.exceptions import ValidationError as VE

import logging

_logger = logging.getLogger(__name__)


class popup(models.TransientModel):
    _name = "gdf.popup"

    name = fields.Char("Title", readonly=True)
    desc = fields.Text("Description", readonly=True)


class mcs_config(models.Model):
    _name = 'mcs.config'

    name = fields.Char("Name")
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

    @api.multi
    def mcs_button_hello_world(self):
        try:
            client, user, pwd, version = self.get_connection_info()
            message = "Hello World Test with MCS was a Success\n%s" % client.service.HelloWorld()

            product = self.env["product.product"].search([("type", "=", "product")], limit=1)
            stock = self.get_stock_xml(product)
            response_str = client.service.stock_request(user, pwd, version, stock.__str__())
            response = ET.fromstring(response_str)
            message += "\n\nERROR:\n%s" % response.text if response.tag == "ERROR" else "\n\nLogin Sucess !"
        except Exception as e:
            message = "Hello World Test with MCS has Failed: %s \n %s" % (e, stock.__str__)
        return self.get_message_popup(message)    \

    @api.multi
    def mcs_send_order(self):
        try:
            client, user, pwd, version = self.get_connection_info()
            msg= '<orders>\n   <order>\n      <orderid>TEST\\ODOO.sh</orderid>\n      <shop>50FIVE</shop>\n      <customerid>15167</customerid>\n      <email>lcretaz@hotmail.fr</email>\n      <phone></phone>\n      <ordernote></ordernote>\n      <language>fr_BE</language>\n      <shipping>\n         <shipping_method>TAX02</shipping_method>\n         <shipping_last_name>Cretaz Laurence</shipping_last_name>\n         <shipping_address>rue des Porettes  12 </shipping_address>\n         <shipping_postal>77210</shipping_postal>\n         <shipping_city>SAMOREAU</shipping_city>\n         <shipping_country>False</shipping_country>\n      </shipping>\n      <invoice>\n         <show_price>N</show_price>\n      </invoice>\n      <items>\n         <item>\n            <ProductName>Wireless Blood Pressure Monitor</ProductName>\n            <ProductCode>3700546700279</ProductCode>\n            <quantity>1</quantity>\n            <item_units>1</item_units>\n            <item_weight>0.0</item_weight>\n         </item>\n      </items>\n   </order>\n</orders>'
            response_str = client.service.stock_request(user, pwd, version, msg)
            response = ET.fromstring(response_str)
            message = "Send order to MCS\n%s"
            message += "\n\nERROR:\n%s" % response.text if response.tag == "ERROR" else "\n\nLogin Sucess !"
        except Exception as e:
            message = "Hello World Test with MCS has Failed: %s \n %s" % (e, stock.__str__)
        return self.get_message_popup(message)
