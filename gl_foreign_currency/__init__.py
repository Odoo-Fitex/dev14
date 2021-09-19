# -*- coding: utf-8 -*-
from . import models

def post_init_hook(cr, registry):
    from odoo.exceptions import Warning
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    if env.ref('base.module_tb_foreign_currency',False) and env.ref('base.module_tb_foreign_currency').state == 'installed':
            if env.ref('gl_foreign_currency.search_template_analytic'):
                env.ref('gl_foreign_currency.search_template_analytic').active = False
