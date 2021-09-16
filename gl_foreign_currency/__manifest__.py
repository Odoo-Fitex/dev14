# -*- coding: utf-8 -*-
{
    'name': "SW - General Ledger in Foreign Currency",
    'summary': "Generate your Trial Balance report with your preferred currencies",
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Accounting',
    'license':  "Other proprietary",
    'version': '13.0.1.0',
    'depends': ['base','account','account_reports'],
    'installable': True,
    'auto_install': False,
    'data': [
        'view/general_ledger.xml',
        'view/data.xml',
    ],
    'images':  ["static/description/image.png"],
    'price' : 50,
    'currency' :  'EUR',
    'post_init_hook': 'post_init_hook',
}
