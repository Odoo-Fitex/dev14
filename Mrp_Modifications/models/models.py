# -*- coding: utf-8 -*-
from odoo import models, fields, api 
 

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Kit')], 'BoM Type',
        default='normal', required=True, store=True)
    ratio = fields.Float(string="L.R", default=1.0, required=True, store=True)
    grey_weight = fields.Char(string="Grey Weight", store=True)
    grey_product_tmpl_id = fields.Many2one(
        'product.template', 'Greige Product', store=True,
        domain="[('type', 'in', ['product', 'consu'])]")
    barcode = fields.Char(string='Barcode',
                          store=True,
                          related='grey_product_tmpl_id.barcode')
    
    material_type = fields.Selection([
        ('dyed', 'Color'),
        ('chemicals', 'Auxiliary'), 
        ('finishing', 'Finishing'),
        ('grey fabric', 'Greige Fabric'),
        ('dyed fabric', 'Dyed Fabric')], 'Type', store=True, required=True)
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Unit of Measure', store=True, required=True)
    @api.onchange('material_type')
    def _onchange_material_type_change_bom_type(self):
        if self.material_type == 'dyed':
            self.type = 'phantom'
        elif self.material_type == 'chemicals':
            self.type = 'phantom'
        elif self.material_type == 'finishing':
            self.type = 'phantom'
        elif self.material_type == 'grey fabric':
            self.type = 'normal'
        elif self.material_type == 'dyed fabric':
            self.type = 'normal'
#      @api.onchange('bom_line_ids')
    def material_type_change_bom_percentage(self):
            if self.material_type == 'dyed':
                if self.bom_line_ids:	
                    for line in self.bom_line_ids:
                        line.product_qty = self.product_qty * line.percentage / 100
            elif self.material_type == 'chemicals':
                if self.bom_line_ids:	
                    for line in self.bom_line_ids:
                        line.product_qty = self.product_qty * self.ratio * line.percentage / 100
class MrpBomLinesAddedFields(models.Model):
    _inherit = 'mrp.bom.line'

    percentage = fields.Float(string="Percentage", store=True)
#     product_qty = fields.Float(
#         'Quantity', default=1.0,
#         digits='Product Unit of Measure', required=True, readonly="False") #, compute='_onchange_material_type_change_bom_percentage'
#     def material_type_change_bom_percentage(self):
#             if self.bom_id.material_type == 'dyed':
#                  if self.product_id:   
#                      self.product_qty = self.bom_id.product_qty * self.percentage / 100
#                  else:
#                      self.product_qty = 1
