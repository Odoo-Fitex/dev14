# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import float_compare


class StockScrap(models.Model):
    _inherit = 'stock.scrap'


    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        domain="[('usage', 'in', ['internal', 'transit']), ('company_id', 'in', [company_id, False])]",
        required=True, store=True, states={'done': [('readonly', True)]}, check_company=True)
