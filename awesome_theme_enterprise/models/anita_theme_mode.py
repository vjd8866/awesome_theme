# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import json
import re
from odoo.tools.config import config

try:
    import sass as libsass
except ImportError:
    libsass = None


class AnitaThemeMode(models.Model):
    '''
    user theme style setting
    '''
    _inherit = 'anita_theme_setting.theme_mode'
    _description = 'anita theme mode'

    def _compile_scss(self):
        """
        This code will compile valid scss into css.
        Simply copied and adapted slightly
        """
        debug = config.get('debug', False)
        if debug:
            # odoo get resource path
            from odoo.modules.module import get_resource_path
            tmp_path = get_resource_path(
                'awesome_theme_enterprise', 'static', 'template', 'template1.scss')
            # read the file content
            with open(tmp_path, 'r') as f:
                template = f.read()
        else:
            template = self.mode_template.template

        scss_source = template.strip()
        mode_name = "body.{name}".format(name=self.name)
        scss_source = scss_source.replace('body.__mode_name__', mode_name)
        scss_source = scss_source.replace(
            'body.$mode_name', "body.{name}".format(name=self.name))
        if not scss_source:
            return ""

        template_vars = json.loads(self.template_vars or "{}")
        for name, value in template_vars.items():
            scss_source = scss_source.replace(name, value)

        precision = 8
        output_style = 'expanded'

        from odoo.modules.module import get_resource_path

        bootstrap_scss_path = get_resource_path('web', 'static', 'lib', 'bootstrap', 'scss')
        awsome_mixins = get_resource_path('anita_theme_base', 'static', 'css')

        try:
            result = libsass.compile(
                string=scss_source,
                include_paths=[bootstrap_scss_path, awsome_mixins],
                output_style=output_style,
                precision=precision)
            index = result.find(mode_name)
            result = result[index:]
            return result
        except libsass.CompileError as e:
            raise libsass.CompileError(e.args[0])