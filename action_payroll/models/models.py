# -*- coding: utf-8 -*-

from odoo import models, fields, api


class action_payroll(models.Model):
    _inherit = 'hr.payslip'
 

    overtime_1 = fields.Float(string="OverTime(Night Shift)", store=True)
    overtime_2 = fields.Float(string="OverTime(Day Shift)", store=True)
    bonus = fields.Float(string="Bonus", store=True)
    incentive = fields.Float(string="Incentive", store=True)
    adjustment_1 = fields.Float(string="Additional Adjustment", store=True)
    absence_with_per = fields.Float(string="Absence With Permission", store=True)
    absence_without_per = fields.Float(string="Absence Without Permission", store=True)
    penality = fields.Float(string="Penality", store=True)
    latency1 = fields.Float(string="Latency 1", store=True)
    adjustment_2 = fields.Float(string="Deduction Adjustment", store=True)
    other = fields.Float(string="Other Deduction", store=True)


    
