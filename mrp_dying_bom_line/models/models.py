# -*- coding: utf-8 -*-

from odoo import models, fields, api



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mrp_production_id = fields.Many2one(comodel_name="mrp.production", string="", required=False, )






class stockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    number_of_rolls_in_line = fields.Float(string="", required=False, )
    sequence = fields.Integer(string='Sequence', default=10)



class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_batch = fields.Boolean(string="Is Batch",  )
    batch_weight = fields.Float(string="Batch Weight", required=False, )
    mo_weight = fields.Float(string="MO Weight", required=False, )

    move_raw_ids = fields.One2many(
        'stock.move', 'raw_material_production_id', 'Components',
        copy=True, states={'done': [('readonly', False)], 'cancel': [('readonly', False)]},
        domain=[('scrapped', '=', False)])

    color_bom_id = fields.Many2one('mrp.bom')  # for dying

    chemical_bom_id = fields.Many2one('mrp.bom')  # for chemical
    finish_bom_id = fields.Many2one('mrp.bom', )  # for finish
    color_bom_line_ids = fields.Many2many('mrp.bom.line')
    production_bom_line_ids = fields.Many2many('production.bom.line')  # for dying

    # @api.onchange('name', 'chemical_bom_id', 'color_bom_id', 'finish_bom_id')
    # def domain_production_bom_line_ids(self):
    #     # self.product_id = False
    #     return {
    #         'domain': {'production_bom_line_ids': [
    #             ('original_bom_line_id', 'in', [line.id for line in self.color_bom_id.bom_line_ids])]},
    #
    #     }

    chemical_production_bom_line_ids = fields.Many2many('chemical.production.bom.line', )  # for chemical

    # @api.onchange('name', 'chemical_bom_id', 'color_bom_id', 'finish_bom_id')
    # def domain_chemical_production_bom_line_ids(self):
    #     self.chemical_production_bom_line_ids = self.chemical_production_bom_line_ids
    #
    #     return {
    #         'domain': {'chemical_production_bom_line_ids': [
    #             ('original_bom_line_id', 'in', [line.id for line in self.chemical_bom_id.bom_line_ids])]},
    #
    #     }

    finish_production_bom_line_ids = fields.Many2many('finish.production.bom.line', )  # for finish

    # @api.onchange('name', 'chemical_bom_id', 'color_bom_id', 'finish_bom_id')
    # def domain_finish_production_bom_line_ids(self):
    #     # self.product_id = False
    #     return {
    #         'domain': {'finish_production_bom_line_ids': [
    #             ('original_bom_line_id', 'in', [line.id for line in self.finish_bom_id.bom_line_ids])]},
    #
    #     }

    liqur_ratio = fields.Float(string="Liqur Ratio")
    liqur_ratio_2 = fields.Float(string="Liqur Ratio")
    liqur_ratio_3 = fields.Float(string="Liqur Ratio")
    dying_mo = fields.Boolean(string="Is Dying MO", default=False)  # to specify if it's a dying mo

    # for dyed MO specification

    grey_weight = fields.Float(string="Greige_M^2_Weight")
    grey_width = fields.Float(string="Greige_Width")
    raising = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Raising')

    carbon = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Carbon')

    compactor = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Compactor')
    gluing = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Gluing')
    cutting_selvadge = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Cutting Selvadge')
    heat_setting = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Heat Setting')
    oil_removing = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Oil Removing')
    enzyme = fields.Selection([
        ('no', 'No'),
        ('single', 'Single'),
        ('double', 'Double')], string='Enzyme')

    # for dying tab




    @api.onchange('batch_weight','mo_weight')
    def get_percentage(self):
        for rec in self:
            if rec .batch_weight and rec.mo_weight :
                for color in rec.production_bom_line_ids:
                    color.percentage_weight=rec.mo_weight / rec.batch_weight
                    color.git_quantity_weight()
                for line in rec.chemical_production_bom_line_ids:
                    line.percentage_weight=rec.mo_weight / rec.batch_weight
                    line.git_quantity_weight()


    def get_transfer(self):
        for rec in self:
            return {
                'domain': [('mrp_production_id.id', '=', self.id)],
                # 'res_id': po_create.id,
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                # 'view_type': 'form',
                'target': 'current',
            }
        # return {
        #     'name': 'Transfers',
        #     'view_type': 'form',
        #     'view_mode': 'tree,form',
        #     'res_model': 'payment.check.line',
        #     'view_id': False,
        #     'type': 'ir.actions.act_window',
        #     'domain': [('id', 'in', self.payment_check_lines.ids)],
        # }




    @api.onchange('color_bom_id')
    def onchange_production_bom_load_lines(self):
        if self.color_bom_id:
            print("Hello color bom lines")
            print(self.color_bom_id.bom_line_ids)
            # for line in self.color_bom_id.bom_line_ids:
            #     print('line', line.id)
            #     color = self.env['production.bom.line'].sudo().search(
            #         [('product_id', '=', line.product_id.id),
            #          ('original_bom_line_id', '=', line.id), ])
            #     print(color.id)
            #     if not color:
            #         color = self.env['production.bom.line'].sudo().create(
            #             {'product_id': line.product_id.id, 'product_qty': line.product_qty,
            #              'percentage': line.percentage, 'product_uom_id': line.product_uom_id.id,
            #              'original_bom_line_id': line.id,
            #              })
            self.write({'production_bom_line_ids': [(2, tag.id, 0) for tag in self.mapped('production_bom_line_ids')]})
            self.write(
                {'production_bom_line_ids': [(0, 0, {'product_id': line.product_id.id, 'product_qty': line.product_qty,
                                                     'percentage': line.percentage,
                                                     'product_uom_id': line.product_uom_id,
                                                     'original_bom_line_id': line.id})
                                             for line in self.color_bom_id.bom_line_ids]})

            # for chemicals tab

    # for chemicals tab
    @api.onchange('chemical_bom_id')
    def onchange_chemical_production_bom_load_lines(self):
        if self.chemical_bom_id:
            print("Hello chemicals bom lines")
            print(self.chemical_bom_id.bom_line_ids)
            # for line in self.chemical_bom_id.bom_line_ids:
            #     print('line', line.id)
            #     chemical = self.env['chemical.production.bom.line'].sudo().search(
            #         [('product_id', '=', line.product_id.id),
            #          ('original_bom_line_id', '=', line.id), ])
            #     if not chemical:
            #         chemical = self.env['chemical.production.bom.line'].sudo().create(
            #             {'product_id': line.product_id.id, 'product_qty': line.product_qty,
            #              'percentage': line.percentage, 'product_uom_id': line.product_uom_id.id,
            #              'original_bom_line_id': line.id,
            #              })

            self.write(
                {'chemical_production_bom_line_ids': [(2, tag.id, 0) for tag in
                                                      self.mapped('chemical_production_bom_line_ids')]})
            self.write(
                {'chemical_production_bom_line_ids': [
                    (0, 0, {'product_id': line.product_id.id, 'product_qty': line.product_qty,
                            'percentage': line.percentage, 'product_uom_id': line.product_uom_id,
                            'original_bom_line_id': line.id})
                    for line in self.chemical_bom_id.bom_line_ids]})

    # for finish tab
    @api.onchange('finish_bom_id')
    def onchange_finish_production_bom_load_lines(self):
        if self.finish_bom_id:
            bom_line_ids = []
            print("Hello finish bom lines")
            print(self.finish_bom_id.bom_line_ids)
            self.write(
                {'finish_production_bom_line_ids': [(2, tag.id, 0) for tag in
                                                    self.mapped('finish_production_bom_line_ids')]})
            self.write(
                {'finish_production_bom_line_ids': [
                    (0, 0, {'product_id': line.product_id.id, 'product_qty': line.product_qty,
                            'percentage': line.percentage, 'product_uom_id': line.product_uom_id,
                            'original_bom_line_id': line.id})
                    for line in self.finish_bom_id.bom_line_ids]})
            # for line in self.finish_bom_id.bom_line_ids:
            #     finish = self.env['finish.production.bom.line'].sudo().search(
            #         [('product_id', '=', line.product_id.id),
            #          ('original_bom_line_id', '=', line.id), ])
            #     if not finish:
            #         finish = self.env['finish.production.bom.line'].sudo().create(
            #             {'product_id': line.product_id.id, 'product_qty': line.product_qty,
            #              'percentage': line.percentage, 'product_uom_id': line.product_uom_id.id,
            #              'original_bom_line_id': line.id,
            #              })

    #     @api.onchange('color_bom_id')
    #     def onchange_color_bom_load_lines(self):
    #         if self.color_bom_id:
    #             print("Hello color bom lines")
    #             print(self.color_bom_id.bom_line_ids)
    #             self.write({'color_bom_line_ids': [(0, 0, {'product_id': line.product_id.id, 'product_qty': line.product_qty,
    #                                                        'original_bom_line_id': line.id, 'bom_id': 0})
    #                                                for line in self.color_bom_id.bom_line_ids]})
    #     #
    def compute_color_bom_line_quantity(self):
        if self.color_bom_id:
            if self.color_bom_id.material_type == 'chemicals':
                if self.production_bom_line_ids:
                    for line in self.production_bom_line_ids:
                        line.product_qty = self.product_qty * self.liqur_ratio * line.percentage / 100
                        # for update components of MO
            if self.color_bom_id.material_type == 'dyed':
                if self.production_bom_line_ids:
                    for line in self.production_bom_line_ids:
                        line.product_qty = self.product_qty * line.percentage / 100
                        # for update components of MO

    def send_money_bom_line(self):
        for line in self.production_bom_line_ids:
            list = []
            loop = 0
            for component in self.move_raw_ids:
                if component.bom_line_id.id == line.original_bom_line_id.id:
                    component.product_uom_qty = line.product_qty
                    loop = 1
            if loop == 0:
                comp = self.env['stock.move'].sudo().create({
                    'name': self.name,
                    'needs_lots': True,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'location_id': self.location_src_id.id,
                    'location_dest_id': self.production_location_id.id,
                    'product_uom_qty': line.product_qty,
                    'bom_line_id': line.original_bom_line_id.id,
                    'raw_material_production_id': self.id,
                })

    def compute_color_bom_line_quantity_chemicals(self):
        if self.chemical_bom_id:
            if self.chemical_bom_id.material_type == 'chemicals':
                if self.chemical_production_bom_line_ids:
                    for line in self.chemical_production_bom_line_ids:
                        line.product_qty = self.product_qty * self.liqur_ratio_2 * line.percentage / 100

    def send_money_chemicals(self):
        for line in self.chemical_production_bom_line_ids:
            list = []
            loop = 0
            for component in self.move_raw_ids:
                if component.bom_line_id.id == line.original_bom_line_id.id:
                    component.product_uom_qty = line.product_qty
                    loop = 1
            if loop == 0:
                comp = self.env['stock.move'].sudo().create({
                    'name': self.name,
                    'needs_lots': True,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'location_id': self.location_src_id.id,
                    'location_dest_id': self.production_location_id.id,
                    'product_uom_qty': line.product_qty,
                    'bom_line_id': line.original_bom_line_id.id,
                    'raw_material_production_id': self.id,
                })

    def compute_color_bom_line_quantity_finish(self):
        for rec in self:
            if self.finish_bom_id:
                if self.finish_production_bom_line_ids:
                    for line in self.finish_production_bom_line_ids:
                        line.product_qty = self.product_qty * self.liqur_ratio_3 * line.percentage / 100

    def send_money_finish(self):
        for line in self.finish_production_bom_line_ids:
            list = []
            loop = 0
            for component in self.move_raw_ids:
                if component.bom_line_id.id == line.original_bom_line_id.id:
                    component.product_uom_qty = line.product_qty
                    loop = 1
            if loop == 0:
                comp = self.env['stock.move'].sudo().create({
                    'name': self.name,
                    'needs_lots': True,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'location_id': self.location_src_id.id,
                    'location_dest_id': self.production_location_id.id,
                    'product_uom_qty': line.product_qty,
                    'bom_line_id': line.original_bom_line_id.id,
                    'raw_material_production_id': self.id,
                })


# def _compute_color_bom_line_quantity(self):
#     if self.color_bom_id:
#         if self.color_bom_id.material_type == 'chemicals':
#             if self.color_bom_line_ids:
#                 for line in self.color_bom_line_ids:
#                     line.product_qty = self.color_bom_id.product_qty * self.liqur_ratio * line.percentage / 100
#         elif self.color_bom_id.material_type == 'dyed':
#             if self.color_bom_line_ids:
#                 for line in self.color_bom_line_ids:
#                     line.product_qty = self.color_bom_id.product_qty * line.percentage / 100


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    original_bom_line_id = fields.Many2one('mrp.bom.line')


class ProductionBomLine(models.Model):
    _name = 'production.bom.line'

    product_id = fields.Many2one('product.product', string="Component")
    barcode = fields.Char(string="Barcode", required=False, related='product_id.barcode')
    percentage = fields.Float(string="Percentage", digits=(11, 4))
    product_qty = fields.Float(string="Quantity", digits=(11, 3))
    product_uom_id = fields.Many2one('uom.uom', string="Product UOM")
    original_bom_line_id = fields.Many2one('mrp.bom.line')
    is_editable = fields.Boolean(string="Editable", )
    qty_weight = fields.Float(string="Qty Weight",  required=False, )
    percentage_weight = fields.Float(string="Percentage Weight",  required=False, )

    @api.onchange('qty_weight', 'percentage_weight')
    def git_quantity_weight(self):
        for rec in self:
            rec.product_qty = rec.qty_weight * rec.percentage_weight


class ChemicalProductionBomLine(models.Model):
    _name = 'chemical.production.bom.line'

    product_id = fields.Many2one('product.product', string="Component")
    barcode = fields.Char(string="Barcode", required=False, related='product_id.barcode')
    percentage = fields.Float(string="Percentage", digits=(11, 4))
    product_qty = fields.Float(string="Quantity", digits=(11, 3))
    product_uom_id = fields.Many2one('uom.uom', string="Product UOM")
    original_bom_line_id = fields.Many2one('mrp.bom.line')
    is_editable = fields.Boolean(string="Editable", )
    qty_weight = fields.Float(string="Qty Weight", required=False, )
    percentage_weight = fields.Float(string="Percentage Weight", required=False, )


    @api.onchange('qty_weight','percentage_weight')
    def git_quantity_weight(self):
        for rec in self:
            rec.product_qty=rec.qty_weight * rec.percentage_weight


class FinishProductionBomLine(models.Model):
    _name = 'finish.production.bom.line'

    product_id = fields.Many2one('product.product', string="Component")
    barcode = fields.Char(string="Barcode", required=False,related='product_id.barcode')
    percentage = fields.Float(string="Percentage", digits=(11, 4))
    product_qty = fields.Float(string="Quantity", digits=(11, 3))
    product_uom_id = fields.Many2one('uom.uom', string="Product UOM")
    original_bom_line_id = fields.Many2one('mrp.bom.line')
    is_editable = fields.Boolean(string="Editable", )
