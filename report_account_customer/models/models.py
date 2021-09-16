# -*- coding: utf-8 -*-

from odoo import models, fields, api



class ImportantJournalLedger(models.TransientModel):
    _name = 'general.ledger.vendor.wizard'
    _description = 'general ledger vendor wizard'



    name = fields.Char()
    date_from = fields.Date(string="Date From", required=False, )
    date_to = fields.Date(string="Date To", required=False, )
    partner_ids = fields.Many2many('res.partner', string='customer')





    def export_product(self):
        for rec in self:
            if not rec.partner_ids:
                rec.partner_ids=self.env['res.partner'].sudo().search([('customer_rank','>',0)]).ids
            return self.env.ref('report_account_customer.report_action_id_general_ledger_customer').report_action(self)

