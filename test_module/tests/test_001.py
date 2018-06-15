# coding: utf-8
# Copyright (C) 2017 DynApps <http://www.dynapps.be>
# @author Pieter Paulussen <pieter.paulussen@dynapps.be>
# @author Stefan Rijnhart <stefan.rijnhart@dynapps.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestCreatePartner(SavepointCase):

    def change_name(self, partner):
        partner.write({'name': "Test"})

    @classmethod
    def setUpClass(cls):
        super(TestCreatePartner, cls).setUpClass()
        cls.test_partner_1 = cls.env['res.parter'].create(
            {'name': "Pieter Paulussen"})

    def test_01_partner_name(self):
        partner = self.env['res.partner'].search([('name', '=', 'Pieter Paulussen')])
        self.assertEqual(partner, self.test_partner_1)
