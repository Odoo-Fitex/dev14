# -*- coding: utf-8 -*-
# from odoo import http


# class AttendenceAddedFields(http.Controller):
#     @http.route('/attendence_added_fields/attendence_added_fields/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/attendence_added_fields/attendence_added_fields/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('attendence_added_fields.listing', {
#             'root': '/attendence_added_fields/attendence_added_fields',
#             'objects': http.request.env['attendence_added_fields.attendence_added_fields'].search([]),
#         })

#     @http.route('/attendence_added_fields/attendence_added_fields/objects/<model("attendence_added_fields.attendence_added_fields"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('attendence_added_fields.object', {
#             'object': obj
#         })
