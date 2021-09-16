# -*- coding: utf-8 -*-
# from odoo import http


# class EditOperationReadonly(http.Controller):
#     @http.route('/edit_operation_readonly/edit_operation_readonly/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/edit_operation_readonly/edit_operation_readonly/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('edit_operation_readonly.listing', {
#             'root': '/edit_operation_readonly/edit_operation_readonly',
#             'objects': http.request.env['edit_operation_readonly.edit_operation_readonly'].search([]),
#         })

#     @http.route('/edit_operation_readonly/edit_operation_readonly/objects/<model("edit_operation_readonly.edit_operation_readonly"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('edit_operation_readonly.object', {
#             'object': obj
#         })
