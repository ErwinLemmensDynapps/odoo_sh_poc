# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    xx_enable_akeneo_interface = fields.Boolean("Enable Akeneo Interface"),
    xx_akeneo_base_url = fields.char("Akeneo base url"),
    xx_akeneo_user = fields.char("Akeneo User"),
    xx_akeneo_password = fields.char("Akeneo Password"),
    xx_akeneo_client_id = fields.char("Akeneo Client Id"),
    xx_akeneo_secret = fields.char("Akeneo Secret"),
    xx_akeneo_family = fields.char("Akeneo Family"),

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            xx_enable_akeneo_interface=ICPSudo.get_param('xx_akeneo.xx_enable_akeneo_interface', default=False),
            xx_akeneo_base_url=ICPSudo.get_param('xx_akeneo.xx_akeneo_base_url', default=False),
            xx_akeneo_user=ICPSudo.get_param('xx_akeneo.xx_akeneo_user', default=False),
            xx_akeneo_password=ICPSudo.get_param('xx_akeneo.xx_akeneo_password', default=False),
            xx_akeneo_client_id=ICPSudo.get_param('xx_akeneo.xx_akeneo_client_id', default=False),
            xx_akeneo_secret=ICPSudo.get_param('xx_akeneo.xx_akeneo_secret', default=False),
            xx_akeneo_family=ICPSudo.get_param('xx_akeneo.xx_akeneo_family', default=False),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("xx_akeneo.xx_enable_akeneo_interface", self.xx_enable_akeneo_interface)
        ICPSudo.set_param("xx_akeneo.xx_akeneo_base_url", self.xx_akeneo_base_url)
        ICPSudo.set_param("xx_akeneo.xx_akeneo_user", self.xx_akeneo_user)
        ICPSudo.set_param("xx_akeneo.xx_akeneo_password", self.xx_akeneo_password)
        ICPSudo.set_param("xx_akeneo.xx_akeneo_client_id", self.xx_akeneo_client_id)
        ICPSudo.set_param("xx_akeneo.xx_akeneo_secret", self.xx_akeneo_secret)
        ICPSudo.set_param("xx_akeneo.xx_akeneo_family", self.xx_akeneo_family)
