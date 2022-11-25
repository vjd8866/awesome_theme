# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import json
import base64
from odoo.tools.config import config
from .anita_utility import apply_alpha
import traceback

import logging
_logger = logging.getLogger(__name__)


class AnitaThemeStyle(models.Model):
    '''
    Theme style
    '''
    _name = 'anita_theme_setting.theme_style'
    _description = 'awesome theme style'
    _order = 'sequence'

    name = fields.Char(string="style name", required=True)
    theme_mode = fields.Many2one(
        comodel_name="anita_theme_setting.theme_mode",
        string="theme mode",
        ondelete="cascade")
    mode_css = fields.Text(string="mode style scss")
    style_css = fields.Text(string="style css")

    is_default = fields.Boolean(string="is default", default=False)

    background_image = fields.Many2one(
        comodel_name="anita_theme_setting.background_image",
        string="background image",
        ondelete="set null")
    opacity = fields.Float(string="opacity", default=1.0)

    owner = fields.Reference(
        string="owner",
        selection=[
            ('res.company', 'res.company'),
            ('res.users', 'res.users')],
        default=False,
        help="Owner which this theme is create by")

    sequence = fields.Integer(string="style sequence", default=0)

    groups = fields.One2many(
        string="Groups",
        comodel_name="anita_theme_setting.style_item_group",
        inverse_name="theme_style")

    side_bar_style = fields.Selection(
        string="side bar style",
        selection=[
            ('style1', 'style1'),
            ('style2', 'style2'),
            ('style3', 'style3')])

    sidebar_width = fields.Integer(string="sidebar width", default=80)
    sidebar_menu_width = fields.Integer(
        string="sidebar menu width", default=220)

    @api.onchange('background_image')
    def onchange_background_image(self):
        """
        on change background image data
        """
        if self.background_image:
            self.opacity = self.background_image.opacity
        else:
            self.opacity = 1.0

    def get_style(self):
        '''
        get simple style data
        :return:
        '''
        self.ensure_one()
        result = self.read(['id', 'name', 'is_default'])[0]
        result["groups"] = self.groups.get_group_data()
        result["theme_mode"] = self.theme_mode.name
        # get background image ulr
        if self.background_image:
            result["background_image"] = self.background_image.get_image_url()
        else:
            result["background_image"] = False
        result["opacity"] = self.opacity
        identities = dict()
        groups = result["groups"]
        # collect identity
        for group in groups:
            sub_groups = group["sub_groups"]
            for sub_group in sub_groups:
                style_items = sub_group["style_items"]
                for item in style_items:
                    if not item["vars"]:
                        continue
                    # collect the identity
                    var_infos = item["vars"]
                    for var in var_infos:
                        if var.get('identity', False):
                            if self.is_semi_transparent():
                                identities[var['identity']] = apply_alpha(var['name'], var['color'], self.opacity, var.get('color_type'))
                            else:
                                identities[var['identity']] = var['color']
                                
        result["identities"] = identities
        return result

    def get_styles(self):
        '''
        get mode datas
        :return:
        '''
        results = []
        for record in self:
            results.append(record.get_style())
        return results

    def _get_style_data(self):
        '''
        get mode datas
        :return:
        '''
        self.ensure_one()
        results = []
        result = self.read(['name', 'is_default', 'sequence'])[0]
        if self.background_image:
            result["background_image"] = self.background_image.get_image_url()
        result["groups"] = self.groups.get_group_data()
        results.append(result)
        return results

    def get_styles_txt(self):
        '''
        get style txt
        :return:
        '''
        self.ensure_one()

        mode_prefix = 'body.' + self.theme_mode.name + ' '
        result = []
        groups = self.groups
        for group in groups:
            for sub_group in group.sub_groups:
                style_items = sub_group.style_items
                for style_item in style_items:
                    val = style_item.val
                    
                    # if the val is same as the ref var, then ignore it
                    if not val or val == "" or not style_item.selectors:
                        continue

                    try:
                        selector = mode_prefix + \
                            ','.join(json.loads(style_item["selectors"]))
                        tmp_txt = selector + " {" + val + "}"
                        result.append(tmp_txt)
                    except Exception as error:
                        traceback.print_stack(e)
                        _logger.info(error)
    
        # append the background image
        if self.background_image:
            background_image_url = self.background_image.get_image_url()
            if background_image_url:
                result.append(
                    mode_prefix + " {background-image: url('" +
                    background_image_url + "') !important;")

        return result

    def is_semi_transparent(self):
        '''
        is semi transparent
        :return:
        '''
        self.ensure_one()
        return self.opacity < 1.0

    def get_mode_style_css(self):
        '''
        get mode styles
        :return:
        '''
        self.ensure_one()

        if not self.is_semi_transparent():
            return self.theme_mode.get_mode_style_css()
        else:
            if config.get('debug', False) or not self.mode_css:
                self.mode_css = self.theme_mode._compile_scss(self.opacity or 1)
            return self.mode_css

    def _compute_var_val(self, style_item_info):
        '''
        compute the val, use by the 
        :return:
        '''
        self.ensure_one()

        background_image = self.background_image
        scss_var_cache = self.theme_mode.get_scss_vars_cache()
        opacity = self.opacity
        vars_cache = dict()
        all_color = True
        all_ref = True
        all_same = True
        for var in style_item_info.get('vars', []):
            name = var.get('name', False)
            type = var.get('type', False)
            if type == 'color':
                # check if has opacity
                color = var.get('color')
                ref_var = var.get('ref_var', False)
                if ref_var:
                    ref_color = scss_var_cache[ref_var]
                    if ref_color != color:
                        all_same = False
                else:
                    all_ref = False

                try:
                    if background_image: 
                        if not var.get('disable_opacity', False):
                            color = apply_alpha(name, color, opacity, var.get('color_type'))
                except Exception as e:
                    traceback.print_stack(e)
                    _logger.error("apply alpha error {e}".format(e=e))
                vars_cache[name] = color
            elif var.type == 'image':
                vars_cache[name] = var.get('image_file_url')
                all_color = False
            elif var.type == 'image_url':
                vars_cache[name] = var.get('image_url')
                all_color = False
            else:
                vars_cache[name] = var.get('svg')
                all_color = False

        # if all the color are the original color, them ignore it
        if all_color and all_ref and all_same:
            style_item_info['val'] = False
        else:
            try:
                val_template = style_item_info.get('val_template', False)
                style_item_info['val'] = val_template.format(**vars_cache)
            except Exception as error:
                style_item_info['val'] = False
                traceback.print_stack(e)
                _logger.info('parse var value error, item name {item_name}->{error}'.format(
                    item_name=style_item_info['name'], error=error))

    def post_deal_preview_data(self, style_item_infos, font_info, preview = False):
        '''
        get mode datas
        :return:
        '''
        self.ensure_one()

        if preview:
            mode_prefix = 'body.preview '
        else:
            mode_prefix = 'body.' + self.theme_mode.name + ' '

        result = [font_info]
        groups = self.groups
        for group in groups:
            for sub_group in group.sub_groups:
                style_items = sub_group.style_items
                for style_item in style_items:
                    if str(style_item.id) not in style_item_infos:
                        val = style_item.val
                        if val == "":
                            continue
                        if not style_item.selectors:
                            continue
                        try:
                            selector = mode_prefix + \
                                ','.join(json.loads(style_item["selectors"]))
                            tmp_txt = selector + " {" + val + "}"
                            result.append(tmp_txt)
                        except Exception as error:
                            traceback.print_stack(e)
                            _logger.info(error)
                    else:
                        style_item = style_item_infos[str(style_item.id)]
                        
                        # compute the val
                        self._compute_var_val(style_item)
                        val = style_item.get('val', False)
                    
                        # if the val is same as the ref var, then ignore it
                        selectors = style_item.get('selectors', False)
                        if not val or val == "" or not selectors:
                            continue

                        try:
                            # check selector is a array
                            if not isinstance(selectors, list):
                                selectors = [selectors]
                            selector = mode_prefix + ','.join(selectors)
                            tmp_txt = selector + " {" + val + "}"
                            result.append(tmp_txt)
                        except Exception as error:
                            traceback.print_stack(e)
                            _logger.info(error)

        # append the background image
        if self.background_image:
            background_image_url = self.background_image.get_image_url()
            if background_image_url:
                result.append(
                    mode_prefix + " {background-image: url('" +
                    background_image_url + "') !important;")

        return "\n".join(result)

    @api.model
    def delete_style(self, style_id):
        '''
        delete styel of user
        :return:
        '''
        record = self.search([('id', '=', style_id)])
        record.unlink()

    def check_groups(self, default_mode, groups):
        '''
        check the style group
        :param groups:
        :return:
        '''
        self.ensure_one()

        new_group_cache = {group["name"]: group for group in groups}
        old_group_cache = {group.name: group for group in self.groups}

        for group_index, name in enumerate(new_group_cache):
            default_group = new_group_cache[name]
            if name not in old_group_cache:
                self.env['anita_theme_setting.style_item_group']\
                    .create_group_from_default_data(self, default_group, group_index)
            else:
                # update the style item
                tmp_group = old_group_cache[name]
                tmp_group.write({
                    "name": name,
                    "is_default": True,
                    "sequence": group_index,
                })
                # check group item data
                sub_group_items = default_group["sub_groups"]
                tmp_group.check_sub_group(default_mode, sub_group_items)

        # delete the style item
        for tmp_group_name in old_group_cache:
            if tmp_group_name not in new_group_cache \
                    and old_group_cache[tmp_group_name].is_default:
                old_group_cache[tmp_group_name].unlink()

    def create_style(
            self, model_id, style_data, owner=False, is_default=True):
        '''
        create theme style from default info
        :return:
        '''
        default_groups = style_data['groups']
        mode = self.env['anita_theme_setting.theme_mode'].browse(model_id)
        scss_vars_cache = mode.get_scss_vars_cache()

        group_datas = []
        for group_index, group in enumerate(default_groups):
            sub_groups = group["sub_groups"]
            sub_group_array = []
            for sub_group_index, sub_group in enumerate(sub_groups):

                style_items = sub_group["style_items"]
                style_item_datas = []
                for style_item_index, style_item in enumerate(style_items):
                    selectors = json.dumps(style_item['selectors'])
                    var_vals = []
                    var_infos = style_item['vars']
                    for var_info in var_infos:
                        ref_var = var_info.get('ref', False)
                        if ref_var:
                            if ref_var in scss_vars_cache:
                                raise exceptions.ValidationError(
                                    _("The variable %s has been used") % ref_var)
                            else:
                                color = scss_vars_cache[ref_var]
                        else:
                            color = var_info.get('color', False)

                        var_vals.append((0, 0, {
                            "name": var_info["name"],
                            "is_default": is_default,
                            "type": var_info["type"],
                            "color": color,
                            "image": var_info.get('image', False),
                            "image_url": var_info.get('image_url', False),
                            "svg": var_info.get('svg', False),
                            "identity": var_info.get('identity', False)
                        }))

                    tmp_style_item = dict()
                    tmp_style_item['selectors'] = selectors
                    tmp_style_item['sequence'] = style_item_index
                    tmp_style_item['name'] = style_item["name"]
                    tmp_style_item["is_default"] = is_default
                    tmp_style_item["val_template"] = style_item["val_template"]
                    tmp_style_item["vars"] = var_vals

                    style_item_datas.append((0, 0, tmp_style_item))

                sub_group_array.append((0, 0, {
                    "name": sub_group["name"],
                    "sequence": sub_group_index,
                    "style_items": style_item_datas,
                    "is_default": True
                }))

            group_datas.append((0, 0, {
                "name": group["name"],
                "sequence": group_index,
                "sub_groups": sub_group_array,
                "is_default": True
            }))

        return self.env['anita_theme_setting.theme_style'].create({
            "name": style_data["name"],
            "theme_mode": model_id,
            "is_default": is_default,
            "groups": group_datas,
            "owner": owner
        })

    @api.model
    def add_new_style(
            self, mode_id, style_data, owner=False, is_default=False):
        '''
        add new style, get the first style as the default, call from the front web
        :return:
        '''
        # if not owner, use the current owner
        if not owner:
             owner = self.env["anita_theme_setting.setting_manager"].get_current_owner()

        theme_style = self.create_style(
            mode_id, style_data, owner, is_default)

        # return the new style data
        style_data = theme_style.get_styles()[0]

        return style_data

    def clone_style(self, owner=False):
        '''
        clone style
        :return:
        '''
        self.ensure_one()
        if not owner:
            owner = self.env["anita_theme_setting.setting_manager"].get_current_owner()

        style_data = self.get_styles()[0]
        return self.add_new_style(self.theme_mode.id, style_data, owner)

    @api.model
    def import_new_style(self, mode_id, wizard_id):
        """
        import new style
        :param mode_id:
        :param wizard_id:
        :return:
        """
        wizard = self.env["anita_theme_setting.import_theme_style"].browse(
            wizard_id)
        style_data = json.loads(
            base64.decodebytes(wizard.file).decode('utf-8'))
        return self.add_new_style(mode_id, style_data)

    def set_background_image(self, wizard_id):
        """
        set background image
        """
        self.ensure_one()
        wizard = self.env["anita_theme_setting.background_image_wizard"].browse(
            wizard_id)

        # create background image
        record = self.env["anita_theme_setting.background_image"].create({
            "data": wizard.data,
            "opacity": wizard.opacity,
        })

        self.background_image = record.id
        self.opacity = wizard.opacity
        # reutrn the image url
        return self.background_image.get_image_url()

    def clear_style_css(self):
        """
        clear style css when style change
        """
        self.ensure_one()
        self.style_css = False
