# coding: utf-8
# Copyright (C) 2017 DynApps <http://www.dynapps.be>
# @author Pieter Paulussen <pieter.paulussen@dynapps.be>
# @author Stefan Rijnhart <stefan.rijnhart@dynapps.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase
from odoo.exceptions import Warning as UserError


class TestCreatePartner(SavepointCase):

    post_install = True
    at_install = False

    def change_name(self, partner):
        partner.write({'name': "Test"})

    @classmethod
    def setUpClass(cls):
        super(TestCreatePartner, cls).setUpClass()
        cls.test_partner_1 = cls.env['res.partner'].create(
            {'name': "Pieter Paulussen"})
        cls.user_1 = cls.env['res.users'].create({'login': 'p.paulussen',
                                     'partner_id': cls.test_partner_1.id})
        cls.user_env = cls.env(user=cls.user_1)


    def test_01_partner_name(self):
        partner = self.env['res.partner'].search([('name', '=', 'Pieter Paulussen')])
        self.assertEqual(partner, self.test_partner_1)
        self.assertFalse(partner.supplier)

    def test_02_partner_name_change(self):
        partner = self.env['res.partner'].search(
            [('name', '=', 'Pieter Paulussen')])
        self.change_name(partner)
        self.assertEqual('Test', partner.name)

    def test_03_assert_user(self):
        """ this is test 3"""
        self.assertEqual(self.env.user.login, 'p.pauussen', "test case has failed")

    def test_04_assert_error(self):
        with self.assertRaises(UserError):
            self.test_partner_1.name = 'test'
