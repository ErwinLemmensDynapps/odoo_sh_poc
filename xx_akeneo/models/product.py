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
        base_url = 'http://demo.akeneo.com'
        url = base_url + '/api/oauth/v1/token'
        username = 'admin'
        password = 'admin'
        client_id = '1_1p8vk60u2h40ggc0kwgckc8ks88s8o0s4sowgkw48wogg0ss0o'
        secret = '3eosuc0kyv8ksoos00gc0gwo4k48wcgwo8c8484o88w084wswc'
        family = 'Accessories'

        authorization = 'Basic %s' % base64.b64encode((client_id + ':' + secret).encode('UTF-8'))
        headers = {'Content-Type': 'application/json',
                   'Authorization': authorization}
        data = '''{ "grant_type": "password", "username": "%s", "password": "%s"}''' % (username, password)
        response = requests.post(url, data=data, headers=headers)
        access_token = 'YTI0NDcwNjQ5OWE5NGY4NDlhNzdkNTg5MmEyYzBjZjE1MDg0ZGNkNGZlOWRkMjEwYjFjNzY0ODkyYmNhYmUxNw'
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

