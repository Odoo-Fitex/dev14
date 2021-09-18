# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from datetime import date, datetime
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def create_receive_bom_lines(self):
        for rec in self:
            moves = []
            for production in rec.production_bom_line_ids:
                moves.append([0, 0, {
                    'product_id': production.product_id.id,
                    'name': production.product_id.product_tmpl_id.name,
                    'date_expected': datetime.now(),
                    'product_uom_qty': production.product_qty,
                    'product_uom': production.product_uom_id.id,
                    'has_move_lines': False,
                    'additional': True,
                    'is_initial_demand_editable': True,
                }])
            for chemical in rec.chemical_production_bom_line_ids:
                moves.append([0, 0, {
                    'product_id': chemical.product_id.id,
                    'name': chemical.product_id.product_tmpl_id.name,
                    'date_expected': datetime.now(),
                    'product_uom_qty': chemical.product_qty,
                    'product_uom': chemical.product_uom_id.id,
                    'has_move_lines': False,
                    'additional': True,
                    'is_initial_demand_editable': True,
                }])
            for finish in rec.finish_production_bom_line_ids:
                moves.append([0, 0, {
                    'product_id': finish.product_id.id,
                    'name': finish.product_id.product_tmpl_id.name,
                    'date_expected': datetime.now(),
                    'product_uom_qty': finish.product_qty,
                    'product_uom': finish.product_uom_id.id,
                    'has_move_lines': False,
                    'additional': True,
                    'is_initial_demand_editable': True,
                }])
            print('moves', moves)
        if moves:
            picking = self.env['stock.picking'].sudo().create({
                'location_id': 50,
                'mrp_production_id': self.id,
                'location_dest_id': 43,
                'picking_type_id': 43,
                'scheduled_date': self.date_planned_start,
                'origin': self.name,
                "move_ids_without_package": moves,
            })
            # for line in self.chemical_production_bom_line_ids:
            #     move = self.env['stock.move'].create({'picking_id': picking.id,
            #                                           'product_id': line.product_id.id,
            #                                           'product_uom_qty': line.product_qty,
            #                                           'product_uom': line.product_uom_id.id,
            #                                           'name': line.product_id.product_tmpl_id.name,
            #                                           'location_id': 8,
            #                                           'location_dest_id': 18,
            #
            #                                           })
            # make picking in ready state
            #                 picking.action_confirm()

            return {
                'name': _('Receive Products'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('id', '=', picking.id)],
            }
        else:
            print("NO Picking")

    # else:
    # raise UserError("Warning , Please Enter chemicals lines")
# else:
#     print("NO ARR")
#     return{
#         'name': _('Receive Products'),
#         'res_model': 'stock.picking',
#         'view_mode': 'form',
#         'view_id': self.env.ref('stock.view_picking_form').id,
#         # 'context': {'default_move_ids_without_package': arr},
#         'target': 'new',
#         'type': 'ir.actions.act_window',
#     }
