# -*- coding: utf-8 -*-

from odoo import models, fields, api

class project(models.Model):
    _inherit = 'hr.contract'

    hra = fields.Float(string='House Allowance', help="House allowance.")
    tr_allowance= fields.Float(string='Transportation Allowance ', help="Deamess allowance.")
    phone_allowance = fields.Float(string='Phone Allowance', help="monthly Travel allowance.")
    meal_allowance = fields.Float(string='Meal Allowance', help="monthly Meal allowance.")
    car_allowance = fields.Float(string='Car Allowance', help="monthly car allowance.")
    clothing_allowance = fields.Float(string='Clothing Allowance', help="monthly Other allowance.")
    social_insurance_per = fields.Float(string='social %', help="Social Insurance.")
    social_insurance = fields.Float(string='social insurance', help="Social Insurance.",compute="compute_social")

    @api.depends('social_insurance_per')
    def compute_social(self):
        # if self.social_insurance_per:
        self.social_insurance = (self.social_insurance_per * self.wage) / 100

class project(models.Model):
    _inherit = 'hr.employee'

    code = fields.Char(string='Employee_Code', help="employee_code")