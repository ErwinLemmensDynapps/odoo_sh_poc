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
        # if not self.env['ir.config_parameter'].sudo().get_param('sale.xx_enable_akeneo_interface'):
        #     return
        base_url = 'https://demo.akeneo.com'
        url = base_url + '/api/oauth/v1/token'
        username = 'admin'
        password = 'admin'
        client_id = '1_54bjrt3co84kg08w4kc8ggsck4cwwk8o4k4woowgw8c48ssc0g'
        secret = '113w260sc64g0k4c4wk4sk84swk08wwowc0w4kk4ocogwcgwsg'
        family = 'created_by_odoo'

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
          "values": {
            "name": [
              {
                "data": "%s",
                "locale": null,
                "scope": null
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

