# -*- coding: utf-8 -*-
# from odoo import http


# class MrpDyingBomLine(http.Controller):
#     @http.route('/mrp_dying_bom_line/mrp_dying_bom_line/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_dying_bom_line/mrp_dying_bom_line/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_dying_bom_line.listing', {
#             'root': '/mrp_dying_bom_line/mrp_dying_bom_line',
#             'objects': http.request.env['mrp_dying_bom_line.mrp_dying_bom_line'].search([]),
#         })

#     @http.route('/mrp_dying_bom_line/mrp_dying_bom_line/objects/<model("mrp_dying_bom_line.mrp_dying_bom_line"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_dying_bom_line.object', {
#             'object': obj
#         })
