# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, fields
from datetime import datetime, timedelta
from odoo.tools.misc import format_date

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter
import io



class ReportGeneralLedger(models.AbstractModel):
    _inherit = "account.general.ledger"
    
    filter_currencys = True
        
    @api.model
    def _get_options(self, previous_options=None):
        res = super(ReportGeneralLedger, self)._get_options(previous_options)
        if self.filter_currencys :
            currencies = self.env['res.currency'].search([])
            res['currenciess'] = [{'id': c.id, 'name': c.name, 'selected': False} for c in currencies]
            if 'curr' in self._context:
                for c in res['currenciess']:
                    if c['id'] == self._context.get('curr'):
                        c['selected'] = True
            else:
                for c in res['currenciess']:
                    if c['id'] == self.env.user.company_id.currency_id.id:
                        c['selected'] = True
            res['currencys'] = True
        return res
    
    @api.model
    def _load_more_lines(self, options, line_id, offset, load_more_remaining, balance_progress):
        if 'curr' in self._context:
            cur = self.env['res.currency'].browse(self._context.get('curr'))
            ''' Get lines for an expanded line using the load more.
            :param options: The report options.
            :param line_id: string representing the line to expand formed as 'loadmore_<ID>'
            :params offset, load_more_remaining: integers. Parameters that will be used to fetch the next aml slice
            :param balance_progress: float used to carry on with the cumulative balance of the account.move.line
            :return:        A list of lines, each one represented by a dictionary.
            '''
            lines = []
            expanded_account = self.env['account.account'].browse(int(line_id[9:]))
    
            load_more_counter = self.MAX_LINES
    
            # Fetch the next batch of lines.
            amls_query, amls_params = self._get_query_amls(options, expanded_account, offset=offset, limit=load_more_counter)
            self._cr.execute(amls_query, amls_params)
            for aml in self._cr.dictfetchall():
                # Don't show more line than load_more_counter.
                if load_more_counter == 0:
                    break
    
                balance_progress += cur._compute(self.env.user.company_id.currency_id,cur,aml['balance'])
    
                # account.move.line record line.
                lines.append(self._get_aml_line(options, expanded_account, aml, balance_progress))
    
                offset += 1
                load_more_remaining -= 1
                load_more_counter -= 1
    
            if load_more_remaining > 0:
                # Load more line.
                lines.append(self._get_load_more_line(
                    options, expanded_account,
                    offset,
                    load_more_remaining,
                    balance_progress,
                ))
            return lines
        return super(ReportGeneralLedger, self)._load_more_lines(options, line_id, offset, load_more_remaining, balance_progress)
    @api.model
    def _get_general_ledger_lines(self, options, line_id=None):
        ''' Get lines for the whole report or for a specific line.
        :param options: The report options.
        :return:        A list of lines, each one represented by a dictionary.
        '''
        if 'curr' in self._context:
            cur = self.env['res.currency'].browse(self._context.get('curr'))
            lines = []
            options_list = self._get_options_periods_list(options)
            unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])
            date_from = fields.Date.from_string(options['date']['date_from'])
            company_currency = self.env.company.currency_id
    
            expanded_account = line_id and self.env['account.account'].browse(int(line_id[8:]))
            accounts_results, taxes_results = self._do_query(options_list, expanded_account=expanded_account)
    
            total_debit = total_credit = total_balance = 0.0
            for account, periods_results in accounts_results:
                # No comparison allowed in the General Ledger. Then, take only the first period.
                results = periods_results[0]
    
                is_unfolded = 'account_%s' % account.id in options['unfolded_lines']
    
                # account.account record line.
                account_sum = results.get('sum', {})
                account_un_earn = results.get('unaffected_earnings', {})
    
                # Check if there is sub-lines for the current period.
                max_date = account_sum.get('max_date')
                has_lines = max_date and max_date >= date_from or False
    
                amount_currency = account_sum.get('amount_currency', 0.0) + account_un_earn.get('amount_currency', 0.0)
                debit = account_sum.get('debit', 0.0) + account_un_earn.get('debit', 0.0)
                credit = account_sum.get('credit', 0.0) + account_un_earn.get('credit', 0.0)
                balance = account_sum.get('balance', 0.0) + account_un_earn.get('balance', 0.0)
                
                debit = cur._compute(self.env.user.company_id.currency_id,cur,debit)
                credit = cur._compute(self.env.user.company_id.currency_id,cur,credit)
                balance = cur._compute(self.env.user.company_id.currency_id,cur,balance)
    
                lines.append(self._get_account_title_line(options, account, amount_currency, debit, credit, balance, has_lines))
    
                total_debit += debit
                total_credit += credit
                total_balance += balance
    
                if has_lines and (unfold_all or is_unfolded):
                    # Initial balance line.
                    account_init_bal = results.get('initial_balance', {})
    
                    cumulated_balance = account_init_bal.get('balance', 0.0) + account_un_earn.get('balance', 0.0)
                    cumulated_balance = cur._compute(self.env.user.company_id.currency_id,cur,account_init_bal.get('balance', 0.0) + account_un_earn.get('balance', 0.0))
                    i1 = cur._compute(self.env.user.company_id.currency_id,cur,account_init_bal.get('amount_currency', 0.0))
                    i2 = cur._compute(self.env.user.company_id.currency_id,cur,account_un_earn.get('amount_currency', 0.0))
                    d1 = cur._compute(self.env.user.company_id.currency_id,cur,account_init_bal.get('debit', 0.0))
                    d2 = cur._compute(self.env.user.company_id.currency_id,cur,account_un_earn.get('debit', 0.0))
                    c1 = cur._compute(self.env.user.company_id.currency_id,cur,account_init_bal.get('credit', 0.0))
                    c2 = cur._compute(self.env.user.company_id.currency_id,cur,account_un_earn.get('credit', 0.0))
    
                    lines.append(self._get_initial_balance_line(
                        options, account,
                        i1 + i2,
                        d1 + d2,
                        c1 + c2,
                        cumulated_balance,
                    ))
    
                    # account.move.line record lines.
                    amls = results.get('lines', [])
    
                    load_more_remaining = len(amls)
                    load_more_counter = self._context.get('print_mode') and load_more_remaining or self.MAX_LINES
    
                    for aml in amls:
                        # Don't show more line than load_more_counter.
                        if load_more_counter == 0:
                            break
    
                        cumulated_balance += aml['balance']
                        lines.append(self._get_aml_line(options, account, aml, company_currency.round(cumulated_balance)))
    
                        load_more_remaining -= 1
                        load_more_counter -= 1
    
                    if load_more_remaining > 0:
                        # Load more line.
                        lines.append(self._get_load_more_line(
                            options, account,
                            self.MAX_LINES,
                            load_more_remaining,
                            cumulated_balance,
                        ))
    
                    # Account total line.
                    lines.append(self._get_account_total_line(
                        options, account,
                        account_sum.get('amount_currency', 0.0),
                        account_sum.get('debit', 0.0),
                        account_sum.get('credit', 0.0),
                        account_sum.get('balance', 0.0),
                    ))
    
            if not line_id:
                # Report total line.
                lines.append(self._get_total_line(
                    options,
                    total_debit,
                    total_credit,
                    company_currency.round(total_balance),
                ))
    
                # Tax Declaration lines.
                journal_options = self._get_options_journals(options)
                if len(journal_options) == 1 and journal_options[0]['type'] in ('sale', 'purchase'):
                    lines += self._get_tax_declaration_lines(
                        options, journal_options[0]['type'], taxes_results
                    )
            return lines
        return super(ReportGeneralLedger, self)._get_general_ledger_lines(options, line_id)
    
    
    @api.model
    def _get_account_total_line(self, options, account, amount_currency, debit, credit, balance):
        if 'curr' in self._context:
            cur = self.env['res.currency'].browse(self._context.get('curr'))
            return {
                'id': 'total_%s' % account.id,
                'class': 'o_account_reports_domain_total',
                'parent_id': 'account_%s' % account.id,
                'name': _('Total'),
                'columns': [
                    {'name': self.format_value(amount_currency, currency=account.currency_id, blank_if_zero=True), 'class': 'number'},
                    {'name': self.format_value(cur._compute(self.env.user.company_id.currency_id,cur,debit),currency=cur), 'class': 'number'},
                    {'name': self.format_value(cur._compute(self.env.user.company_id.currency_id,cur,credit),currency=cur), 'class': 'number'},
                    {'name': self.format_value(cur._compute(self.env.user.company_id.currency_id,cur,balance),currency=cur), 'class': 'number'},
                ],
                'colspan': 4,
            }
        return super(ReportGeneralLedger, self)._get_account_total_line(options, account, amount_currency, debit, credit, balance)
    
    @api.model
    def _get_total_line(self, options, debit, credit, balance):
        if 'curr' in self._context:
            cur = self.env['res.currency'].browse(self._context.get('curr'))
            return {
                'id': 'general_ledger_total_%s' % self.env.company.id,
                'name': _('Total'),
                'class': 'total',
                'level': 1,
                'columns': [
                    {'name': self.format_value(cur._compute(self.env.user.company_id.currency_id,cur,debit),currency=cur), 'class': 'number'},
                    {'name': self.format_value(cur._compute(self.env.user.company_id.currency_id,cur,credit),currency=cur), 'class': 'number'},
                    {'name': self.format_value(cur._compute(self.env.user.company_id.currency_id,cur,balance),currency=cur), 'class': 'number'},
                ],
                'colspan': 5,
                }
        return super(ReportGeneralLedger, self)._get_total_line(options, debit, credit, balance)
    
    @api.model
    def _get_account_title_line(self, options, account, amount_currency, debit, credit, balance, has_lines):
        if 'curr' in self._context:
            cur = self.env['res.currency'].browse(self._context.get('curr'))
            has_foreign_currency = account.currency_id and account.currency_id != account.company_id.currency_id or False
    
            unfold_all = self._context.get('print_mode') and not options.get('unfolded_lines')
    
            name = '%s %s' % (account.code, account.name)
            if len(name) > 40 and not self._context.get('print_mode'):
                name = name[:40] + '...'
            
            return {
                'id': 'account_%d' % account.id,
                'name': name,
                'title_hover': name,
                'columns': [
                    {'name': has_foreign_currency and self.format_value(amount_currency, currency=account.currency_id, blank_if_zero=True) or '', 'class': 'number'},
                    {'name': self.format_value(debit,currency=cur), 'class': 'number'},
                    {'name': self.format_value(credit,currency=cur), 'class': 'number'},
                    {'name': self.format_value(balance,currency=cur), 'class': 'number'},
                ],
                'level': 2,
                'unfoldable': has_lines,
                'unfolded': has_lines and 'account_%d' % account.id in options.get('unfolded_lines') or unfold_all,
                'colspan': 4,
            }
        return super(ReportGeneralLedger, self)._get_account_title_line(options, account, amount_currency, debit, credit, balance, has_lines)
    
    @api.model
    def _get_initial_balance_line(self, options, account, amount_currency, debit, credit, balance):
        if 'curr' in self._context:
            cur = self.env['res.currency'].browse(self._context.get('curr'))
            has_foreign_currency = account.currency_id and account.currency_id != account.company_id.currency_id or False
            return {
                'id': 'initial_%d' % account.id,
                'class': 'o_account_reports_initial_balance',
                'name': _('Initial Balance'),
                'parent_id': 'account_%d' % account.id,
                'columns': [
                    {'name': has_foreign_currency and self.format_value(amount_currency, currency=account.currency_id, blank_if_zero=True) or '', 'class': 'number'},
                    {'name': self.format_value(debit,currency=cur), 'class': 'number'},
                    {'name': self.format_value(credit,currency=cur), 'class': 'number'},
                    {'name': self.format_value(balance,currency=cur), 'class': 'number'},
                ],
                'colspan': 4,
            }
        return super(ReportGeneralLedger, self)._get_initial_balance_line(options, account, amount_currency, debit, credit, balance)
    
    @api.model
    def _get_aml_line(self, options, account, aml, cumulated_balance):
        if 'curr' in self._context:
            cur = self.env['res.currency'].browse(self._context.get('curr'))
            if aml['payment_id']:
                caret_type = 'account.payment'
            elif aml['move_type'] in ('in_refund', 'in_invoice', 'in_receipt'):
                caret_type = 'account.invoice.in'
            elif aml['move_type'] in ('out_refund', 'out_invoice', 'out_receipt'):
                caret_type = 'account.invoice.out'
            else:
                caret_type = 'account.move'
    
            if aml['ref'] and aml['name']:
                title = '%s - %s' % (aml['name'], aml['ref'])
            elif aml['ref']:
                title = aml['ref']
            elif aml['name']:
                title = aml['name']
            else:
                title = ''
    
            if aml['currency_id']:
                currency = self.env['res.currency'].browse(aml['currency_id'])
            else:
                currency = False
    
            return {
                'id': aml['id'],
                'caret_options': caret_type,
                'class': 'top-vertical-align',
                'parent_id': 'account_%d' % aml['account_id'],
                'name': aml['move_name'],
                'columns': [
                    {'name': format_date(self.env, aml['date']), 'class': 'date'},
                    {'name': self._format_aml_name(aml['name'], aml['ref'], aml['move_name']), 'title': title, 'class': 'whitespace_print'},
                    {'name': aml['partner_name'], 'title': aml['partner_name'], 'class': 'whitespace_print'},
                    {'name': currency and self.format_value(aml['amount_currency'], currency=currency, blank_if_zero=True) or '', 'class': 'number'},
                    {'name': self.format_value(cur._compute(self.env.user.company_id.currency_id,cur,aml['debit']), currency=cur, blank_if_zero=True), 'class': 'number'},
                    {'name': self.format_value(cur._compute(self.env.user.company_id.currency_id,cur,aml['credit']), currency=cur, blank_if_zero=True), 'class': 'number'},
                    {'name': self.format_value(cur._compute(self.env.user.company_id.currency_id,cur,cumulated_balance), currency=cur), 'class': 'number'},
                ],
                'level': 4,
            }
        return super(ReportGeneralLedger, self)._get_aml_line(options, account, aml, cumulated_balance)
    
    def get_pdf(self, options, minimal_layout=True):
        for opt in options['currenciess']:
            if opt['selected'] and self.env['res.currency'].browse(opt['id']) != self.env.user.company_id.currency_id:
                return super(ReportGeneralLedger, self.with_context(curr = opt['id'])).get_pdf(options,minimal_layout)
        return super(ReportGeneralLedger, self).get_pdf(options,minimal_layout)
    
    def get_xlsx(self, options, response=None):
        for opt in options['currenciess']:
            if opt['selected'] and self.env['res.currency'].browse(opt['id']) != self.env.user.company_id.currency_id:
                return super(ReportGeneralLedger, self.with_context(curr = opt['id'])).get_xlsx(options,response)
        return super(ReportGeneralLedger, self).get_xlsx(options,response)

   