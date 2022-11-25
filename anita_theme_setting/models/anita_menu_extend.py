# -*- coding: utf-8 -*-

from odoo.tools.convert import xml_import, nodeattr2bool
import odoo
from odoo import api, fields, models, tools
from odoo.osv import expression
from .anita_default_menu_icon import svg_icons, font_icons


class AnitaMenuExtend(models.Model):
    '''
    extend to support font icon and svg icon
    '''
    _inherit = 'ir.ui.menu'

    font_icon = fields.Char(string='font icon')
    svg_icon = fields.Text(string='svg icon')
    
    
    def load_web_menus(self, debug):
        """ Loads all menu items (all applications and their sub-menus) and
        processes them to be used by the webclient. Mainly, it associates with
        each application (top level menu) the action of its first child menu
        that is associated with an action (recursively), i.e. with the action
        to execute when the opening the app.

        :return: the menus (including the images in Base64)
        """
        theme_setting = self.env["anita_theme_setting.setting_manager"].sudo().get_theme_setting()
        menu_icon_policy = theme_setting.get("menu_icon_policy", "svg_icon")

        menus = self.load_menus(debug)
        favorite_cache = {}
        if theme_setting["favorite_mode"]:
            favorite_apps = self.env['anita_theme_setting.favorite_menu'].sudo().search(
                [('user_id', '=', self.env.uid)])
            favorite_cache = {fav.menu_id.id: fav for fav in favorite_apps}

        web_menus = {}
        for menu in menus.values():
            if not menu['id']:
                # special root menu case
                web_menus['root'] = {
                    "id": 'root',
                    "name": menu['name'],
                    "children": menu['children'],
                    "appID": False,
                    "xmlid": "",
                    "actionID": False,
                    "actionModel": False,
                    "webIcon": None,
                    "webIconData": None,
                    "backgroundImage": menu.get('backgroundImage'),
                    "menu_icon_policy": menu_icon_policy,
                }
            else:
                action = menu['action']

                if menu['id'] == menu['app_id']:
                    # if it's an app take action of first (sub)child having one defined
                    child = menu
                    while child and not action:
                        action = child['action']
                        child = menus[child['children'][0]] if child['children'] else False

                action_model, action_id = action.split(',') if action else (False, False)
                action_id = int(action_id) if action_id else False

                web_menus[menu['id']] = {
                    "id": menu['id'],
                    "name": menu['name'],
                    "children": menu['children'],
                    "appID": menu['app_id'],
                    "xmlid": menu['xmlid'],
                    "actionID": action_id,
                    "actionModel": action_model,
                    "svg_icon": menu.get('svg_icon'),
                    "font_icon": menu.get('font_icon'),
                    "webIcon": menu['web_icon'],
                    "webIconData": menu['web_icon_data'],
                    "is_favorite": True if favorite_cache.get(menu['id']) else False,
                    "sequence": favorite_cache.get(menu['id'], {}).sequence if favorite_cache.get(menu['id']) else 0
                }

        return web_menus

    @api.model
    # @tools.ormcache_context('self._uid', 'debug', keys=('lang',))
    def load_menus(self, debug):
        """ Loads all menu items (all applications and their sub-menus).
        :return: the menu root
        :rtype: dict('children': menu_nodes)
        """
        theme_setting = self.env["anita_theme_setting.setting_manager"].sudo().get_theme_setting()
        menu_icon_policy = theme_setting.get("menu_icon_policy", "svg_icon")

        fields = ['name', 'sequence', 'parent_id', 'action', 'web_icon']
        if menu_icon_policy == "font_icon":
            fields.append('font_icon')
        elif menu_icon_policy == "svg_icon":
            fields.append('svg_icon')
        else:
            fields.append('web_icon')
        fields.append('web_icon_data')
        
        menu_roots = self.get_user_roots()
        menu_roots_data = menu_roots.read(fields) if menu_roots else []

        menu_root = {
            'id': False,
            'name': 'root',
            'parent_id': [-1, ''],
            'children': [menu['id'] for menu in menu_roots_data],
        }

        all_menus = {'root': menu_root}

        if not menu_roots_data:
            return all_menus

        # menus are loaded fully unlike a regular tree view, cause there are a
        # limited number of items (752 when all 6.1 addons are installed)
        menus_domain = [('id', 'child_of', menu_roots.ids)]
        blacklisted_menu_ids = self._load_menus_blacklist()
        if blacklisted_menu_ids:
            menus_domain = expression.AND([menus_domain, [('id', 'not in', blacklisted_menu_ids)]])
        menus = self.search(menus_domain)
        menu_items = menus.read(fields)
        xmlids = (menu_roots + menus)._get_menuitems_xmlids()

        # add roots at the end of the sequence, so that they will overwrite
        # equivalent menu items from full menu read when put into id:item
        # mapping, resulting in children being correctly set on the roots.
        menu_items.extend(menu_roots_data)

        # set children ids and xmlids
        menu_items_map = {menu_item["id"]: menu_item for menu_item in menu_items}
        for menu_item in menu_items:
            menu_item.setdefault('children', [])

            # set the default icons
            if menu_icon_policy == "svg_icon":
                if not menu_item.get('svg_icon'):
                    menu_item["svg_icon"] = svg_icons.get(menu_item["name"], False) or False
            elif menu_icon_policy == "font_icon":
                if not menu_item.get('font_icon'):
                    menu_item["font_icon"] = font_icons.get(menu_item["name"], False) or "fa fa-circle-o"

            parent = menu_item['parent_id'] and menu_item['parent_id'][0]
            menu_item['xmlid'] = xmlids.get(menu_item['id'], "")
            if parent in menu_items_map:
                menu_items_map[parent].setdefault(
                    'children', []).append(menu_item['id'])

        all_menus.update(menu_items_map)

        # sort by sequence
        for menu_id in all_menus:
            all_menus[menu_id]['children'].sort(key=lambda id: all_menus[id]['sequence'])

        # recursively set app ids to related children
        def _set_app_id(app_id, menu):
            menu['app_id'] = app_id
            for child_id in menu['children']:
                _set_app_id(app_id, all_menus[child_id])

        for app in menu_roots_data:
            app_id = app['id']
            _set_app_id(app_id, all_menus[app_id])

        # filter out menus not related to an app (+ keep root menu)
        all_menus = {menu['id']: menu for menu in all_menus.values() if menu.get('app_id')}
        all_menus['root'] = menu_root

        return all_menus

def _tag_menuitem_extend(self, rec, parent=None):
    """
    extend tag menu item
    """
    rec_id = rec.attrib["id"]
    self._test_xml_id(rec_id)

    # The parent attribute was specified, if non-empty determine its ID, otherwise
    # explicitly make a top-level menu
    values = {
        'parent_id': False,
        'active': nodeattr2bool(rec, 'active', default=True),
    }

    if rec.get('sequence'):
        values['sequence'] = int(rec.get('sequence'))

    if parent is not None:
        values['parent_id'] = parent
    elif rec.get('parent'):
        values['parent_id'] = self.id_get(rec.attrib['parent'])
    elif rec.get('web_icon'):
        values['web_icon'] = rec.attrib['web_icon']

    if rec.get('name'):
        values['name'] = rec.attrib['name']

    if rec.get('action'):
        a_action = rec.attrib['action']

        if '.' not in a_action:
            a_action = '%s.%s' % (self.module, a_action)
        act = self.env.ref(a_action).sudo()
        values['action'] = "%s,%d" % (act.type, act.id)

        if not values.get('name') and act.type.endswith(('act_window', 'wizard', 'url', 'client', 'server')) and act.name:
            values['name'] = act.name

    if not values.get('name'):
        values['name'] = rec_id or '?'

    groups = []
    for group in rec.get('groups', '').split(','):
        if group.startswith('-'):
            group_id = self.id_get(group[1:])
            groups.append(odoo.Command.unlink(group_id))
        elif group:
            group_id = self.id_get(group)
            groups.append(odoo.Command.link(group_id))
    if groups:
        values['groups_id'] = groups

    # read font icon
    if rec.get('font_icon'):
        values['font_icon'] = rec.get('font_icon')

    if rec.get('svg_icon'):
        values['svg_icon'] = rec.get('svg_icon')

    data = {
        'xml_id': self.make_xml_id(rec_id),
        'values': values,
        'noupdate': self.noupdate,
    }
    menu = self.env['ir.ui.menu']._load_records([data], self.mode == 'update')
    for child in rec.iterchildren('menuitem'):
        self._tag_menuitem(child, parent=menu.id)

xml_import._tag_menuitem = _tag_menuitem_extend
