# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMoveLine(models.Model): 
    _inherit = "account.move"
    name = fields.Char(string='Number', required=True, readonly=False, copy=False, default='/')   
    
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
        ], string="Invoice Status", readonly=False)
    
class account_payment(models.Model):
    _inherit = "account.payment"
    name = fields.Char(readonly=False)
    move_name = fields.Char(string='Journal Entry Name', readonly=False,
        default=False, copy=False,
        help="Technical field holding the number given to the journal entry, automatically set when the statement line is reconciled then stored to set the same number again if the line is cancelled, set to draft and re-processed again.")
