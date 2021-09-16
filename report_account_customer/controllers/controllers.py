# -*- coding: utf-8 -*-
# from odoo import http


# class ReportAccountCustomer(http.Controller):
#     @http.route('/report_account_customer/report_account_customer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_account_customer/report_account_customer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_account_customer.listing', {
#             'root': '/report_account_customer/report_account_customer',
#             'objects': http.request.env['report_account_customer.report_account_customer'].search([]),
#         })

#     @http.route('/report_account_customer/report_account_customer/objects/<model("report_account_customer.report_account_customer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_account_customer.object', {
#             'object': obj
#         })
