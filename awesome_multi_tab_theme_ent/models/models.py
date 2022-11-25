# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class awesome_multi_tab_theme_ent(models.Model):
#     _name = 'awesome_multi_tab_theme_ent.awesome_multi_tab_theme_ent'
#     _description = 'awesome_multi_tab_theme_ent.awesome_multi_tab_theme_ent'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
