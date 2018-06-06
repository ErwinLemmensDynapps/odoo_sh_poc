import logging
import requests
import json
import base64
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    xx_sent_to_akeneo = fields.Boolean(string='Sent to Akeneo')


    @api.model
    def send_to_akeneo(self):
        # get Authorization token
        if not self.pool['ir.values'].get_default(self._cr, SUPERUSER_ID, 'sale.config.settings', 'xx_enable_akeneo_interface'):
            return
        base_url = self.pool['ir.values'].get_default(self._cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_base_url')
        url = base_url + '/api/oauth/v1/token'
        username = self.pool['ir.values'].get_default(self._cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_user')
        password = self.pool['ir.values'].get_default(self._cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_password')
        client_id = self.pool['ir.values'].get_default(self._cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_client_id')
        secret = self.pool['ir.values'].get_default(self._cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_secret')
        family = self.pool['ir.values'].get_default(self._cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_family')
        authorization = 'Basic %s' % base64.b64encode(client_id+':'+secret)
        headers = {'Content-Type': 'application/json',
                   'Authorization': authorization}
        data = '''{ "grant_type": "password", "username": "%s", "password": "%s"}''' % (username, password)
        response = requests.post(url, data=data, headers=headers)
        access_token = json.loads(response._content)['access_token']
        authorization = 'Bearer %s' % access_token
        # create product
        url = base_url + '/api/rest/v1/products'
        data = '''{
          "identifier": "%s",
          "enabled": true,
          "family": "%s",
          "groups": [],
          "variant_group": null,
          "values": {
            "name": [
              {
                "data": "%s",
                "locale": "en_GB",
                "scope": "50five"
              }]
          }
        }''' % (self.barcode, family, self.name)
        headers = {'Content-Type': 'application/json', 'Authorization': authorization}
        response = requests.post(url, data=data, headers=headers)
        # if not ok or already exists
        if not response.status_code in [201,422]:
            raise ValidationError(response.text)
        else:
            self.xx_sent_to_akeneo = True

    @api.model
    def create(self, vals):
        product_id = super(ProductProduct, self).create(vals)
        if product_id and product_id.barcode:
            product_id.send_to_akeneo()
        return product_id

    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if vals and 'barcode' in vals:
            self.send_to_akeneo()
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    xx_sent_to_akeneo = fields.Boolean(string='Sent to Akeneo', related='product_variant_ids.xx_sent_to_akeneo')

