# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, tools
import json
import re
from odoo.tools.config import config
from odoo.modules.module import get_resource_path
from .anita_utility import apply_alpha

try:
    import sass as libsass
except ImportError:
    libsass = None

import logging
_logger = logging.getLogger(__name__)


class AnitaThemeMode(models.Model):
    '''
    user theme style setting
    '''
    _name = 'anita_theme_setting.theme_mode'
    _description = 'anita theme mode'

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Mode Sequence", default=0)

    theme_styles = fields.One2many(
        string="Theme Styles",
        comodel_name="anita_theme_setting.theme_style",
        inverse_name="theme_mode")

    mode_template = fields.Many2one(
        comodel_name="anita_theme_setting.mode_template",
        string="Mode Template")

    template_var_vals = fields.One2many(
        comodel_name="anita_theme_setting.template_var_val",
        inverse_name="theme_mode",
        string="Template Vars")

    # if owner is False, so the style own to global
    owner = fields.Reference(
        string="Owner",
        selection=[('res.company', 'res.company'),
                   ('res.users', 'res.users')],
        default=False,
        help="owner which this theme is create by, if it is false, it mean it is owned to the system!")
    mode_style_css = fields.Text(string="Mode Style Css")
    compiled_mode_style_css = fields.Text(string="Compiled mode style css")

    is_default = fields.Boolean(string="Is Default", default=False)
    version = fields.Char(
        string="Version", help="use version to check update or not")

    _sql_constraints = [('theme_mode_name_unique', 'UNIQUE(name, owner)',
                         "Theme mode name and owner must unique")]

    def get_mode_preview_data(self, style_id=False):
        """
        get mode preview data
        :return:
        """
        if self.mode_template:
            if style_id:
                theme_style = self.env['anita_theme_setting.theme_style'].browse(
                    style_id)
                if theme_style.is_semi_transparent():
                    result = theme_style.get_mode_style_css()
                else:
                    result = self.get_mode_style_css()
            else:
                result = self.get_mode_style_css()
        else:
            result = ""
        
        mode_name = 'body.{name}'.format(name=self.name)
        # replace mode_name with body.preview
        result = result.replace(mode_name, 'body.preview')
        return result

    @api.onchange('mode_template')
    def on_mode_template_changed(self):
        """
        compute mode style
        :return:
        """
        # check id is instance of NewId
        if self.mode_template:
            scss_vars = self.mode_template.get_color_vars()
            template_var_vals = [(5, 0, 0)]
            for group_name in scss_vars:
                var_items = scss_vars[group_name]
                for var_item in var_items:
                    template_var_vals.append((0, 0, {
                        "name": var_item["name"],
                        "group": group_name,
                        "value": var_item["value"],
                        "disable_opacity": var_item.get("disable_opacity", False),
                        "description": var_item["description"]
                    }))
            self.template_var_vals = template_var_vals
        else:
            self.template_var_vals = [(5, 0, 0)]

    def check_template_vars(self):
        """
        check style css
        :return:
        """
        template = self.mode_template.template
        if not template:
            self.mode_template.refresh_templates()
            template = self.mode_template.template
            
        if not template:
            return False

        self.compiled_mode_style_css = self._compile_scss()
        tmp_re = re.compile(r'\$[\d\w_-]+color')
        var_cache = self.get_scss_var_record_cache()
        results = tmp_re.findall(template)
        for result in results:
            # check if start with _
            if result.startswith('$_'):
                # replace with $
                result = result.replace('$_', '$')
            if result not in var_cache:
                # give a chance to refresh the cache
                self.mode_template.template = False
                # raise exceptions.ValidationError(
                #     '{tmp_var} not in vars!'.format(tmp_var=result))
                
    @tools.ormcache('self.id')
    def get_scss_vars_cache(self):
        """
        get scss vars
        :return:
        """
        records = self.template_var_vals.read(['name', 'value'])
        return {record['name']: record['value'] for record in records}

    @tools.ormcache('self.id')
    def get_scss_var_record_cache(self):
        """
        get scss vars
        :return:
        """
        records = self.template_var_vals
        return {record.name: {
            "name": record.name,
            "value": record.value,
            "disable_opacity": record.disable_opacity,
        } for record in records}

    def _compile_scss(self, alpha=False):
        """
        This code will compile valid scss into css.
        Simply copied and adapted slightly
        """
        self.ensure_one()
        scss_source = self.mode_template.template

        scss_vars = []
        var_val_cache = self.get_scss_var_record_cache()
        for var_name in var_val_cache:
            var_record = var_val_cache[var_name]
            name = var_record.get("name")
            if alpha and alpha < 1:
                color = apply_alpha(var_record.get('name'), var_record.get('value'), alpha)
            else:
                color = var_record.get('value')
            # new color
            scss_vars.append('{name}: {value};'.format(
                name=name, value=color))
            # origin color, some element disable alpha
            scss_vars.append('{name}: {value};'.format(
                name=name.replace('$', '$_'), value=var_record.get('value')))

        precision = 8
        output_style = 'expanded'

        bootstrap_scss_path = get_resource_path('web', 'static', 'lib', 'bootstrap', 'scss')
        mixins = get_resource_path('anita_theme_base', 'static', 'css')

        mode_selectors = "$mode_selectors: 'body.{name}';".format(name=self.name)
        extra_vars = [
            mode_selectors,
            "$compile_normal: 1;",
            "$semi_transparent: {semi_trans};".format(semi_trans=True if alpha < 1.0 else False),
        ]

        total_vars = extra_vars + scss_vars
        normal_source = '\n'.join(total_vars) + '\n' + scss_source if scss_source else ''

        # compile normal
        results = []
        try:
            result = libsass.compile(
                string=normal_source,
                include_paths=[bootstrap_scss_path, mixins],
                output_style=output_style,
                precision=precision)
            # remove the import bootstrap
            index = result.find("body.{name}".format(name=self.name))
            result = result[index:]
            results.append(result)
        except libsass.CompileError as e:
            _logger.error(e.args[0])

        # compile for background
        if alpha < 1.0:
            scss_vars = []
            for var_name in var_val_cache:
                var_record = var_val_cache[var_name]
                name = var_record.get("name")
                # new color
                scss_vars.append('{name}: {value};'.format(name=name, value=var_record.get('value')))
                # origin color
                scss_vars.append('{name}: {value};'.format(name=name.replace('$', '$_'), value=var_record.get('value')))

            mode_selectors = "$mode_selectors: 'body.{name} .o_dialog_container';".format(name=self.name)
            extra_vars = [
                mode_selectors,
                "$compile_normal: 0;",
                "$semi_transparent: {semi_trans};".format(semi_trans=1 if alpha < 1.0 else 0),
            ]
            total_vars = extra_vars + scss_vars
            normal_source = '\n'.join(total_vars) + '\n' +  str(scss_source)
            try:
                result = libsass.compile(
                    string=normal_source,
                    include_paths=[bootstrap_scss_path, mixins],
                    output_style=output_style,
                    precision=precision)
                # remove the import bottstrap
                index = result.find('body.{name} .o_dialog_container'.format(name=self.name))
                result = result[index:]
                results.append(result)
            except libsass.CompileError as e:
                _logger.error(e.args[0])
        
        return '\n'.join(results)
        
    @api.model
    def compute_mode_style_url(self):
        """
        compute mode style url
        :return:
        """
        for record in self:
            record.mode_style_url = \
                '/web/image/anita_theme_setting.anita_theme_setting/{var_id}/icon128x128'.format(
                    var_id=record.id)

    def get_default_mode_style_text(self, theme_mode_info):
        """
        get default mode data
        :return:
        """
        if self.name == 'normal':
            return

        color_vars = theme_mode_info["template_vars"]
        mode_template = theme_mode_info["mode_template"]
        if not mode_template:
            raise exceptions.ValidationError('Can not find the theme template!')

        template = mode_template.template
        # css template data
        template = template.replace('$mode_name', self.name)

        # replace the var
        for var_nam in color_vars:
            template = str(template).replace(var_nam, color_vars[var_nam])

        return template

    @api.model
    def check_default_mode_data(self, owner=False, force = False):
        '''
        check default mode data
        :return:
        '''
        modes = self.search([('owner', '=', owner)])
        olde_mode_cache = {mode.name: mode for mode in modes}

        default_modes = \
            self.env["anita_theme_setting.default_mode_data"].search([])

        # create new mode if the mode do not exits
        for default_mode in default_modes:
                
            if not default_mode.data:
                continue

            # need to reload the mode data
            mode_data = default_mode.get_mode_data()
            if default_mode.name not in olde_mode_cache:
                mode_data["name"] = default_mode["name"]

                # create new mode use the mode data
                record = self.create_mode(mode_data, owner)
                if not record.mode_template:
                    continue

                # check the templates
                templates = self.env["anita_theme_setting.mode_template"].get_templates(
                )
                template = mode_data.get('mode_template', False)
                if template and template not in templates:
                    raise exceptions.ValidationError(
                        '{template} do not exits!'.format(template=mode_data["template"]))

                template = templates[mode_data["mode_template"]]
                record.mode_template = template.id

                # check vars are defined in the template vars
                record.check_template_vars()
            else:
                # check version, if the version is different
                mode = olde_mode_cache[default_mode.name]
                if force or mode.version != mode_data["version"]:
                    # update template vars
                    temlate_var_vals = mode_data["template_var_vals"]
                    mode.update_template_var_values(temlate_var_vals)
                    # update template
                    mode_templates = self.env["anita_theme_setting.mode_template"].get_templates(
                    )
                    if mode_data.get("mode_template", False):
                        template_name = mode_data["mode_template"]
                        mode.mode_template = \
                            mode_templates.get(template_name, False)
                    mode.version = mode_data["version"]
                    mode.check_mode_data()
                    # recompile the template
                    mode.compiled_mode_style_css = False

        # unlink the invalid mode
        for default_mode in default_modes:
            if not default_mode.data:
                default_mode.unlink()

    def create_mode(self, mode_config, owner=False, is_default=True):
        '''
        create mode
        :param mode style txt:
        :param mode_data:
        :param owner:
        :param is_default:
        :return:
        '''
        mode_templates = \
            self.env["anita_theme_setting.mode_template"].get_templates()
        mode_template = mode_config.get('mode_template', False)
        if mode_template and mode_template not in mode_templates:
            raise exceptions.ValidationError('Can not find mode template {mode_template}'.format(
                mode_template=mode_template))

        # convert to cache data
        template_var_vals = mode_config.get('template_var_vals', {})
        var_val_cache = {}
        for group in template_var_vals:
            var_items = template_var_vals[group]
            for var_item in var_items:
                var_val_cache[var_item["name"]] = var_item["value"]

        theme_styles = mode_config['theme_styles']
        theme_style_array = []
        for theme_style in theme_styles:
            groups = theme_style["groups"]
            group_datas = []
            for group_index, var_items in enumerate(groups):
                sub_groups = var_items["sub_groups"]
                sub_group_array = []
                for sub_group_index, sub_group in enumerate(sub_groups):
                    # create sub group
                    item_array = []
                    style_items = sub_group["style_items"]
                    for item_index, style_item in enumerate(style_items):
                        var_val_array = []
                        var_infos = style_item["vars"]
                        for var_index, var_info in enumerate(var_infos):
                            color = var_info.get("color", False)
                            ref_var = var_info.get("ref_var", False)
                            if ref_var:
                                if ref_var not in var_val_cache:
                                    color = False
                                    _logger.info(
                                        "Can not find ref var {ref_var}".format(ref_var=ref_var))
                                else:
                                    color = var_val_cache[ref_var]

                            var_val_array.append((0, 0, {
                                "name": var_info["name"],
                                "type": var_info["type"],
                                "sequence": var_index,
                                "is_default": is_default,
                                "color": color,
                                "image": var_info.get('image', False),
                                "image_url": var_info.get('image_url', False),
                                "svg": var_info.get('svg', False),
                                "identity": var_info.get('identity', False)
                            }))

                        item_array.append((0, 0, {
                            "name": style_item["name"],
                            "is_default": is_default,
                            "sequence": item_index,
                            "val_template": style_item["val_template"],
                            "sub_group": sub_group["name"],
                            "vars": var_val_array,
                            "selectors": json.dumps(style_item["selectors"])
                        }))

                    sub_group_array.append((0, 0, {
                        "name": sub_group["name"],
                        "sequence": sub_group_index,
                        "style_items": item_array,
                        "is_default": is_default
                    }))

                group_datas.append((0, 0, {
                    "name": var_items["name"],
                    "sequence": group_index,
                    "is_default": is_default,
                    "sub_groups": sub_group_array
                }))

            theme_style_array.append((0, 0, {
                "name": theme_style["name"],
                "is_default": is_default,
                "groups": group_datas
            }))

        vals = []
        template_var_vals = mode_config.get('template_var_vals', {})
        for group_name in template_var_vals:
            var_items = template_var_vals[group_name]
            for var_item in var_items:
                vals.append((0, 0, {
                    "name": var_item["name"],
                    "group": group_name,
                    "value": var_item["value"],
                    "disable_opacity": var_item.get("disable_opacity", False),
                    "description": var_item["description"]
                }))

        mode_template = mode_config.get("mode_template", False)
        return self.env["anita_theme_setting.theme_mode"].create([{
            "name": mode_config["name"],
            "theme_styles": theme_style_array,
            "is_default": is_default,
            "version": mode_config["version"],
            "mode_template": mode_templates[mode_template].id if mode_template else False,
            "owner": owner,
            "template_var_vals": vals
        }])

    def get_mode_data(self):
        '''
        get the mode data
        :return:
        '''
        self.ensure_theme_style()
        rst = []
        for record in self:
            tmp_data = record.read(
                ['name', 'is_default', 'sequence', 'version'])[0]
            tmp_data['theme_styles'] = record.theme_styles.get_styles()
            rst.append(tmp_data)
        return rst

    def delete_mode(self):
        """
        delete the mode
        :return:
        """
        self.unlink()

    def check_style_css(self):
        """
        check style css
        :return:
        """
        if self.mode_template and not self.compiled_mode_style_css:
            self.compiled_mode_style_css = self._compile_scss()

    def update_template_var_values(self, template_var_vals):
        """
        update template var values
        :param temlate_var_vals:
        :return:
        """
        self.ensure_one()
        vals = [(5, 0, 0)]
        for group_name in template_var_vals:
            var_items = template_var_vals[group_name]
            for var_item in var_items:
                vals.append((0, 0, {
                    "name": var_item["name"],
                    "group": group_name,
                    "value": var_item["value"],
                    "description": var_item.get("description")
                }))
        self.template_var_vals = vals

    def get_mode_style_css(self):
        """
        get mode style css
        """
        if config.get('debug', False) or not self.compiled_mode_style_css:
            self.compiled_mode_style_css = self._compile_scss()
            
        return self.compiled_mode_style_css
        
    def check_mode_data(self):
        '''
        check the mode data
        :return:
        '''
        self.ensure_one()

        default_modes = self.env[
            "anita_theme_setting.default_mode_data"].search([])
        default_mode_cache = {
            default_mode.name: default_mode for default_mode in default_modes}

        mode_name = self.name
        if mode_name not in default_mode_cache:
            return

        theme_styles = self.theme_styles
        theme_style_cache = {
            theme_style.name: theme_style for theme_style in theme_styles if theme_style.is_default}

        default_mode = default_mode_cache[mode_name]
        default_mode_data = default_mode.get_mode_data()

        theme_styles = default_mode_data['theme_styles']
        for theme_style in theme_styles:
            # create new style
            style_name = theme_style['name']
            if style_name not in theme_style_cache:
                self.env["anita_theme_setting.theme_style"].create_style(
                    self.id, theme_style)
            else:
                # check the style data, may be one more style with the same name
                tmp_style = theme_style_cache[style_name]
                tmp_style.check_groups(default_mode, theme_style["groups"])

    def get_mode_edit_action(self, style_id):
        """
        get theme mode edit action
        """
        self.ensure_one()
        form_id = self.env.ref("anita_theme_setting.edit_theme_mode_form").id

        var_vals = []
        for var_val in self.template_var_vals:
            var_vals.append((0, 0, {
                "name": var_val.name,
                "group": var_val.group,
                "value": var_val.value,
                "disable_opacity": var_val.disable_opacity,
                "description": var_val.description
            }))
        
        return {
            "type": "ir.actions.act_window",
            "res_model": "anita_theme_setting.theme_mode",
            "views": [[form_id, "form"]],
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_name": self.name,
                "default_mode_template": self.mode_template.id,
                "sequnce": self.sequence,
                "template_var_vals": var_vals,
                "default_style_id": style_id
            }
        }

    @api.model
    def get_create_new_mode_action(self):
        """
        get create new mode action
        """
        form_id = self.env.ref("anita_theme_setting.new_theme_mode_form").id
        return {
            "type": "ir.actions.act_window",
            "res_model": "anita_theme_setting.theme_mode",
            "views": [[form_id, "form"]],
            "view_mode": "form",
            "target": "new"
        }

    def ensure_theme_style(self):
        """
        create a empty theme style
        """
        if not self.theme_styles:
            self.env["anita_theme_setting.theme_style"].create_style(
                self.id, {
                    "name": "style1",
                    "is_default": False,
                    "groups": []
                })