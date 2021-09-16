# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero


class PartialProductionQty(models.TransientModel):
    _name  = 'partial.production.qty'
    _description = 'Partial Production Qty'


    @api.onchange('partial_qty')
    def _new_product_uom_qty(self):
        active_id = self.env['mrp.production'].browse(self.env.context.get('active_ids'))
        if self.partial_qty >0:
            values = []
            values_2 = []
            product_list = []
            final_values = []
            for product in self.component_vals_ids:
                for rec in active_id.move_raw_ids:
                    if product.product_id == rec.product_id:
                        new_value = rec.product_uom_qty//active_id.product_qty
                        if rec.product_id.tracking != 'serial':
                            product.product_uom_qty = new_value*self.partial_qty
                            values_2.append(product.id)

                if product.product_id.tracking == 'serial':
                    #values.append((2,product.id,0))
                    values.append(product) 

            for active in active_id.move_raw_ids:
                if active.product_id.tracking == 'serial':
                    product_list.append(active.product_id)       

                        
            for pro in range(len(product_list)):
                count=0
                for value in range(len(values)):
                    if values[value].product_id == product_list[pro]:
                        final_values.append(values[value].id)
                        count+=1
                        if count == self.partial_qty:
                            break

            final_values.extend(values_2)
            self.component_vals_ids = [(6,0,final_values)] 

                    

    @api.model
    def default_get(self, fields):
        res = super(PartialProductionQty, self).default_get(fields)
        val_list = []
        production = self.env['mrp.production']
        production_id = self.env.context.get('default_production_id') or self.env.context.get('active_id')
        if production_id:
            production = self.env['mrp.production'].browse(production_id)
        if production.exists():
            serial_finished = (production.product_id.tracking == 'serial')
            todo_uom = production.product_uom_id.id
            if serial_finished:
                if production.product_uom_id.uom_type != 'reference':
                    todo_uom = self.env['uom.uom'].search([('category_id', '=', production.product_uom_id.category_id.id), ('uom_type', '=', 'reference')]).id
            if 'production_id' in fields:
                res['production_id'] = production.id
            if 'product_uom_id' in fields:
                res['product_uom_id'] = todo_uom
            if 'product_id' in fields:
                res['product_id'] = production.product_id.id
            if 'company_id' in fields:
                res['company_id'] = production.company_id.id
            if 'product_tracking' in fields:
                res['product_tracking'] = production.product_id.tracking

        active_id = self.env['mrp.production'].browse(self.env.context.get('active_ids'))
        length = len(active_id.move_raw_ids)

        for rec in range(length):
            if active_id.move_raw_ids[rec].product_id.tracking == 'serial':
                for record in range(int(active_id.move_raw_ids[rec].product_uom_qty)):

                    if active_id.move_raw_ids[rec].state not in ['done','cancel'] :
    
                        val_list.append((0,0,{
                    
                                'product_id': active_id.move_raw_ids[rec].product_id.id,
                                'product_uom_qty':1,
                                'reserved_availability':active_id.move_raw_ids[rec].reserved_availability,
                                'quantity_done':active_id.move_raw_ids[rec].quantity_done,
                                'product_uom_id':active_id.move_raw_ids[rec].product_uom.id,

                                }))
            else:        
                if active_id.move_raw_ids[rec].state not in ['done','cancel'] :
                    val_list.append((0,0,{
                        'product_id': active_id.move_raw_ids[rec].product_id.id,
                        'product_uom_qty':active_id.move_raw_ids[rec].product_uom_qty,
                        'reserved_availability':active_id.move_raw_ids[rec].reserved_availability,
                        'quantity_done':active_id.move_raw_ids[rec].quantity_done,
                        'product_uom_id':active_id.move_raw_ids[rec].product_uom.id,
                    }))

        res['component_vals_ids']= val_list          
        return res

    rolls = fields.Integer(string="Number Of Rolls")
    partial_qty = fields.Float('Quantity to Be Produced', required=True)
    product_tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Tracking", help="Ensure the traceability of a storable product in your warehouse.", default='none')
    production_id = fields.Many2one('mrp.production', 'Manufacturing Order')
    product_id = fields.Many2one(related='production_id.product_id', readonly=True, store=True, check_company=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    finished_lot_id = fields.Many2one(
        'stock.production.lot', string='Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)
    company_id = fields.Many2one('res.company','Company')

    component_vals_ids = fields.One2many('partial.production.qty.line','component_line_id')


    def do_partial_produce(self):
        
        current_number_of_rolls = self.finished_lot_id.roll_number
        new_number_of_rolls = current_number_of_rolls + self.rolls
        self.finished_lot_id.write({'roll_number': new_number_of_rolls}) 
        if self._context.get('active_id') and self._context.get('active_model')== 'mrp.production':
            production  =  self.env['mrp.production'].browse(self._context.get('active_id'))
            partial_production_qty = production.product_qty - production.partial_qty
            if self.partial_qty > partial_production_qty: 
                raise UserError(_("You have enter quantity higher than planned quantity %d ")%(partial_production_qty))
            else:
                production.partial_qty = self.partial_qty
                
                if production.routing_id:
                    orders_to_plan = production.filtered(lambda order: order.routing_id and order.state in ['confirmed','progress'])
                    for order in orders_to_plan:
                        order.move_raw_ids.filtered(lambda m: m.state == 'draft')._action_confirm()
                        quantity = order.product_uom_id._compute_quantity(order.product_qty, order.bom_id.product_uom_id) / order.bom_id.product_qty
                        boms, lines = order.bom_id.explode(order.product_id, quantity, picking_type=order.bom_id.picking_type_id)
                        if self.product_id.tracking == 'serial' and self.partial_qty > 1:
                            raise ValidationError(_("The number of Serial Numbers must be one."))
                        order.with_context({'finished_lot_id': self.finished_lot_id.id,'raw_workorder_line_ids':self.component_vals_ids})._generate_workorders(boms)
                        order._plan_workorders()
                        
                else:
                    production.partial_qty = self.partial_qty
                    quantity = self.partial_qty
                    if self.product_id.tracking == 'serial' and self.partial_qty > 1:
                        raise ValidationError(_("The number of Serial Numbers must be one."))
                    if float_compare(quantity, 0, precision_rounding=production.product_uom_id.rounding) <= 0:
                        raise UserError(_("The production order for '%s' has no quantity specified") % self.product_id.display_name)
                    for move in production.move_raw_ids.filtered(lambda x: x.state == 'assigned'):
                        # TODO currently not possible to guess if the user updated quantity by hand or automatically by the produce wizard.
                        if move.product_id.tracking == 'none' and move.state not in ('done', 'cancel') and move.unit_factor:
                            rounding = move.product_uom.rounding
                            move.quantity_done = float_round(quantity * move.unit_factor, precision_rounding=rounding)
                    for move in production.move_finished_ids:
                        if move.product_id.tracking == 'none' and move.state not in ('done', 'cancel'):
                            rounding = move.product_uom.rounding
                            if move.product_id.id == production.product_id.id:
                                move.quantity_done = float_round(quantity, precision_rounding=rounding)
                                
                            elif move.unit_factor:
                                # byproducts handling
                                move.quantity_done = float_round(quantity * move.unit_factor, precision_rounding=rounding)
                    produce_move = production.move_finished_ids.filtered(lambda x: x.product_id == production.product_id and x.state not in ('done', 'cancel'))
                    if produce_move and produce_move.product_id.tracking != 'none':
                        if not self.finished_lot_id:
                            raise UserError(_('You need to provide a lot for the finished product'))
                    existing_move_line = produce_move.move_line_ids.filtered(lambda x: x.lot_id == self.finished_lot_id)
                    if existing_move_line:
                        existing_move_line.product_uom_qty = production.partial_qty + existing_move_line.product_uom_qty
                        existing_move_line.qty_done = production.partial_qty + existing_move_line.qty_done 
                    else:
                        vals = {
                              'move_id': produce_move.id,
                              'product_id': produce_move.product_id.id,
                              'production_id': production.id,
                              'product_uom_qty': quantity,
                              'product_uom_id': production.product_uom_id.id,
                              'qty_done': quantity,
                              'lot_id': self.finished_lot_id.id,
                              'location_id': produce_move.location_id.id,
                              'location_dest_id': produce_move.location_dest_id.id,
                              'company_id': production.company_id.id,
                            }     
                        self.env['stock.move.line'].create(vals)
                    for move in production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')):
                        if move.needs_lots and not production.routing_id :
                            existing_move_line = self.env['stock.move.line'].search([('id','in',move.move_line_ids.ids),
                                                                                ('product_id','=',move.product_id.id),
                                                                                ('state','!=','done'),
                                                                                ], limit=1)
                            if existing_move_line:
                                rounding = move.product_uom.rounding
                                existing_move_line.qty_done = existing_move_line.qty_done + float_round(production.partial_qty * move.unit_factor, precision_rounding=rounding)
                            else:
                                allowed_lot_ids = self.env['stock.production.lot'].search([
                                    ('product_id', '=', move.product_id.id),
                                    ('company_id', '=', move.company_id.id),
                                    ('quant_ids', '=', False),
                                ])
                                self.env['stock.move.line'].create({
                                    'lot_produced_ids': [(6, 0, allowed_lot_ids.ids)],
                                    'move_id':move.id,
                                    'location_id': production.location_src_id.id,
                                    'location_dest_id': production.product_id.property_stock_production.id,
                                    'product_uom_qty':quantity,
                                    'qty_done':quantity,
                                    'product_id':move.product_id.id,
                                    'product_uom_id':production.product_uom_id.id,
                                    'company_id': production.company_id.id,
                                })
                return True


class PartialProductionQtyLine(models.TransientModel):
    _name  = 'partial.production.qty.line'
    _description = 'Partial Production Qty Line'

    component_line_id = fields.Many2one('partial.production.qty')
    product_id = fields.Many2one('product.product')
    lot_id = fields.Many2one('stock.production.lot',string="Lot/Serial No")
    reserved_availability = fields.Float(string="Reserved",readonly=True)
    product_uom_qty = fields.Float(string="To Consume",readonly=True) 
    quantity_done = fields.Float(string="Consumed",readonly=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
