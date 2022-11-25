# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class awesome_theme_studio_patch(models.Model):
#     _name = 'awesome_theme_studio_patch.awesome_theme_studio_patch'
#     _description = 'awesome_theme_studio_patch.awesome_theme_studio_patch'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
