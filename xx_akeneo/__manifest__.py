# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 DynApps NV (<http://www.dynapps.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Akeneo Product Interface",
    "version": "1.0",
    "author": "DynApps",
    "website": 'http://www.dynapps.be',
    "category": "Products",
    "description": """
        Akeneo Product Interface
    """,
    "depends": [
        'base',
        'product',
    ],
    "data": [
        'views/res_config_view.xml',
        'views/product_view.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "active": False,
}
