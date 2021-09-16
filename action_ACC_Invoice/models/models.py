# -*- coding: utf-8 -*-
from odoo import models, fields, api


class action_SO_line(models.Model):
    _inherit = 'account.move.line'

    trade_name = fields.Char(string='The Trade Name',
                         store=True,
                         related='product_id.name')

    barcode = fields.Char(string='Barcode',
                          store=True,
                          related='product_id.barcode')
    
    
class action_auditing(models.Model):
    _inherit = 'account.move'

    audited = fields.Boolean(string="Audited", store=True)
