# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.modules.module import get_resource_path
import base64
from .anita_utility import split_module_and_path


class AnitaThemeSettingBackgroundImage(models.Model):
    '''
    Model Project
    '''
    _name = 'anita_theme_setting.background_image'
    _description = 'background image'

    data = fields.Image(string='data')
    opacity = fields.Float(string='theme opacity', default=0.8)

    def get_image_url(self):
        """
        get image url
        """
        image_url = 'web/image/anita_theme_setting.background_image/' + str(self.id) + '/data'
        return image_url
