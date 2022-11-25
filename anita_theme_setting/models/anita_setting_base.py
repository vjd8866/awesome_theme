# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AnitaThemeSettingBase(models.Model):
    '''
    Anita Setting Base
    '''
    _name = 'anita_theme_setting.setting_base'
    _description = 'Anita Setting Base'

    res_id = fields.Reference(
        selection=[
            ('res.users', 'user'),
            ('res.company', 'company')],
        string="Res Id",
        help="If it is system, Res id is false")

    layout_mode = fields.Selection(
        string="Layout Mode",
        selection=[
            ('Layout1', 'Layout1'),
            ('Layout2', 'Layout2'),
            ('Layout3', 'Layout3'),
        ],
        default='Layout1')

    login_style = fields.Selection(
        string="login style",
        selection=[('login_style1', 'login_style1'),
                   ('login_style2', 'login_style2'),
                   ('login_style3', 'login_style3'),
                   ('login_style4', 'login_style4')],
        default='login_style1')

    menu_icon_policy = fields.Selection(
        string="Menu Icon Policy",
        selection=[
            ('web_icon', 'web_icon'),
            ('font_icon', 'font_icon'),
            ('svg_icon', 'svg_icon')],
        default='svg_icon')

    current_theme_mode = fields.Many2one(
        comodel_name='anita_theme_setting.theme_mode',
        string="Current Theme Mode")

    current_theme_style = fields.Many2one(
        string="Current Theme Style",
        comodel_name="anita_theme_setting.theme_style",
        domain="[('theme_mode', '=', current_theme_mode)]",
        help="Just use when theme style mode is system")

    dialog_pop_style = fields.Selection(
        string="Dialog Popup Animation",
        selection=[('normal', 'normal'),
                   ('anita-effect-scale', 'scale'),
                   ('anita-effect-slide-in-right', 'slide-in-right'),
                   ('anita-effect-slide-in-bottom', 'slide-in-bottom'),
                   ('anita-effect-fall', 'anita-fall'),
                   ('anita-effect-flip-horizontal', 'flip-horizontal'),
                   ('anita-effect-effect-flip-vertical', 'flip-vertical'),
                   ('anita-effect-super-scaled', 'super-scaled'),
                   ('anita-effect-sign-in', 'sign-in'),
                   ('anita-effect-effect-newspaper', 'effect-newspaper'),
                   ('anita-effect-rotate-bottom', 'rotate-bottom'),
                   ('anita-effect-rotate-left', 'rotate-left')],
        default='normal')

    button_style = fields.Selection(
        string="Button Style",
        selection=[("btn-style-normal", "btn-style-normal"),
                   ("btn-round", "btn-round"),
                   ("btn-style-slant", "btn-style-slant")],
        default="btn-style-normal")

    table_style = fields.Selection(
        string="Table style",
        selection=[('normal', 'normal'),
                   ('bordered', 'bordered')],
        default="normal")

    form_control_style = fields.Selection(selection=[
        ('normal', 'normal'),
        ('line', 'line'),
        ('round',  'round')], default='normal')

    font_name = fields.Selection(
        string="Font Name",
        selection=[('Roboto', 'Roboto'),
                   ('Helvetica', 'Helvetica'),
                   ('Verdana', 'Verdana'),
                   ('Tahoma', 'Tahoma'),
                   ('OpenSans', 'OpenSans'),
                   ('Poppins', 'Poppins'),
                   ('NotoSansArabic', 'NotoSansArabic')],
        default="Roboto")

    rtl_mode = fields.Boolean(string="RTL MODE", default=False)
    allow_debug = fields.Boolean(string="Allow Debug", default=True)
    
    tab_style = fields.Selection(
        string="Tab style",
        selection=[('normal', 'normal'), ('line', 'line')],
        default='normal')

    input_style = fields.Selection(
        string="input style",
        selection=[('normal', 'normal'), ('line', 'line')],
        default="normal")

    @api.onchange('current_theme_mode')
    def on_current_theme_mode_change(self):
        """
        change the style
        :return:
        """
        if self.current_theme_mode.theme_styles:
            self.current_theme_style = \
                self.current_theme_mode.theme_styles[0].id
        else:
            self.current_theme_style = False
