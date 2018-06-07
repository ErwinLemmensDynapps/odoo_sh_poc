{
    'name': 'MCS Integration',
    'category': 'Website',
    'summary': 'MCS Integration',
    'website': 'https://www.odoo.com',
    'version': '1.0',
    'description': """MCS Integration""",
    'author': 'OpenERP SA',
    'depends': [
        'delivery',
        'gdf_multiwebsite',
        'product'
    ],
    'installable': True,
    'data': [
        'views/backend/mcs_config.xml',
    ],
    'demo' : [
    ],
    'application': False,

}

