# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv


class crm_configuration(osv.TransientModel):
    _name = 'sale.config.settings'
    _inherit = 'sale.config.settings'

    _columns = {
        'xx_enable_akeneo_interface': fields.boolean("Enable Akeneo Interface"),
        'xx_akeneo_base_url': fields.char("Akeneo base url"),
        'xx_akeneo_user': fields.char("Akeneo User"),
        'xx_akeneo_password': fields.char("Akeneo Password"),
        'xx_akeneo_client_id': fields.char("Akeneo Client Id"),
        'xx_akeneo_secret': fields.char("Akeneo Secret"),
        'xx_akeneo_family': fields.char("Akeneo Family"),
    }

    def set_default_xx_enable_akeneo_interface(self, cr, uid, ids, context=None):
        xx_enable_akeneo_interface = self.browse(cr, uid, ids, context=context).xx_enable_akeneo_interface
        res = self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'sale.config.settings',
                                                     'xx_enable_akeneo_interface', xx_enable_akeneo_interface)
        return res

    def get_default_xx_enable_akeneo_interface(self, cr, uid, ids, context=None):
        return {
            'xx_enable_akeneo_interface': self.pool['ir.values'].get_default(cr, SUPERUSER_ID, 'sale.config.settings',
                                                                             'xx_enable_akeneo_interface')}

    def set_default_xx_akeneo_base_url(self, cr, uid, ids, context=None):
        xx_akeneo_base_url = self.browse(cr, uid, ids, context=context).xx_akeneo_base_url
        res = self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'sale.config.settings',
                                                     'xx_akeneo_base_url', xx_akeneo_base_url)
        return res

    def get_default_xx_akeneo_base_url(self, cr, uid, ids, context=None):
        return {
            'xx_akeneo_base_url': self.pool['ir.values'].get_default(cr, SUPERUSER_ID, 'sale.config.settings',
                                                                             'xx_akeneo_base_url')}

    def set_default_xx_akeneo_user(self, cr, uid, ids, context=None):
        xx_akeneo_user = self.browse(cr, uid, ids, context=context).xx_akeneo_user
        res = self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_user',
                                                     xx_akeneo_user)
        return res

    def get_default_xx_akeneo_user(self, cr, uid, ids, context=None):
        return {'xx_akeneo_user': self.pool['ir.values'].get_default(cr, SUPERUSER_ID, 'sale.config.settings',
                                                                     'xx_akeneo_user')}

    def set_default_xx_akeneo_password(self, cr, uid, ids, context=None):
        xx_akeneo_password = self.browse(cr, uid, ids, context=context).xx_akeneo_password
        res = self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_password',
                                                     xx_akeneo_password)
        return res

    def get_default_xx_akeneo_password(self, cr, uid, ids, context=None):
        return {'xx_akeneo_password': self.pool['ir.values'].get_default(cr, SUPERUSER_ID, 'sale.config.settings',
                                                                         'xx_akeneo_password')}

    def set_default_xx_akeneo_client_id(self, cr, uid, ids, context=None):
        xx_akeneo_client_id = self.browse(cr, uid, ids, context=context).xx_akeneo_client_id
        res = self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_client_id',
                                                     xx_akeneo_client_id)
        return res

    def get_default_xx_akeneo_client_id(self, cr, uid, ids, context=None):
        return {'xx_akeneo_client_id': self.pool['ir.values'].get_default(cr, SUPERUSER_ID, 'sale.config.settings',
                                                                          'xx_akeneo_client_id')}

    def set_default_xx_akeneo_secret(self, cr, uid, ids, context=None):
        xx_akeneo_secret = self.browse(cr, uid, ids, context=context).xx_akeneo_secret
        res = self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_secret',
                                                     xx_akeneo_secret)
        return res

    def get_default_xx_akeneo_secret(self, cr, uid, ids, context=None):
        return {'xx_akeneo_secret': self.pool['ir.values'].get_default(cr, SUPERUSER_ID, 'sale.config.settings',
                                                                       'xx_akeneo_secret')}

    def set_default_xx_akeneo_family(self, cr, uid, ids, context=None):
        xx_akeneo_family = self.browse(cr, uid, ids, context=context).xx_akeneo_family
        res = self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'sale.config.settings', 'xx_akeneo_family',
                                                     xx_akeneo_family)
        return res

    def get_default_xx_akeneo_family(self, cr, uid, ids, context=None):
        return {'xx_akeneo_family': self.pool['ir.values'].get_default(cr, SUPERUSER_ID, 'sale.config.settings',
                                                                       'xx_akeneo_family')}
