# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpProduction(models.Model): 
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    partial_qty  =  fields.Float('Partial Quantity To Produce', copy=False)

    @api.depends('move_raw_ids.quantity_done', 'move_finished_ids.quantity_done', 'is_locked')
    def _compute_post_visible(self):
        for order in self:
            if order.product_tmpl_id._is_cost_method_standard():
                order.post_visible = order.is_locked and any((x.quantity_done > 0 and x.state not in ['done', 'cancel']) for x in order.move_raw_ids | order.move_finished_ids)
            else:
                order.post_visible = order.is_locked and any((x.quantity_done > 0 and x.state not in ['done', 'cancel']) for x in order.move_finished_ids)

    def _generate_workorders(self, exploded_boms):

        workorders = self.env['mrp.workorder']
        original_one = False
        for bom, bom_data in exploded_boms:
            # If the routing of the parent BoM and phantom BoM are the same, don't recreate work orders, but use one master routing
            if bom.routing_id.id and (not bom_data['parent_line'] or bom_data['parent_line'].bom_id.routing_id.id != bom.routing_id.id):
                temp_workorders = self._workorders_create(bom, bom_data)
                workorders += temp_workorders
                if temp_workorders: # In order to avoid two "ending work orders"
                    if original_one:
                        temp_workorders[-1].next_work_order_id = original_one
                    original_one = temp_workorders[0]
        return workorders

    def _workorders_create(self, bom, bom_data):
        
        """
        :param bom: in case of recursive boms: we could create work orders for child
                    BoMs
        """
        workorders = self.env['mrp.workorder']
        # Initial qty producing
        quantity = self.partial_qty
        quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom_id)
        if self.product_id.tracking == 'serial':
            quantity = 1.0

        values = []    
        workorder_record = self._context.get('raw_workorder_line_ids')
    
        for operation in bom.routing_id.operation_ids:
            workorder = workorders.create({
                'name': operation.name,
                'production_id': self.id,
                'workcenter_id': operation.workcenter_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'operation_id': operation.id,
                'state': len(workorders) == 0 and 'ready' or 'pending',
                'qty_producing': quantity,
                'consumption': self.bom_id.consumption,
                'qty_production_wo': quantity,
                'finished_lot_id': self._context.get('finished_lot_id',False),
            })
            if workorders:
                workorders[-1].next_work_order_id = workorder.id
                workorders[-1]._start_nextworkorder()
            workorders += workorder

            moves_raw = self.move_raw_ids.filtered(lambda move: move.operation_id == operation and move.bom_line_id.bom_id.routing_id == bom.routing_id)
            moves_finished = self.move_finished_ids.filtered(lambda move: move.operation_id == operation)
            # - Raw moves from a BoM where a routing was set but no operation was precised should
            #   be consumed at the last workorder of the linked routing.
            # - Raw moves from a BoM where no rounting was set should be consumed at the last
            #   workorder of the main routing.
            if len(workorders) == len(bom.routing_id.operation_ids):
                moves_raw |= self.move_raw_ids.filtered(lambda move: not move.operation_id and move.bom_line_id.bom_id.routing_id == bom.routing_id)
                moves_raw |= self.move_raw_ids.filtered(lambda move: not move.workorder_id and not move.bom_line_id.bom_id.routing_id)
 
                moves_finished |= self.move_finished_ids.filtered(lambda move: move.product_id != self.product_id and not move.operation_id)
 
            moves_raw.mapped('move_line_ids').write({'workorder_id': workorder.id})
            (moves_finished | moves_raw).write({'workorder_id': workorder.id})
        
            workorder._generate_wo_lines()
            
            #Passing lot_no values directly to the lines. Just worked for Lot no. Not serial number
            # for rec in workorder.raw_workorder_line_ids:
            #     print(rec.lot_id)
            #     for value in workorder_record:
            #         if rec.product_id == value.product_id:
            #             rec.update({'lot_id': value.lot_id}) 
        if not workorders.mapped('check_ids'):
                workorders._create_checks()
        return workorders

    def _plan_workorders(self):
        """ Plan all the production's workorders depending on the workcenters
        work schedule"""
        self.ensure_one()

        # Schedule all work orders (new ones and those already created)
        qty_to_produce = max(self.product_qty - self.qty_produced, 0)
        qty_to_produce = self.product_uom_id._compute_quantity(qty_to_produce, self.product_id.uom_id)
        start_date = self._get_start_date()
        for workorder in self.workorder_ids.filtered(lambda order: order.state != 'done'):
            workcenters = workorder.workcenter_id | workorder.workcenter_id.alternative_workcenter_ids

            best_finished_date = datetime.datetime.max
            vals = {}
            for workcenter in workcenters:
                # compute theoretical duration
                time_cycle = workorder.operation_id.time_cycle
                cycle_number = float_round(qty_to_produce / workcenter.capacity, precision_digits=0, rounding_method='UP')
                duration_expected = workcenter.time_start + workcenter.time_stop + cycle_number * time_cycle * 100.0 / workcenter.time_efficiency

                # get first free slot
                # planning 0 hours gives the start of the next attendance
                from_date = workcenter.resource_calendar_id.plan_hours(0, start_date, compute_leaves=True, resource=workcenter.resource_id, domain=[('time_type', 'in', ['leave', 'other'])])
                # If the workcenter is unavailable, try planning on the next one
                if from_date is False:
                    continue
                to_date = workcenter.resource_calendar_id.plan_hours(duration_expected / 60.0, from_date, compute_leaves=True, resource=workcenter.resource_id, domain=[('time_type', 'in', ['leave', 'other'])])

                # Check if this workcenter is better than the previous ones
                if to_date and to_date < best_finished_date:
                    best_start_date = from_date
                    best_finished_date = to_date
                    best_workcenter = workcenter
                    vals = {
                        'workcenter_id': workcenter.id,
                        'capacity': workcenter.capacity,
                        'duration_expected': duration_expected,
                    }

            # If none of the workcenter are available, raise
            if best_finished_date == datetime.datetime.max:
                raise UserError(_('Impossible to plan the workorder. Please check the workcenter availabilities.'))

            # Instantiate start_date for the next workorder planning
            if workorder.next_work_order_id:
                if workorder.operation_id.batch == 'no' or workorder.operation_id.batch_size >= qty_to_produce:
                    start_date = best_finished_date
                else:
                    cycle_number = float_round(workorder.operation_id.batch_size / best_workcenter.capacity, precision_digits=0, rounding_method='UP')
                    duration = best_workcenter.time_start + cycle_number * workorder.operation_id.time_cycle * 100.0 / best_workcenter.time_efficiency
                    start_date = best_workcenter.resource_calendar_id.plan_hours(duration / 60.0, best_start_date, compute_leaves=True, resource=best_workcenter.resource_id, domain=[('time_type', 'in', ['leave', 'other'])])

            # Create leave on chosen workcenter calendar
            leave = self.env['resource.calendar.leaves'].create({
                'name': self.name + ' - ' + workorder.name,
                'calendar_id': best_workcenter.resource_calendar_id.id,
                'date_from': best_start_date,
                'date_to': best_finished_date,
                'resource_id': best_workcenter.resource_id.id,
                'time_type': 'other'
            })
            vals['leave_id'] = leave.id
            workorder.write(vals)
        self.with_context(force_date=True).write({
            'date_planned_start': self.workorder_ids[0].date_planned_start,
            'date_planned_finished': self.workorder_ids[-1].date_planned_finished
        })

    def post_inventory(self):
        for order in self:
            moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
                move.product_uom_qty = move.quantity_done
            # MRP do not merge move, catch the result of _action_done in order
            # to get extra moves.
            moves_to_do = moves_to_do._action_done()
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
            order._cal_price(moves_to_do)
            moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves_to_finish = moves_to_finish._action_done()
            order.workorder_ids.mapped('raw_workorder_line_ids').unlink()
            order.workorder_ids.mapped('finished_workorder_line_ids').unlink()
            order.action_assign()
            consume_move_lines = moves_to_do.mapped('move_line_ids')
            for moveline in moves_to_finish.mapped('move_line_ids'):
                if moveline.move_id.has_tracking != 'none' and moveline.product_id == order.product_id:
#                     if any([not ml.lot_produced_ids for ml in consume_move_lines]):
#                         raise UserError(_('You can not consume without telling for which lot you consumed it'))
                    # Link all movelines in the consumed with same lot_produced_ids false or the correct lot_produced_ids
                    filtered_lines = consume_move_lines.filtered(lambda ml: moveline.lot_id in ml.lot_produced_ids)
                    moveline.write({'consume_line_ids': [(6, 0, [x for x in filtered_lines.ids])]})
                else:
                    # Link with everything
                    moveline.write({'consume_line_ids': [(6, 0, [x for x in consume_move_lines.ids])]})
        return True

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    qty_production_wo = fields.Float('Original Production Quantity Wo', readonly=True)

    def _create_or_update_finished_line(self):
        """
        1. Check that the final lot and the quantity producing is valid regarding
            other workorders of this production
        2. Save final lot and quantity producing to suggest on next workorder
        """
        self.ensure_one()
        final_lot_quantity = self.qty_production_wo
        rounding = self.product_uom_id.rounding
        # Get the max quantity possible for current lot in other workorders
        for workorder in (self.production_id.workorder_ids - self):
            # We add the remaining quantity to the produced quantity for the
            # current lot. For 5 finished products: if in the first wo it
            # creates 4 lot A and 1 lot B and in the second it create 3 lot A
            # and it remains 2 units to product, it could produce 5 lot A.
            # In this case we select 4 since it would conflict with the first
            # workorder otherwise.
            line = workorder.finished_workorder_line_ids.filtered(lambda line: line.lot_id == self.finished_lot_id)
            line_without_lot = workorder.finished_workorder_line_ids.filtered(lambda line: line.product_id == workorder.product_id and not line.lot_id)
            quantity_remaining = workorder.qty_remaining + line_without_lot.qty_done or self.qty_production_wo
            quantity = line.qty_done + quantity_remaining
            if line and float_compare(quantity, final_lot_quantity, precision_rounding=rounding) <= 0:
                final_lot_quantity = quantity
            elif float_compare(quantity_remaining, final_lot_quantity, precision_rounding=rounding) < 0:
                final_lot_quantity = quantity_remaining

        # final lot line for this lot on this workorder.
        current_lot_lines = self.finished_workorder_line_ids.filtered(lambda line: line.lot_id == self.finished_lot_id)
        # this lot has already been produced
        if float_compare(final_lot_quantity, current_lot_lines.qty_done + self.qty_producing, precision_rounding=rounding) < 0:
            raise UserError(_('You have produced %s %s of lot %s in the previous workorder. You are trying to produce %s in this one') %
                (final_lot_quantity, self.product_id.uom_id.name, self.finished_lot_id.name, current_lot_lines.qty_done + self.qty_producing))

        # Update workorder line that regiter final lot created
        if not current_lot_lines:
            current_lot_lines = self.env['mrp.workorder.line'].create({
                'finished_workorder_id': self.id,
                'product_id': self.product_id.id,
                'lot_id': self.finished_lot_id.id,
                'qty_done': self.qty_producing,
            })
        else:
            current_lot_lines.qty_done += self.qty_producing


    def _generate_wo_lines(self):
        """ Generate workorder line """
        print(self._context)
        self.ensure_one()
        workorder_record = self._context.get('raw_workorder_line_ids')
        moves = (self.move_raw_ids | self.move_finished_ids).filtered(
            lambda move: move.state not in ('done', 'cancel')
        )
        for move in moves:
            qty_to_consume = self._prepare_component_quantity(move, self.qty_producing)
            line_values = self._generate_lines_values(move, qty_to_consume)
            pro_list = []
            for line in line_values:
                if len(line) > 1:
                    for value in workorder_record:
                        product = self.env['product.product'].browse(line.get('product_id'))
                        if value.product_id not in pro_list:
                            if product == value.product_id:       
                                line.update({'lot_id': value.lot_id.id})
                                pro_list.append(value.product_id)
                       
                else:
                    for value in workorder_record:
                        if line.get('product_id.id') == value.product_id:
                            line.update({'lot_id': value.lot_id.id})                 
            self.env['mrp.workorder.line'].create(line_values)    
                
    
    def _start_nextworkorder(self):
        rounding = self.product_id.uom_id.rounding
        if self.next_work_order_id.state == 'pending' and (
                (self.operation_id.batch == 'no' and
                 float_compare(self.qty_production_wo, self.qty_produced, precision_rounding=rounding) <= 0) or
                (self.operation_id.batch == 'yes' and
                 float_compare(self.operation_id.batch_size, self.qty_produced, precision_rounding=rounding) <= 0)):
            self.next_work_order_id.state = 'ready'

    @api.depends('qty_production_wo', 'qty_produced')
    def _compute_qty_remaining(self):
        for wo in self:
            wo.qty_remaining = float_round(wo.qty_production_wo - wo.qty_produced, precision_rounding=wo.production_id.product_uom_id.rounding)


    def record_production(self):
        if not self:
            return True

        self.ensure_one()
        self._check_company()
        if float_compare(self.qty_producing, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_('Please set the quantity you are currently producing. It should be different from zero.'))

        # If last work order, then post lots used
        if not self.next_work_order_id:
            self._update_finished_move()

        # Transfer quantities from temporary to final move line or make them final
        self._update_moves()

        # Transfer lot (if present) and quantity produced to a finished workorder line
        if self.product_tracking != 'none':
            self._create_or_update_finished_line()

        # Update workorder quantity produced
        self.qty_produced += self.qty_producing

        # Suggest a finished lot on the next workorder
        if self.next_work_order_id and self.product_tracking != 'none' and (not self.next_work_order_id.finished_lot_id or self.next_work_order_id.finished_lot_id == self.finished_lot_id):
            self.next_work_order_id._defaults_from_finished_workorder_line(self.finished_workorder_line_ids)
            # As we may have changed the quantity to produce on the next workorder,
            # make sure to update its wokorder lines
            self.next_work_order_id._apply_update_workorder_lines()

        # One a piece is produced, you can launch the next work order
        self._start_nextworkorder()

        # Test if the production is done
        rounding = self.production_id.product_uom_id.rounding
        if float_compare(self.qty_produced, self.production_id.partial_qty, precision_rounding=rounding) < 0:
            previous_wo = self.env['mrp.workorder']
            if self.product_tracking != 'none':
                previous_wo = self.env['mrp.workorder'].search([
                    ('next_work_order_id', '=', self.id)
                ])
            candidate_found_in_previous_wo = False
            if previous_wo:
                candidate_found_in_previous_wo = self._defaults_from_finished_workorder_line(previous_wo.finished_workorder_line_ids)
            if not candidate_found_in_previous_wo:
                # self is the first workorder
                self.qty_producing = self.qty_remaining
                self.finished_lot_id = False
                if self.product_tracking == 'serial':
                    self.qty_producing = 1

            self._apply_update_workorder_lines()
        else:
            self.qty_producing = 0
            self.button_finish()
        return True

