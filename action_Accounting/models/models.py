
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime, timedelta

class AccountMoveLine(models.Model):  
    _inherit = "account.move"
    name = fields.Char(string='Number', required=True, store=True, readonly=False, copy=False, default='/')
    
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'Fully Billed'),
    ], string='Billing Status', store=True, readonly=False, copy=False)

class SaleReport(models.Model):
    _inherit = 'sale.order'
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string="Invoice Status", store=True, readonly=False)
    
class account_payment(models.Model):
    _inherit = "account.payment"
    move_name = fields.Char(string='Journal Entry Name', readonly=False,
        default=False, store=True, copy=False,
        help="Technical field holding the number given to the journal entry, automatically set when the statement line is reconciled then stored to set the same number again if the line is cancelled, set to draft and re-processed again.")

    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    today = fields.Date(string="Today", store=True, default=datetime.now().strftime('%Y-%m-%d'))
    general_balance = fields.Monetary(string='Balance', store=True,
                                      compute='compute_balance')
#     balance_sum = fields.Float('Quantity', compute='compute_balance_sum')
    

    @api.depends('debit', 'credit')
    def compute_balance(self):   
           for line in self:
            if line.general_balance:
                line.general_balance = line.debit - line.credit
            else:
                line.general_balance = 0
     
            
class AccountAccount(models.Model):
    _inherit = "account.account"
    
    total_debit = fields.Monetary(string="Total Debit", compute='compute_total_debit_balance_credit')
    total_credit = fields.Monetary(string="Total Credit", compute='compute_total_debit_balance_credit')
    total_balance = fields.Monetary(string="Total Balance", compute='compute_total_debit_balance_credit')    
    today = fields.Date(string="Today", compute='compute_total_today_debit_balance_credit')
    total_debit_today = fields.Monetary(string="Total Debit Today",  compute='compute_total_today_debit_balance_credit')
    total_credit_today = fields.Monetary(string="Total Credit Today", compute='compute_total_today_debit_balance_credit')
    total_balance_today = fields.Monetary(string="Total Balance Today", compute='compute_total_today_debit_balance_credit')
    total_debit_beforetoday = fields.Monetary(string="Total Debit Before Today", compute='compute_total_today_debit_balance_credit')
    total_credit_beforetoday = fields.Monetary(string="Total Credit Before Today", compute='compute_total_today_debit_balance_credit')
    total_balance_beforetoday = fields.Monetary(string="Total Balance Before Today", compute='compute_total_today_debit_balance_credit')

    def compute_total_debit_balance_credit(self):
        for record in self:
            total_debit = total_credit = total_balance = 0.0
            for line in self.env['account.move.line'].search([('account_id', '=', record.id),('move_id.state', '=', 'posted')]):
                total_debit += line.debit
                total_credit += line.credit 
                total_balance += line.balance
            record.total_debit = total_debit
            record.total_credit = total_credit
            record.total_balance = total_balance

    def compute_total_today_debit_balance_credit(self):
        for record in self:
            record.today = fields.Date.today()
            total_credit_today = total_debit_today = total_balance_today = 0.0
            for line in self.env['account.move.line'].search([('account_id', '=', record.id),('date', '=', fields.Date.today()),('move_id.state', '=', 'posted')]):
                total_debit_today += line.debit
                total_credit_today += line.credit 
                total_balance_today += line.balance
            record.total_debit_today = total_debit_today
            record.total_credit_today = total_credit_today
            record.total_balance_today = total_balance_today
            record.total_debit_beforetoday = record.total_debit - total_debit_today
            record.total_credit_beforetoday = record.total_credit - total_credit_today
            record.total_balance_beforetoday = record.total_balance - total_balance_today

class AccountJournalEntries(models.Model):  
    _inherit = "account.move"
    to_delete = fields.Boolean(string='To Be Deleted', default = False)
