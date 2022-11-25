# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import logging
import json
from .anita_utility import apply_alpha

_logger = logging.getLogger(__name__)


class AnitaThemeStyleItem(models.Model):
    '''
    user theme style setting
    '''
    _name = 'anita_theme_setting.style_item'
    _order = 'sequence asc'
    _description = "style item"

    sub_group = fields.Many2one(
        comodel_name="anita_theme_setting.style_item_sub_group", string="sub group")
    theme_mode = fields.Many2one(
        comodel_name="anita_theme_setting.theme_mode", 
        related="sub_group.group.theme_style.theme_mode",
        store=True,
        string="theme mode")
    theme_style = fields.Many2one(
        comodel_name="anita_theme_setting.theme_style",
        related = "sub_group.group.theme_style",
        string="theme style")
        
    name = fields.Char(string="name", required=True, default="var1")
    val = fields.Char(string="val", compute="_compute_val")
    sequence = fields.Integer(string="sequence", default=0)
    mode = fields.Selection(
        selection=[('override', 'override'), ('primary', 'primary')],
        string="mode",
        default="override", 
        help="override or primary, override is override the default style and primary is create a new style")
    val_template = fields.Char(
        string="val template",
        required=True,
        default="background: {var1}", help="Save the last val")
    vars = fields.One2many(
        string="vars",
        comodel_name="anita_theme_setting.theme_var",
        inverse_name="style_item")
    selectors = fields.Char(string="selectors", required=True)
    is_default = fields.Boolean(string="Is Default", default=True)
    type = fields.Selection(
        string="type",
        selection=[('normal', 'normal'),
                   ('login', 'login')],
        default='normal')
    login_style = fields.Char(string="login style", default="login_style1")


    def check_vars(self, default_mode, sub_group_id, default_vars):
        '''
        check vars
        :return:
        '''
        # check vars
        self.ensure_one()
        var_val_cache = default_mode.get_var_val_cache()

        # get current var cache
        old_var_cache = {var.name: var for var in self.vars}
        default_var_cache = \
            {default_var["name"]: default_var for default_var in default_vars}

        tmp_vals = []
        for default_var in default_vars:

            color = default_var.get("color", False)
            ref_var = default_var.get("ref_var",False)
            if ref_var:
                if ref_var not in var_val_cache:
                    color = False
                    _logger.info("ref var {ref_var} not in var cache".format(ref_var=ref_var))
                else:
                    color = var_val_cache[ref_var]

            # item exits must keep
            if default_var["name"] not in old_var_cache:
                tmp_vals.append({
                    "sub_group": sub_group_id,
                    "name": default_var["name"],
                    "style_item": self.id,
                    "type": default_var["type"],
                    "color": color,
                    "image": default_var.get('image', False),
                    "image_url": default_var.get('image_url', False),
                    "svg": default_var.get('svg', False),
                    "is_default": default_var.get('is_default', True),
                    "identity": default_var.get('identity', False),
                    "ref_var": ref_var,
                    "disable_opacity": default_var.get('disable_opacity', False),
                })
            else:
                # keep the val, maybe user will
                tmp_var = old_var_cache[default_var["name"]]
                tmp_var.write({
                    "type": default_var["type"],
                    "is_default": default_var.get('is_default', True),
                    "identity": default_var.get('identity', False),
                    "color": color,
                    "image": default_var.get('image', False),
                    "image_url": default_var.get('image_url', False),
                    "svg": default_var.get('svg', False),
                    "ref_var": ref_var,
                    "disable_opacity": default_var.get('disable_opacity', False),
                })

        # create the missing vars
        self.env["anita_theme_setting.theme_var"].create(tmp_vals)

        # unlink the old var
        for name in old_var_cache:
            if name not in default_var_cache:
                tmp_var = old_var_cache[name]
                tmp_var.unlink()

    @api.depends('selectors', 'val_template', "vars")
    def _compute_val(self):
        '''
        compute the val
        :return:
        '''
        # check if mode has background image
        for record in self:
            # if every var is color and the color val is same as the ref var
            background_image = record.theme_style.background_image
            scss_var_cache = record.theme_mode.get_scss_var_record_cache()
            opacity = record.theme_style.opacity
            vars_cache = dict()
            all_color = True
            all_ref = True
            all_same = True
            for var in record.vars:
                if var.type == 'color':
                    # check if has opacity
                    color = var.color
                    if var.ref_var and var.ref_var in scss_var_cache:
                        ref_color = scss_var_cache[var.ref_var]
                        if ref_color != color:
                            all_same = False
                    else:
                        all_ref = False

                    try:
                        if background_image:
                            if not var.disable_opacity:
                                color = apply_alpha(var.name, color, opacity, var.color_type)
                    except Exception as e:
                        _logger.error("apply alpha error {e}".format(e=e))

                    vars_cache[var.name] = color
                elif var.type == 'image':
                    vars_cache[var.name] = var.image_file_url
                    all_color = False
                elif var.type == 'image_url':
                    vars_cache[var.name] = var.image_url
                    all_color = False
                else:
                    vars_cache[var.name] = var.svg
                    all_color = False

            # if all the color are the original color, them ignore it
            if all_color and all_ref and all_same:
                record.val = False
            else:
                if not record.vars:
                    record.val = False
                else:
                    try:
                        record.val = str(record.val_template).format(**vars_cache)
                    except Exception as error:
                        record.val = False
                        _logger.info('parse var value error, item name {item_name}->{error}'.format(
                            item_name=record['name'], error=error))

    def get_style_item_data(self):
        '''
        get the style item data
        :return:
        '''
        export_style = self.env.context.get('export_style', False)
        style_items = []
        for record in self:
            style_item = record.read(
                fields=["id", "name", "is_default", "val_template", "val", "selectors"])[0]

            try:
                style_item['selectors'] = json.loads(style_item['selectors'])
            except Exception as error:
                _logger.info('try to decode selectors error!', error)

            if not export_style:
                # maybe the image is very large, so do not read the image
                style_item["vars"] = \
                    record.vars.read(
                        ["name", "identity", "type", "image_file_url", "image_url", "color", "svg", "color_type"])
            else:
                style_item["vars"] = \
                    record.vars.read(
                        ["name", "identity", "type", "image", "image_url", "color", "svg", "color_type"])
                for tmp_var in style_item["vars"]:
                    if tmp_var["image"]:
                        tmp_var["image"] = str(tmp_var["image"])

            style_items.append(style_item)
        return style_items

    def write(self, vals):
        """
        rewrite to check if the selectors are right
        :param vals:
        :return:
        """
        super(AnitaThemeStyleItem, self).write(vals)

        vars_cache = dict()
        for var in self.vars:
            if var.type == 'color':
                vars_cache[var.name] = var.color
            elif var.type == 'image':
                vars_cache[var.name] = var.image_file_url
            elif var.type == 'image_url':
                vars_cache[var.name] = var.image_url
            else:
                vars_cache[var.name] = var.svg

        # check the var
        try:
            str(self.val_template).format(**vars_cache)
        except Exception as error:
            _logger.info('parse var value error, item name {item_name}->{error}'.format(
                item_name=self['name'], error=error))

    def get_login_style_data(
            self, theme_style_id, login_style):
        """
        get login style data
        :return:
        """
        result = []
        theme_style = self.env["anita_theme_setting.theme_style"].browse(theme_style_id)
        sub_group_ids = theme_style.mapped('groups.sub_groups.id')
        style_items = self.search(
            [('type', '=', 'login'),
             ('login_style', '=', login_style),
             ('sub_group', 'in', sub_group_ids)])
        for style_item in style_items:
            val = style_item.val
            if val == "":
                continue
            if not style_item.selectors:
                continue
            try:
                selector = ','.join(json.loads(style_item["selectors"]))
                tmp_txt = selector + " {" + val + "}"
                result.append(tmp_txt)
            except Exception as error:
                _logger.info(error)
        return ";".join(result)

    def delete_style_item(self):
        '''
        delete style item
        :return:
        '''
        self.ensure_one()
        self.unlink()

    def create_style_item(
            self, default_mode, sub_group, style_item, style_item_index):
        '''
        create group from default data
        :return:
        '''
        selectors = json.dumps(style_item["selectors"])
        var_infos = style_item["vars"]
        var_val_cache = default_mode.get_var_val_cache()

        var_vals = []
        for var_index, var_info in enumerate(var_infos):

            color = var_info.get("color", False)
            ref_var = var_info.get("ref_var", False)
            if ref_var:
                if ref_var not in var_val_cache:
                    color = False
                    _logger.info("ref var not in var cache", ref_var)
                else:
                    color = var_val_cache[ref_var]

            var_vals.append((0, 0, {
                "name": var_info["name"],
                "type": var_info["type"],
                "sequence": var_index,
                "color": color,
                "image": var_info.get('image', False),
                "image_url": var_info.get('image_url', False),
                "svg": var_info.get('svg', False),
                "identity": var_info.get('identity', False),
                "ref_var": ref_var
            }))

        style_item_val = {
            "name": style_item["name"],
            "sequence": style_item_index,
            "val_template": style_item["val_template"],
            "selectors": selectors,
            "vars": var_vals,
            "sub_group": sub_group
        }

        return self.create([style_item_val])

    def resert_var(self):
        """
        reset var, resut to the derfault value
        :return:
        """
        if not self.ref_var and self.type != 'color':
            return False
        # get mode first
        var_cache = self.sub_group.group.theme_style.theme_mode.get_scss_vars_cache()
        for var in self.vars.filtered(lambda x: x.type == 'color'):
            if var.ref_var:
                var.color = var_cache.get(var.ref_var, False)
        return True