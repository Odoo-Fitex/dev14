# -*- coding: utf-8 -*-

from odoo import models, fields, api






class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_readonly = fields.Boolean(string="Is Readonly",default=True)

    @api.onchange('picking_type_id')
    def make_is_readonly_false(self):
        for rec in self:
            if rec.picking_type_id.code=='outgoing' :
                rec.is_readonly=True
            else:
                rec.is_readonly = False





