# -*- coding: utf-8 -*-

from odoo import fields, models, exceptions
import base64
from datetime import date, datetime
from odoo.modules.module import get_resource_path


class AnitaCompany(models.Model):
    '''
    extend to support current mode and current style
    '''
    _inherit = "res.company"
    _name = 'res.company'
    _inherits = {"anita_theme_setting.setting_base": "setting_id"}

    setting_id = fields.Many2one(
        comodel_name="anita_theme_setting.setting_base",
        ondelete="cascade",
        string="setting id")
    
    def _get_default_favicon_icon(self):
        """
        get default favicon icon form  static path
        """
        tmp_path = get_resource_path(
            'anita_theme_setting', 'static', 'images', 'favicon.png')
        return base64.b64encode(open(tmp_path, 'rb').read())
        
    favicon_icon = fields.Binary(
        string='Web Favicon Icon', default='_get_default_favicon_icon')

    def _get_default_small_logo(self):
        '''
        get the default small logo
        :return:
        '''
        tmp_path = get_resource_path(
            'anita_theme_setting', 'static', 'images', 'favicon.ico')
        return base64.b64encode(open(tmp_path, 'rb').read())

    logo_small = fields.Binary(
        default=_get_default_small_logo, string="Company Small Logo")

    def get_mode_data(self):
        '''
        get mode data
        :return:
        '''
        owner = 'res.company, {company_id}'.format(
            company_id=self.env.user.company_id)
        self.env["anita_theme_setting.theme_mode"].check_default_mode_data(owner)
        return self.env["anita_theme_setting.theme_mode"].get_mode_data()

    def get_mode_domain(self):
        """
        get mode domain dynamic
        :return:
        """
        owner = 'res.company, {company_id}'.format(
            company_id=self.env.user.company_id.id)
        return [('owner', '=', owner)]

    def get_company_mode_data(self):
        '''
        get company mode data
        :return:
        '''
        return self.get_mode_data()

    def check_setting_id(self):
        '''
        check setting id
        :return:
        '''
        self.ensure_one()

        # copy use the global default data
        values = self.env['res.config.settings'].get_theme_values()
        
        # get fields of anita_theme_setting.setting_base
        field_names = [name for name, field in self.setting_id._fields.items() if name not in [
            'id', 'create_uid', 'create_date', 'write_uid', 'write_date']]
        
        # remove name not in fields
        values = {k: v for k, v in values.items() if k in field_names}

        del values["current_theme_mode"]
        del values["current_theme_style"]

        if not self.setting_id:
            tmp_record = self.env["anita_theme_setting.setting_base"].create(values)
            self.setting_id = tmp_record.id

    def get_theme_setting(self):
        '''
        get company setting
        :return:
        '''
        company_id = self.env.user.company_id.id
        record = self.search([('id', '=', company_id)])
        record.check_setting_id()
        result = record.setting_id.read()[0]
        result["current_theme_mode"] = record.setting_id.current_theme_mode.id
        result["current_theme_style"] = record.setting_id.current_theme_style.id
        for key, item in result.items():
            if isinstance(item, datetime):
                result[key] = fields.Datetime.to_string(item)
            if isinstance(item, date):
                result[key] = fields.Date.to_string(item)

        return result

    def save_company_settings(self, settings):
        '''
        save settings to company id
        :param company_id:
        :param settings:
        :return:
        '''
        self.setting_id = (6, 0, settings)

    def check_default_data(self):
        """
        check default data
        :return:
        """
        # check mode data
        owner = 'res.company, {company_id}'.format(company_id=self.id)
        self.env["anita_theme_setting.theme_mode"].check_default_mode_data(owner)

    def edit_company_theme(self):
        '''
        edit company theme
        :return:
        '''
        self.ensure_one()

        rst = dict()

        self.check_setting_id()
        self.check_default_data()

        theme_settings = self.get_theme_setting()
        cur_style_id = theme_settings["current_theme_style"]
        cur_mode_id = theme_settings["current_theme_mode"]
        cur_mode_name = ""
        owner = 'res.company, {company_id}'.format(company_id=self.id)

        all_modes = self.env["anita_theme_setting.theme_mode"].search([('owner', '=', owner)])
        if not all_modes:
            raise exceptions.ValidationError("Please create mode first!")
        ids = [mode.id for mode in all_modes]
        if not cur_mode_id or cur_mode_id not in ids:
            cur_mode_id = all_modes[0].id
            cur_style_id = all_modes[0].theme_styles[0].id
            cur_mode_name = all_modes[0].name

        # rst['theme_modes'] = all_modes.get_mode_data()
        rst['settings'] = theme_settings
        rst['cur_mode_id'] = cur_mode_id
        rst['cur_style_id'] = cur_style_id
        rst['cur_mode_name'] = cur_mode_name
        rst['is_admin'] = self.env.is_admin()
        rst['owner'] = owner

        return {
            "type": "ir.actions.client",
            "tag": "theme_edit_action",
            "params": rst
        }

    def theme_setting(self):
        '''
        theme setting action
        :return:
        '''
        self.check_setting_id()
        self.check_default_data()

        return {
            "type": "ir.actions.act_window",
            "res_model": "res.company",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            "views": [[self.env.ref(
                'anita_theme_setting.anita_edit_company_setting').id, "form"]]
        }
