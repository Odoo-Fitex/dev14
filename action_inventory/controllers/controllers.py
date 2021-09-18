# -*- coding: utf-8 -*-
# from odoo import http


# class ActionPayroll(http.Controller):
#     @http.route('/action_payroll/action_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/action_payroll/action_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('action_payroll.listing', {
#             'root': '/action_payroll/action_payroll',
#             'objects': http.request.env['action_payroll.action_payroll'].search([]),
#         })

#     @http.route('/action_payroll/action_payroll/objects/<model("action_payroll.action_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('action_payroll.object', {
#             'object': obj
#         })
