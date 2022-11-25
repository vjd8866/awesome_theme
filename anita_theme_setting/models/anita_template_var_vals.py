# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import json
from odoo.modules.module import get_resource_path
from odoo.tools import ormcache


class AnitaTemplateVarVal(models.Model):
    '''
    user theme style setting
    '''
    _name = 'anita_theme_setting.template_var_val'
    _description = 'Anita Mode Template'

    theme_mode = fields.Many2one(string="Theme Mode", comodel_name="anita_theme_setting.theme_mode")
    name = fields.Char(string="Name", required=True)
    group = fields.Char(string="Group", required=True)
    value = fields.Char(string="Value", required=True)
    disable_opacity = fields.Boolean(string="Disable Opacity", default=False)
    description = fields.Char(string="Description")

