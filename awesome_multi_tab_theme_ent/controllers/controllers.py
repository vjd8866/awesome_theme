# -*- coding: utf-8 -*-
# from odoo import http


# class AwesomeMultiTabThemeEnt(http.Controller):
#     @http.route('/awesome_multi_tab_theme_ent/awesome_multi_tab_theme_ent', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/awesome_multi_tab_theme_ent/awesome_multi_tab_theme_ent/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('awesome_multi_tab_theme_ent.listing', {
#             'root': '/awesome_multi_tab_theme_ent/awesome_multi_tab_theme_ent',
#             'objects': http.request.env['awesome_multi_tab_theme_ent.awesome_multi_tab_theme_ent'].search([]),
#         })

#     @http.route('/awesome_multi_tab_theme_ent/awesome_multi_tab_theme_ent/objects/<model("awesome_multi_tab_theme_ent.awesome_multi_tab_theme_ent"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('awesome_multi_tab_theme_ent.object', {
#             'object': obj
#         })
