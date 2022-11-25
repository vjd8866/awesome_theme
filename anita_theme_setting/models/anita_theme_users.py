# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import datetime
from datetime import date, datetime


class AnitaThemeUsers(models.Model):
    '''
    user theme style setting
    '''
    _inherit = "res.users"
    _description = 'user setting'
    _inherits = {"anita_theme_setting.setting_base": "setting_id"}

    setting_id = fields.Many2one(
        comodel_name="anita_theme_setting.setting_base",
        ondelete="cascade",
        string="settings")

    @api.model
    def save_setting(self, settings):
        '''
        save settings, create if there is no user info
        just use full when the mode is user wide mode
        :param settings:
        :return:
        '''
        uid = self.env.user.id
        record = self.search([('uid', '=', uid)])
        if not record:
            self.create([{"setting_id": [(0, 0, settings)]}])
        else:
            self.setting_id.write(settings)

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
        get settings
        :return:
        '''
        record = self.env.user
        record.check_setting_id()
        field_names = [name for name, field in record.setting_id._fields.items() if name not in [
                "icon128x128", "icon144x144", "icon152x152", "icon192x192", "icon256x256", "icon512x512"]]
        result = record.setting_id.read(fields=field_names)[0]
        result["current_theme_mode"] = record.setting_id.current_theme_mode.id
        result["current_theme_style"] = record.setting_id.current_theme_style.id
        for key, item in result.items():
            if isinstance(item, datetime):
                result[key] = fields.Datetime.to_string(item)
            if isinstance(item, date):
                result[key] = fields.Date.to_string(item)

        return result

    def check_default_data(self):
        """
        check default data
        :return:
        """
        # check mode data
        owner = 'res.users, {user_id}'.format(user_id=self.id)
        self.env["anita_theme_setting.theme_mode"].check_default_mode_data(owner)

    def edit_user_theme(self):
        '''
        user theme setting
        :return:
        '''
        self.ensure_one()

        rst = dict()

        # check mode data
        self.check_default_data()

        theme_settings = self.get_theme_setting()
        cur_style_id = theme_settings["current_theme_style"]
        cur_mode_id = theme_settings["current_theme_mode"]

        owner = 'res.users, {user_id}'.format(user_id=self.id)
        all_modes = self.env["anita_theme_setting.theme_mode"].search([('owner', '=', owner)])
        if not all_modes:
            raise exceptions.ValidationError("Please create mode first!")

        ids = all_modes.ids
        if not cur_mode_id or cur_mode_id not in ids:
            cur_mode_id = all_modes[0].id
            cur_style_id = all_modes[0].theme_styles[0].id

        rst['theme_modes'] = all_modes.get_mode_data()
        rst['settings'] = theme_settings
        rst['cur_mode_id'] = cur_mode_id
        rst['cur_style_id'] = cur_style_id
        rst['is_admin'] = self.env.is_admin()
        rst['owner'] = owner

        return {
            "type": "ir.actions.client",
            "tag": "theme_edit_action",
            "params": rst
        }

    @api.model
    def get_user_xml_groups(self):
        '''
        :return:
        '''
        group_ids = self.env.user.groups_id.ids
        records = self.env['ir.model.data']\
            .sudo() \
            .search_read([('model', '=', 'res.groups'),
                          ('res_id', 'in', group_ids)], fields=["complete_name"])
        return {record["complete_name"]: True for record in records}

    def get_mode_domain(self):
        """
        get mode domain dynamic
        :return:
        """
        owner = 'res.users, {user_id}'.format(user_id=self.id)
        return [('owner', '=', owner)]

    @api.model
    def get_group_infos(self):
        '''
        :return:
        '''
        group_ids = self.env.user.groups_id.ids
        records = self.env['ir.model.data']\
            .sudo() \
            .search_read(
            [('model', '=', 'res.groups'),
             ('res_id', 'in', group_ids)],
            fields=["complete_name"])
        groups = {record["complete_name"]: True for record in records}

        return {
            "groups": groups,
            "group_ids": group_ids,
            "user_id": self.env.user.id
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
            "res_model": "res.users",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            "views": [[self.env.ref(
                'anita_theme_setting.anita_user_theme_setting_form').id, "form"]]
        }
