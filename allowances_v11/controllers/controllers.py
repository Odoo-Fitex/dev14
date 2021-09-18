# -*- coding: utf-8 -*-
from odoo import http

# class AllowancesV11(http.Controller):
#     @http.route('/allowances_v11/allowances_v11/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/allowances_v11/allowances_v11/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('allowances_v11.listing', {
#             'root': '/allowances_v11/allowances_v11',
#             'objects': http.request.env['allowances_v11.allowances_v11'].search([]),
#         })

#     @http.route('/allowances_v11/allowances_v11/objects/<model("allowances_v11.allowances_v11"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('allowances_v11.object', {
#             'object': obj
#         })