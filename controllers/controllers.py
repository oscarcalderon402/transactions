# -*- coding: utf-8 -*-
# from odoo import http


# class Transations(http.Controller):
#     @http.route('/transations/transations/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/transations/transations/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('transations.listing', {
#             'root': '/transations/transations',
#             'objects': http.request.env['transations.transations'].search([]),
#         })

#     @http.route('/transations/transations/objects/<model("transations.transations"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('transations.object', {
#             'object': obj
#         })
