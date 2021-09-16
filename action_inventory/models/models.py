# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError



class action_inventory(models.Model):
    _inherit = 'stock.production.lot'
    
    roll_number = fields.Integer(string="Number Of Rolls/Boxes", store=True)
    notes = fields.Char(string="Notes", store=True)



class action_inventory2(models.Model):
    _inherit = 'stock.inventory.line'
    
    roll_number2 = fields.Integer(string='Number Of Rolls/Boxes',
                               store=True,
                               related='prod_lot_id.roll_number')

class action_inventory3(models.Model):
    _inherit = 'stock.quant'
    
    roll_number3 = fields.Integer(string='Number Of Rolls/Boxes',
                               store=True,
                               related='lot_id.roll_number')
class action_inventory_scrap_fields(models.Model):
    _inherit = 'stock.scrap'
    
    
    scrap_reason = fields.Selection([
        ('عروق في الغزل', 'عروق في الغزل'),
        ('تهويه', 'تهويه'),
        ('عقده كبيره من الفني ', 'عقده كبيره من الفني'),
        ('نوعية الغزل ', 'نوعية الغزل'),
        ('اتساخات في الغزل', 'اتساخات في الغزل'),
        ('سوء تخزين الغزل', 'سوء تخزين الغزل'),
        ('تهريب ليكرا بسبب وبرة', ' تهريب ليكرا بسبب وبرة'),
        ('لضمة خطأ من الفني', ' لضمة خطأ من الفني'),
        ('دخول فتله ليكرا مع فتله الغزل', 'دخول فتله ليكرا مع فتله الغزل'),
        ('تقصيف ليكرا بسبب خلل في الماكينه', 'تقصيف ليكرا بسبب خلل في الماكينه'),
        ('انتهاء العمر الافتراضي للأبر', 'انتهاء العمر الافتراضي للأبر'),
        ('رفع سرعة الماكينه', 'رفع سرعة الماكينه'),
        ('عقدة كبيرة', 'عقدة كبيرة'),
        ('وبرة', 'وبرة'),
        ('خلل كهربائي في البطاريه', 'خلل كهربائي في البطاريه'),
        ('بطارية ملغيه', 'بطارية ملغيه'),
        ('اتساخات في السلندر تحت الابر', 'اتساخات في السلندر تحت الابر'),
        ('الابلاتين', 'الابلاتين'),
        ('امتلأ عبوة الزيت الفايظ', 'امتلأ عبوة الزيت الفايظ'),
        ('تسريب في خراطيم الزيت', 'تسريب في خراطيم الزيت'),
        ('خطأ من الفني', 'خطأ من الفني'),
        ('خلل في البطارية', 'خلل في البطارية'),
        ('فتله سلبي', 'فتله سلبي'),
        ('عينات معمل', 'عينات معمل'),
        ('عينات', 'عينات'),
        ('بدايه تشغيل الماكينه', 'بدايه تشغيل الماكينه'),
        ('انتهاء العمر الافتراضي للأبر', 'انتهاء العمر الافتراضي للأبر')], store=True, string="Reason Of Scrap")
    
    MO = fields.Char(string="MO_Reference", store=True)
    
    scrap_type = fields.Selection([
        ('ابرة', 'ابرة'),
        ('ريجا غزل', 'ريجا غزل'),
        ('ريجا ليكرا ', 'ريجا ليكرا '),
        ('ريجا متقطعه', 'ريجا متقطعه'),
        ('ريجا متقطعه', 'ريجا متقطعه'),
        ('تنميل ليكرا', 'تنميل ليكرا'),
        ('ثقوب', 'ثقوب'),
        ('فتله ناقصه', 'فتله ناقصه'),
        ('ابرة زيت', 'ابرة زيت'),
        ('زيت', 'زيت'),
        ('معمل صباغة', 'معمل صباغة'),
        ('عينات كارت صنف', 'عينات كارت صنف'),
        ('ريجا بطاريه مرفوعه', 'ريجا بطاريه مرفوعه'),
        ('عيوب ضبط الماكينه', 'عيوب ضبط الماكينه'),
        ('ابرة مشرزة', 'ابرة مشرزة')], store=True, string='Type Of Scrap')
    
    scrap_lable = fields.Selection([
        ('Scrap', 'Scrap'),
        ('Black', 'Black'),
        ('White/Printing', 'White/Printing'),
        ('B.quality', 'B.quality')], store=True, string='Lable ')
    notes = fields.Char(string="Notes", store=True)
    
class action_inventory2(models.Model):
    _inherit = 'stock.scrap'

    @api.onchange('stock.scrap_lable')
    def onchange_lable_in_scrap(self):
            if stock.scrap_lable == "Scrap":
                stock.scrap_location_id == "Virtual Locations/My Company: Scrap"
     
class Picking(models.Model):
    _inherit = "stock.picking"
    partner_id = fields.Many2one(
    'res.partner', 'Contact', store=True,
         check_company=True)
# ,
#     states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}
    connected = fields.Boolean(string="Connected to Sales/Purchase order", store=True, default="True")
    def button_validate(self):
        res = super(Picking, self).button_validate()
#         if  ((self.sale_id and self.purchase_id) or self.connected==True):
#             raise UserError("هذا الإذن غير مرتبط بإذن شراء أو بيع برجاء مراجعة قسم التخطيط")
        for rec in self.move_line_ids_without_package:
            current_number_of_rolls = rec.lot_id.roll_number
            new_number_of_rolls = current_number_of_rolls - rec.rolls_number2
            rec.lot_id.write({'roll_number': new_number_of_rolls})
        return res
      
    def WHIN_order_edit(self):
      self.write({'state': 'cancel'})
      
class StockScrap(models.Model):
    _inherit = 'stock.scrap'
    
    date_done = fields.Datetime('Date', store=True, readonly=False)
    worker = fields.Many2one(
                             'hr.employee', 'Responsable Worker', store=True )
                              # domain="['|',('department_id', '=', 'Production'),('department_id', '=', 'Production / Maintenance')]", store=True)
class SalesOrderAccess(models.Model):
    _inherit = 'stock.picking'
    sales = fields.Many2one('sale.order', 'Sales Order',
        compute='_compute_Sales_order_origin')
    purchase = fields.Many2one('purchase.order', 'Purchase Order',
        compute='_compute_Sales_order_origin')

    @api.depends('origin')
    def _compute_Sales_order_origin(self):
         if self.origin:
            if self.origin[:1] == 'S':
              sale_order = self.env['sale.order'].search([('name', '=', self.origin)])
              self.sales = sale_order.id
              self.purchase = False
            elif self.origin[:1] == 'P':
              purchase_order = self.env['purchase.order'].search([('name', '=', self.origin)])
              self.purchase = purchase_order.id
              self.sales = False
            else:
              self.sales = False
              self.purchase = False
         else:
             self.sales = False
             self.purchase = False
