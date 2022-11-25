# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import json
from odoo.modules.module import get_resource_path
from odoo.tools import ormcache
from .anita_utility import split_module_and_path
from odoo.tools.config import config


class AnitaModeTemplate(models.Model):
    '''
    user theme style setting
    '''
    _name = 'anita_theme_setting.mode_template'
    _description = 'Anita Mode Template'

    name = fields.Char(string="Name", required=True)
    template = fields.Text(string="Template")
    color_vars = fields.Text(string="Color Vars", help="This is the default var values for this template")
    template_path = fields.Char(string="Template Path", help="This is the template path of the template")

    _sql_constraints = [('name_unique', 'UNIQUE(name)', "Name Must Be Unique!")]

    @ormcache()
    def get_templates(self):
        """
        get templates
        :return:
        """
        records = self.search([])
        return {record.name: record for record in records}

    @ormcache('self.id')
    def get_template(self):
        """
        get template
        :return:
        """
        return json.loads(self.template)

    def get_color_vars(self):
        """
        get vars
        :return:
        """
        return json.loads(self.color_vars)

    def refresh_templates(self):
        """
        update template content
        """
        records = self.search([])
        for record in records:
            if record.template_path:
                module, file_path = split_module_and_path(record.template_path)
                tmp_path = get_resource_path(module, file_path)
                with open(tmp_path, 'r') as fd:
                    template = fd.read()
                    record.template = template
        self.clear_caches()

    def _register_hook(self):
        """ 
        stuff to do right after the registry is built 
        """
        records = self.search([])
        if config.get('debug', False):
            records.refresh_templates()

    @api.model
    def install_template(self, name, template_path, theme_mode_paths):
        """
        install mode
        :return:
        """
        module, file_path = split_module_and_path(template_path)
        if not module:
            raise exceptions.ValidationError("Template Path is not valid!")
        
        tmp_path = get_resource_path(module, file_path)
        if not tmp_path:
            raise exceptions.ValidationError("Template Path is not valid!")

        with open(tmp_path, 'r') as fd:
            template = fd.read()
            if not name:
                raise exceptions.ValidationError(
                    'Template {template} must has a name!'.format(template=template_path))

            template_record = self.search([('name', '=', name)])
            if not template_record:
                self.create([{
                    "name": name,
                    "template": template,
                    "template_path": template_path
                }])
            else:
                template_record.write({
                    "name": name,
                    "template": template,
                    "template_path": template_path
                })

            for index, mode_path in enumerate(theme_mode_paths):
                record = self.env['anita_theme_setting.default_mode_data'].install_mode(
                    mode_path, template_record)
                if index == 0:
                    template_record.write({
                        "color_vars": record.template_var_vals
                    })
