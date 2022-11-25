# -*- coding: utf-8 -*-

from inspect import trace
from math import fabs
from odoo import models, api
from odoo.tools.config import config
import traceback

import logging
_logger = logging.getLogger(__name__)


class AnitaThemeSettingManager(models.AbstractModel):
    '''
    user theme style setting
    '''
    _name = 'anita_theme_setting.setting_manager'
    _description = 'theme setting manager'

    def _register_hook(self):
        """ 
        stuff to do right after the registry is built 
        """
        # check theme mode data
        try:
            # check mode data
            owner = self.get_current_owner()
            force = False
            if config.get('debug', False):
                self.env['anita_theme_setting.default_mode_data'].sudo().refresh_default_mode()
                force = True
            self.env["anita_theme_setting.theme_mode"].check_default_mode_data(owner, force)
        except Exception as e:
            traceback.print_stack(e)
            _logger.error(e)

    @api.model
    def get_user_setting(self, get_style=True):
        '''
        get user setting
        :return:
        '''
        rst = dict()

        # just get the setting data
        theme_setting_mode = \
            self.env["res.config.settings"].sudo().get_theme_setting_mode()

        # check mode data
        owner = self.get_current_owner()

        # get the setting data
        if theme_setting_mode == 'system':
            theme_settings = self.env["res.config.settings"].get_theme_setting()
        elif theme_setting_mode == 'company':
            theme_settings = self.env["res.company"].get_theme_setting()
        else:
            theme_settings = self.env["res.users"].get_theme_setting()

        all_modes = self.env["anita_theme_setting.theme_mode"].search(
            [('owner', '=', owner)])

        cur_style_id = theme_settings["current_theme_style"]
        cur_mode_id = theme_settings["current_theme_mode"]

        theme_mode = self.env["anita_theme_setting.theme_mode"].search(
            [('id', '=', cur_mode_id)])
        theme_style = self.env["anita_theme_setting.theme_style"].search(
            [('id', '=', cur_style_id)])
        cur_mode_name = theme_mode.name

        if not cur_mode_id \
                or cur_mode_id not in all_modes.ids:
            if all_modes:
                cur_mode_id = all_modes[0].id
                cur_style_id = all_modes[0].theme_styles[0].id if all_modes[0].theme_styles else False
                cur_mode_name = all_modes[0].name
                theme_mode = all_modes[0]
                theme_style = all_modes[0].theme_styles[0] if all_modes[0].theme_styles else False
            else:
                cur_mode_id = False
                cur_style_id = False
                cur_mode_name = False
                theme_mode = self.env["anita_theme_setting.theme_mode"]

        if not cur_style_id:
            theme_styles = theme_mode.theme_styles
            theme_style = theme_styles[0] if theme_styles else self.env["anita_theme_setting.theme_style"]
            cur_style_id = theme_style.id if theme_style else False

        rst['settings'] = theme_settings
        rst['cur_mode_id'] = cur_mode_id
        rst['cur_style_id'] = cur_style_id

        # used to set the body class
        rst['cur_mode_name'] = cur_mode_name
        rst['theme_setting_mode'] = theme_setting_mode

        rst["window_default_title"] = self.env['ir.config_parameter'].sudo().get_param(
            "anita_theme_setting.window_default_title", "Funenc Odoo")
        rst["powered_by"] = self.env['ir.config_parameter'].sudo().get_param(
            "anita_theme_setting.powered_by", "Funenc Odoo")

        # check the user is admin
        rst['is_admin'] = self.env.user._is_admin()

        # add font info
        font_name = theme_settings.get("font_name", False)
        if font_name:
            font_type_css = "*:not(.fa) {font-family: " + font_name + ", sans-serif !important;}"
        else:
            font_type_css = ""

        # get the style
        if get_style:
            if theme_style:
                style_datas = [font_type_css]
                if theme_style:
                    style_datas += theme_style.get_styles_txt()

                style_txt = '\n'.join(style_datas)
                rst['style_txt'] = style_txt

                if not theme_style.background_image:
                    rst['mode_style_css'] = theme_mode.get_mode_style_css()
                else:
                    # get from style
                    rst['mode_style_css'] = theme_style.get_mode_style_css()

            else:
                rst['style_txt'] = ""
                rst['mode_style_css'] = ""

        return rst

    @api.model
    def get_font_link(self):
        """
        get font link
        :return:
        """
        theme_settings = self.get_theme_setting()
        result = ""
        if theme_settings.get('font_name', False):
            result = '/anita_theme_setting/static/fonts/{font_name}/fonts.css'.format(font_name=theme_settings.get('font_name'))
        return result

    @api.model
    def get_theme_setting(self):
        """
        get theme setting
        :return:
        """
        # just get the setting data
        theme_setting_mode = \
            self.env["res.config.settings"].sudo().get_theme_setting_mode()

        if theme_setting_mode == 'system':
            theme_settings = self.env["res.config.settings"].get_theme_setting()
        elif theme_setting_mode == 'company':
            theme_settings = self.env["res.company"].get_theme_setting()
        else:
            theme_settings = self.env["res.users"].get_theme_setting()

        return theme_settings

    @api.model
    def get_font_name(self):
        """
        get font name
        """
        theme_settings = self.get_theme_setting()
        return theme_settings.get('font_name')

    @api.model
    def update_cur_style(self, mode_id, style_id):
        '''
        update user cur mode
        :return:
        '''
        ir_config = self.env['ir.config_parameter'].sudo()
        setting_mode = self.env["res.config.settings"].get_theme_setting_mode()
        if setting_mode == "system":
            ir_config.set_param("anita_theme_setting.current_theme_mode", mode_id)
            ir_config.set_param("anita_theme_setting.current_theme_style", style_id)
        elif setting_mode == "company":
            company = self.env.user.company_id
            company.setting_id.current_theme_mode = mode_id
            company.setting_id.current_theme_style = style_id
        elif setting_mode == "user":
            user_id = self.env.user.id
            user = self.env["res.users"].browse(user_id)
            user.setting_id.current_theme_mode = mode_id
            user.setting_id.current_theme_style = style_id
        else:
            assert False

    @api.model
    def save_style_data(self, style_id, style_data, owner):
        '''
        save style datas
        :param style_id:
        :param style_data:
        :param owner:
        :return:
        '''
        theme_style = self.env["anita_theme_setting.theme_style"].browse(style_id)
        theme_style.ensure_one()

        # save current style just when type is same
        mode_id = theme_style.theme_mode.id
        if owner:
            if owner.startswith('res.users'):
                parts = owner.split(',')
                user = self.env["res.users"].browse(int(parts[1].strip()))
                if user:
                    user.write({
                        "current_theme_mode": mode_id,
                        "current_theme_style": style_id
                    })
            elif owner.startswith('res.company'):
                parts = owner.split(',')
                company = self.env["res.company"].browse(int(parts[1].strip()))
                if company:
                    company.write({
                        "current_theme_mode": mode_id,
                        "current_theme_style": style_id
                    })
        else:
            self.update_cur_style(mode_id, style_id)

        # as the image is direct change from database so not need to update it
        var_infos = theme_style.mapped('groups.sub_groups.style_items.vars')
        var_cache = {var_info.id: var_info for var_info in var_infos}
        for data in style_data:
            var_id = data["id"]
            tmp_var = var_cache[var_id]
            tmp_var.write({
                "color": data.get('color', False)
            })

        # return the style data
        return {
            'theme_style': theme_style.get_style(),
            'mode_style_css': theme_style.get_mode_style_css()
        }

    def get_current_owner(self):
        """
        get current owner
        :return:
        """
        theme_setting_mode = \
            self.env["res.config.settings"].sudo().get_theme_setting_mode()

        # check mode data
        owner = False
        if theme_setting_mode == 'system':
            owner = False
        elif theme_setting_mode == 'company':
            owner = 'res.company, {company_id}'.format(
                company_id=self.env.user.company_id.id)
        elif theme_setting_mode == 'user':
            owner = 'res.users, {user_id}'.format(user_id=self.env.user.id)

        return owner

    @api.model
    def get_all_mode_data(self, owner):
        """
        get all mode data
        """
        all_modes = self.env["anita_theme_setting.theme_mode"].search([('owner', '=', owner)])
        result = []
        for mode in all_modes:
            result.append(mode.get_mode_data()[0])
        return result
