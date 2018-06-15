# coding: utf-8
# Copyright (C) 2017 DynApps <http://www.dynapps.be>
# @author Pieter Paulussen <pieter.paulussen@dynapps.be>
# @author Stefan Rijnhart <stefan.rijnhart@dynapps.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import Warning as UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def write(self, values):
        res = super(ResPartner, self).write(values)

        if values.get('name') == 'test':
            raise UserError("Error raised")
        return res
