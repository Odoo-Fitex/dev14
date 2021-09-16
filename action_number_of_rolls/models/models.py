# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class NumberOfRolls(models.Model):
    _inherit = 'stock.quant'
  
    number_of_rolls = fields.Float(string='Number Of Rolls', readonly=False, help="original number of rolls")

    
class LotNumberOfRolls(models.Model):
    _inherit = 'stock.production.lot'
    
    lot_number_of_rolls = fields.Float('Number', compute='product_number_of_rolls')
    def product_number_of_rolls(self):
        for lot in self:
            # We only care for the rollss in internal or transit locations.
            rolls = lot.quant_ids.filtered(lambda q: q.location_id.usage in ['internal', 'transit'])
            lot.lot_number_of_rolls = sum(rolls.mapped('number_of_rolls'))
            
            
class NumberOfRollsAddAndSubtract(models.Model):
   _inherit = 'stock.move.line'

   number_of_rolls_in_line = fields.Float(string="العدد") 
    
class Picking(models.Model):
   _inherit = 'stock.picking'
   
   new_number_of_rolls_src = fields.Float(compute='button_validate')
   new_number_of_rolls_dest = fields.Float(compute='button_validate')
   related_operation_type = fields.Selection(string="Picking Type", related='picking_type_id.code')
   total_rolls = fields.Float(string="Total Count Of Rolls", default=0,compute="amount_all_rolls")
   total_quantity = fields.Float(string="Total Quantity", default=0, compute="amount_all_rolls") 

   @api.onchange('move_line_ids')
   def amount_all_rolls(self):
     for stock in self:
      if stock.move_line_ids:
       total_rolls =0.0
       total_quantity = 0.0
       for line in stock.move_line_ids:
        if line.number_of_rolls_in_line or line.qty_done:
           total_rolls += line.number_of_rolls_in_line
           total_quantity += line.qty_done
           stock.update({
           'total_rolls': total_rolls,
           'total_quantity': total_quantity,
                    })
        else:
            stock.total_rolls = 0.0
            stock.total_quantity = 0.0
      else:
           stock.total_rolls = 0.0
           stock.total_quantity = 0.0
            
   def button_validate(self):
        res = super(Picking, self).button_validate()
        if self.related_operation_type == 'incoming':
            for roll in self.move_line_nosuggest_ids:
                roll_count_in_src_location = self.env['stock.quant'].search([('product_id', '=', roll.product_id.id),
                                                                              ('lot_id', '=', roll.lot_id.id),
                                                                              ('location_id', '=', roll.location_id.id)])
                
                roll_count_in_dest_location = self.env['stock.quant'].search([('product_id', '=', roll.product_id.id),
                                                                              ('lot_id', '=', roll.lot_id.id),
                                                                              ('location_id', '=', roll.location_dest_id.id)])
                
                self.new_number_of_rolls_src = roll_count_in_src_location.number_of_rolls - roll.number_of_rolls_in_line
                self.new_number_of_rolls_dest = roll_count_in_dest_location.number_of_rolls + roll.number_of_rolls_in_line
                roll_count_in_src_location.write({'number_of_rolls': self.new_number_of_rolls_src})
                roll_count_in_dest_location.write({'number_of_rolls': self.new_number_of_rolls_dest})
            return res
        elif self.related_operation_type in ['outgoing', 'internal']:
            for roll in self.move_line_ids_without_package:
                roll_count_in_src_location = self.env['stock.quant'].search([('product_id', '=', roll.product_id.id),
                                                                              ('lot_id', '=', roll.lot_id.id),
                                                                              ('location_id', '=', roll.location_id.id)])
                
                roll_count_in_dest_location = self.env['stock.quant'].search([('product_id', '=', roll.product_id.id),
                                                                              ('lot_id', '=', roll.lot_id.id),
                                                                              ('location_id', '=', roll.location_dest_id.id)])
                
                self.new_number_of_rolls_src = roll_count_in_src_location.number_of_rolls - roll.number_of_rolls_in_line
                self.new_number_of_rolls_dest = roll_count_in_dest_location.number_of_rolls + roll.number_of_rolls_in_line
                roll_count_in_src_location.write({'number_of_rolls': self.new_number_of_rolls_src})
                roll_count_in_dest_location.write({'number_of_rolls': self.new_number_of_rolls_dest})
            return res
        
class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production'
    
#     production_destiation_location = fields.Many2one(string="Destination Location",
#                                                       readonly=True,
#                                                       related='production_id.location_dest_id')
    rolls_post_visiblity = fields.Boolean(string="Rolls Posted",default=False)
    number_of_rolls =  fields.Float(string="Number Of Rolls")
    new_number_of_rolls_dest = fields.Float(compute='do_roll_finish')
    
    def do_roll_finish(self):
        for roll in self:
            roll_count_in_dest_location = self.env['stock.quant'].search([('product_id', '=', roll.product_id.id),
                                                                          ('lot_id', '=', roll.lot_producing_id.id),
                                                                          ('location_id', '=', roll.location_dest_id.id)])
            if roll_count_in_dest_location.number_of_rolls:
                self.new_number_of_rolls_dest = roll_count_in_dest_location.number_of_rolls + roll.number_of_rolls
                roll_count_in_dest_location.write({'number_of_rolls': roll.new_number_of_rolls_dest})
                roll.rolls_post_visiblity=True
            else:
                quant = self.env['stock.quant'].create({'product_id':roll.product_id.id,
                                                        'location_id':roll.location_dest_id.id,
                                                        'lot_id':roll.lot_producing_id.id
                                                        })
                quant.number_of_rolls = roll.number_of_rolls
                quant.write({'number_of_rolls': roll.number_of_rolls})
                roll.rolls_post_visiblity=True
            
class NumberOfRollsInventoryAdjustment(models.Model):
    _inherit = 'stock.inventory.line'
    number_of_rolls =  fields.Float(string="Number Of Rolls")
    def button_validate(self):
        res = super(Picking, self).button_validate()
