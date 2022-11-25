# -*- coding: utf-8 -*-

from statistics import mode
from odoo import models, fields, api, exceptions
from odoo.tools import ormcache
import json
from odoo.modules.module import get_resource_path
from .anita_utility import split_module_and_path

import logging
_logger = logging.getLogger(__name__)


class AnitaDefaultMode(models.Model):
    '''
    default mode
    '''
    _name = 'anita_theme_setting.default_mode_data'
    _description = 'Anita Theme Setting Mode Template'

    name = fields.Char(string="Name", required=True)
    data = fields.Text(string="Content", required=True)
    template_var_vals = fields.Text(string="Template Var Vals")
    version = fields.Char(string="Version", required=True)
    config_path = fields.Char(string="Config Path", help="This is the file path of the template")

    _sql_constraints = [('name_unique', 'UNIQUE(name)', "Name Must Be Unique!")]

    @ormcache('self.id')
    def get_mode_data(self):
        """
        get mode
        :return:
        """
        self.ensure_one()
        mode_data = json.loads(self.data)
        mode_data.update({
            "name": self.name,
            "version": self.version
        })
        return mode_data

    @ormcache('self.id')
    def get_var_val_cache(self):
        """
        get var value cache
        """
        self.ensure_one()
        var_vals = self.template_var_vals
        var_vals = var_vals.replace('\'', '\"')
        data = json.loads(var_vals)
        var_val_cache = {}
        for group_name in data:
            group = data[group_name]
            for var_item in group:
                var_val_cache[var_item['name']] = var_item['value']
        return var_val_cache

    @ormcache()
    def get_default_modes(self):
        """
        get default modes
        :return:
        """
        records = self.search([])
        default_models = []
        for record in records:
            default_models.append(record.get_mode_data())
        return default_models

    @api.model
    def refresh_default_mode(self):
        """
        udpate data
        """
        records = self.search([])
        for record in records:
            if not record.config_path:
                return

            module, file_path = split_module_and_path(record.config_path)
            tmp_path = get_resource_path(module, file_path)
            if not tmp_path:
                continue    
            with open(tmp_path, 'r') as fd:
                mode_text = fd.read()

                # check the data is valid json
                try:
                    mode_data = json.loads(mode_text)
                    record.write({
                        "data": json.dumps(mode_data),
                        "template_var_vals": json.dumps(mode_data.get('template_var_vals', {}))
                        })
                except Exception as e:
                    self.data = False
                    _logger.error(e)

        self.clear_caches()

    @api.model
    def install_mode(self, config_path, template):
        """
        install mode
        :return:
        """
        module, file_path = split_module_and_path(config_path)
        tmp_path = get_resource_path(module, file_path)
        if not tmp_path:
            raise exceptions.ValidationError('File not found! {}'.format(config_path))
        
        with open(tmp_path, 'r') as fd:

            mode_text = fd.read()

            # check the data is valid json
            try:
                mode_data = json.loads(mode_text)
            except Exception as e:
                raise exceptions.ValidationError(
                    'Template {template} must be a valid json file!'.format(template=config_path))

            name = mode_data.get('name')
            if not name:
                raise exceptions.ValidationError(
                    'Template {template} must has a name!'.format(template=config_path))

            model_record = self.search([('name', '=', name)])
            if not model_record:
                self.create([{
                    "name": name,
                    "data": json.dumps(mode_data),
                    "version": mode_data.get('version', '1.0'),
                    "config_path": config_path,
                    "template_var_vals": mode_data.get("template_var_vals", "")
                }])
            else:
                model_record.write({
                    "name": name,
                    "data": json.dumps(mode_data),
                    "version": mode_data.get('version', '1.0'),
                    "config_path": config_path,
                    "template_var_vals": mode_data.get("template_var_vals", "")
                })
            return model_record
