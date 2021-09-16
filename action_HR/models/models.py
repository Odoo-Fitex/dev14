# -*- coding: utf-8 -*-
from odoo import models, fields, api


class action_HR(models.Model):
    _inherit = 'hr.employee'

    address_name = fields.Char(string='Address', store=True)
    social_number = fields.Integer(string='Social Insurance Number', store=True)
    social_amount = fields.Integer(string='Social Insurance Amount', store=True)
    social_date = fields.Date(string='Social Insurance Date', store=True)
    
