# -*- coding: utf-8 -*-
# from odoo import http


# class AwesomeThemeStudioPatch(http.Controller):
#     @http.route('/awesome_theme_studio_patch/awesome_theme_studio_patch', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/awesome_theme_studio_patch/awesome_theme_studio_patch/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('awesome_theme_studio_patch.listing', {
#             'root': '/awesome_theme_studio_patch/awesome_theme_studio_patch',
#             'objects': http.request.env['awesome_theme_studio_patch.awesome_theme_studio_patch'].search([]),
#         })

#     @http.route('/awesome_theme_studio_patch/awesome_theme_studio_patch/objects/<model("awesome_theme_studio_patch.awesome_theme_studio_patch"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('awesome_theme_studio_patch.object', {
#             'object': obj
#         })
