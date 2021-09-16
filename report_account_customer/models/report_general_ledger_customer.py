# -*- coding: utf-8 -*-


from odoo import _, api, fields, models


class GeneralLedgerAccount(models.AbstractModel):
    _name = 'report.report_account_customer.report_customer'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet('General Ledger Report')
            format0 = workbook.add_format({'font_size': 15, 'align': 'center'})
            format1 = workbook.add_format(
                {'font_size': 15, 'align': 'center', 'bold': True, 'bg_color': '#D5D5D5', 'color': 'black',
                 'border': 2})
            format2 = workbook.add_format(
                {'font_size': 13, 'align': 'center', 'bold': True,
                 'border': 1})
            format10 = workbook.add_format({'align': 'center', 'bold': True, 'bg_color': '#FF6600', 'border': 5})
            format3 = workbook.add_format(
                {'align': 'center', 'bold': True, 'bg_color': '#4CE400', 'color': 'black', 'border': 5})
            row = 1
            if obj.partner_ids:
                print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                for partner in obj.partner_ids:
                    balance = 0
                    total_debit = 0
                    total_credit = 0
                    sheet.merge_range(row, 2, row, 6, partner.name, format3)
                    row += 3
                    sheet.write(row, 2, 'FROM : ' + str(obj.date_from), format0)
                    sheet.write(row, 5, 'TO : ' + str(obj.date_to), format0)
                    row += 3
                    sheet.write(row, 1, 'Date', format3)
                    sheet.set_column(row, 1, 30)
                    sheet.set_row(row, 20)
                    sheet.write(row, 2, 'Entry', format3)
                    sheet.write(row, 3, 'Reference', format3)
                    sheet.write(row, 4, 'Description', format3)
                    sheet.write(row, 5, 'Debit', format3)
                    sheet.write(row, 6, 'Credit', format3)
                    sheet.write(row, 7, 'Balance', format3)
                    sheet.set_column(row, 7, 5)
                    account_move_lines = self.env['account.move.line'].search([
                        ('date', '>=', obj.date_from),
                        ('date', '<=', obj.date_to),
                        ('partner_id', '=', partner.id),
                        ('move_id.state', '=', 'posted'),
                        ('account_id.user_type_id', 'in', [self.env.ref('account.data_account_type_receivable').id,
                                                           self.env.ref('account.data_account_type_payable').id]),
                    ], order="date")
                    account_move_lines_balance = self.env['account.move.line'].search([
                        ('date', '<=', obj.date_from),
                        ('partner_id', '=', partner.id),
                        ('move_id.state', '=', 'posted'),
                        ('account_id.user_type_id', 'in', [self.env.ref('account.data_account_type_receivable').id,
                                                          self.env.ref('account.data_account_type_payable').id]),
                    ], order="date")
                    for move_balance in account_move_lines_balance:
                        balance = balance + move_balance.debit - move_balance.credit

                    row += 1
                    sheet.write(row, 3, "Initial balance", format2)
                    sheet.write(row, 7, balance, format2)
                    row += 1

                    for move in account_move_lines:
                        if True:
                            total_credit += move.credit
                            total_debit += move.debit
                            balance = balance + move.debit - move.credit
                            sheet.write(row, 1, str(move.date), format1)
                            sheet.set_column(row, 1, 30)
                            sheet.write(row, 2, move.move_id.name, format1)
                            sheet.write(row, 3, move.ref or "", format1)
                            sheet.write(row, 4, move.name or "", format1)
                            sheet.write(row, 5, move.debit, format1)
                            sheet.write(row, 6, move.credit, format1)
                            sheet.write(row, 7, balance, format1)
                            row += 1
                            account_invoice = self.env['account.move'].sudo().search(
                                [('id', '=', move.move_id.id), ('state', '=', 'posted'), ], limit=1)
                            if account_invoice:
                                if account_invoice.invoice_line_ids.product_id:
                                    print('account_invoice.invoice_line_ids', account_invoice.invoice_line_ids)
                                    # if 'INV' in move.move_id.name:
                                    #     account_invoice=self.env['account.invoice'].sudo().search([('number','=',move.move_id.name)],limit=1)
                                    #     account_invoice = self.env['account.invoice'].sudo().search([('move_id', '=', move.move_id.id)], limit=1)
                                    sheet.write(row, 1, "product", format2)
                                    sheet.set_column(row, 1, 40)
                                    sheet.write(row, 2, 'QTY', format2)
                                    sheet.write(row, 3, 'Price', format2)
                                    sheet.write(row, 4, 'Amount', format2)
                                    row += 1
                                    for line in account_invoice.invoice_line_ids:
                                        sheet.write(row, 1, line.product_id.name, format2)
                                        sheet.write(row, 2, line.quantity, format2)
                                        sheet.write(row, 3, line.price_unit, format2)
                                        sheet.write(row, 4, line.price_subtotal, format2)
                                        row += 1
                            # elif 'INV' not in move.move_id.name:
                            elif move.payment_id:
                                if move.payment_id.payment_check_lines:
                                    sheet.write(row, 1, "Check Number", format1)
                                    sheet.set_column(row, 1, 40)
                                    sheet.write(row, 2, 'Check Date', format1)
                                    sheet.write(row, 3, 'Check Amount', format1)
                                    sheet.write(row, 4, 'Check Bank', format1)
                                    # sheet.write(row, 5, 'Drawer Name', format1)
                                    row += 1
                                    for check in move.payment_id.payment_check_lines:
                                        sheet.write(row, 1, check.check_number, format2)
                                        sheet.write(row, 2, str(check.check_date), format2)
                                        sheet.write(row, 3, check.check_amount, format2)
                                        sheet.write(row, 4, check.check_bank_id.name, format2)
                                        # sheet.write(row, 5, check.with_drawer_name, format2)
                                        row += 1
                                row += 1

                    sheet.write(row, 5, total_debit, format3)
                    sheet.write(row, 6, total_credit, format3)
                    sheet.write(row, 7, balance, format3)

                    row += 7
