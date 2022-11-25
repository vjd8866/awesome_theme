# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.modules.module import get_resource_path
import base64
from odoo.tools.mimetypes import guess_mimetype


class AnitaUserSetting(models.TransientModel):
    '''
    anita user setting
    '''
    _inherit = 'res.config.settings'
    _inherits = {'anita_theme_setting.setting_base': 'setting_id'}

    setting_id = fields.Many2one(
        comodel_name="anita_theme_setting.setting_base",
        required=True,
        ondelete="cascade",
        string="setting id")

    theme_setting_mode = fields.Selection(
        string="theme style mode",
        selection=[('system', 'system'),
                   ('company', 'company'),
                   ('user', 'user')],
        default='system')

    allow_debug = fields.Boolean(string="allow debug", default=False)

    window_default_title = fields.Char(string="login title", default="Funenc")
    powered_by = fields.Char(string="powered by", default="Anita")

    @api.model
    def get_theme_setting(self):
        '''
        get the theme setting, it is usefull when the mode is system
        :return:
        '''
        return self.get_theme_values()

    @api.model
    def get_theme_setting_mode(self):
        '''
        get theme setting mode
        :return:
        '''
        config = self.env['ir.config_parameter'].sudo()
        theme_setting_mode = config.get_param(
            key='anita_theme_setting.theme_setting_mode', default='system')
        return theme_setting_mode

    @api.model
    def get_values(self):
        '''
        get the vuales
        :return:
        '''
        res = super(AnitaUserSetting, self).get_values()
        theme_values = self.get_theme_values()
        # get the favicon
        res.update(theme_values)

        return res

    @api.model
    def get_theme_values(self):
        '''
        get the theme values
        :return:
        '''
        config = self.env['ir.config_parameter'].sudo()

        layout_mode = config.get_param(key='anita_theme_setting.layout_mode', default='Layout1')
        login_style = config.get_param(key='anita_theme_setting.login_style', default='login_style1')
        theme_setting_mode = config.get_param(key='anita_theme_setting.theme_setting_mode', default='system')
        current_theme_mode = config.get_param(key='anita_theme_setting.current_theme_mode', default=False)
        current_theme_style = config.get_param(key='anita_theme_setting.current_theme_style', default=False)
        dialog_pop_style = config.get_param(key="anita_theme_setting.dialog_pop_style", default='normal')
        button_style = config.get_param(key="anita_theme_setting.button_style", default='btn-style-normal')
        control_panel_mode = config.get_param(key="anita_theme_setting.control_panel_mode", default='mode1')
        table_style = config.get_param(key="anita_theme_setting.table_style", default='normal')
        font_name = config.get_param(key="anita_theme_setting.font_name", default='Roboto')
        show_app_name = config.get_param(key="anita_theme_setting.show_app_name", default=True)
        rtl_mode = config.get_param(key="anita_theme_setting.rtl_mode", default=False)
        favorite_mode = config.get_param(key="anita_theme_setting.favorite_mode", default=False)
        allow_debug = config.get_param(key="anita_theme_setting.allow_debug", default=True)
        window_default_title = config.get_param(key="anita_theme_setting.allow_debug", default="Awesome odoo")
        powered_by = config.get_param(key="anita_theme_setting.powered_by", default="Awesome odoo")
        menu_icon_policy = config.get_param(
            key="anita_theme_setting.menu_icon_policy", default="svg_icon")

        tab_style = config.get_param(key="anita_theme_setting.tab_style", default="normal")
        icon_style = config.get_param(key="anita_theme_setting.icon_style", default="normal")
        
        return {
            "layout_mode": layout_mode,
            "login_style": login_style,
            "theme_setting_mode": theme_setting_mode,
            "current_theme_mode": int(current_theme_mode),
            "current_theme_style": int(current_theme_style),
            "dialog_pop_style": dialog_pop_style,
            "button_style": button_style,
            "control_panel_mode": control_panel_mode,
            "table_style": table_style,
            "font_name": font_name,
            "show_app_name": show_app_name,
            "rtl_mode": rtl_mode,
            "favorite_mode": favorite_mode,
            "allow_debug": allow_debug,
            "window_default_title": window_default_title,
            "powered_by": powered_by,
            "menu_icon_policy": menu_icon_policy,
            "tab_style": tab_style,
            "icon_style": icon_style,
        }

    def set_values(self):
        '''
        set values
        :return:
        '''
        super(AnitaUserSetting, self).set_values()

        ir_config = self.env['ir.config_parameter'].sudo()

        ir_config.set_param("anita_theme_setting.layout_mode", self.layout_mode or "Layout1")
        ir_config.set_param("anita_theme_setting.login_style", self.login_style or "login_style1")
        ir_config.set_param("anita_theme_setting.theme_setting_mode", self.theme_setting_mode or 'system')
        ir_config.set_param("anita_theme_setting.current_theme_mode", self.current_theme_mode.id or False)
        ir_config.set_param("anita_theme_setting.current_theme_style", self.current_theme_style.id or False)
        ir_config.set_param("anita_theme_setting.dialog_pop_style", self.dialog_pop_style or 'normal')
        ir_config.set_param("anita_theme_setting.button_style", self.button_style or 'btn-style-normal')
        ir_config.set_param("anita_theme_setting.table_style", self.table_style or 'normal')
        ir_config.set_param("anita_theme_setting.control_panel_mode", self.control_panel_mode or 'normal')
        ir_config.set_param("anita_theme_setting.font_name", self.font_name or 'Roboto')
        ir_config.set_param("anita_theme_setting.show_app_name", self.show_app_name)
        ir_config.set_param("anita_theme_setting.rtl_mode", self.rtl_mode)
        ir_config.set_param("anita_theme_setting.favorite_mode", self.favorite_mode)
        ir_config.set_param("anita_theme_setting.allow_debug", self.favorite_mode)

        ir_config.set_param("anita_theme_setting.window_default_title", self.window_default_title)
        ir_config.set_param("anita_theme_setting.powered_by", self.powered_by)

        ir_config.set_param("anita_theme_setting.menu_icon_policy", self.menu_icon_policy)
        ir_config.set_param("anita_theme_setting.tab_style", self.tab_style)
        ir_config.set_param("anita_theme_setting.icon_style", self.icon_style)

    def set_values_company_favicon(self):
        '''
        set the favicon of company
        :return:
        '''
        company = self.sudo().env['res.company']
        records = company.search([])

        if len(records) > 0:
            for record in records:
                record.write({'favicon': self._set_web_favicon(original=True)})

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model
    def get_login_style(self):
        '''
        get login style
        :return:
        '''
        ir_config = self.env['ir.config_parameter'].sudo()
        login_style = ir_config.get_param(
            key='anita_theme_setting.login_style', default='login_style1')
        return login_style
