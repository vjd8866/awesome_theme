# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AnitaBkImageWizard(models.TransientModel):
    '''
    Model Project
    '''
    _name = 'anita_theme_setting.background_image_wizard'
    _description = 'background image wizard'

    data = fields.Binary(string='data', required=True)
    opacity = fields.Float(string='theme opacity', default=0.8)
