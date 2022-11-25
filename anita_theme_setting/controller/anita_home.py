# -*- coding: utf-8 -*-

import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo.exceptions import AccessError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.modules import get_resource_path
from odoo.tools.mimetypes import guess_mimetype
from odoo import http
from odoo.http import request

import json
import base64
import functools
import io
import os
import logging
from io import BytesIO

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
db_monodb = http.db_monodb


class AnitaHome(odoo.addons.web.controllers.main.Home):
    '''
    inhere home to extend web.login style
    '''

    @http.route('/anita_theme_setting/export_theme_style/<int:style_id>', type='http', auth="user")
    def export_theme_style(self, style_id):
        '''
        export style data
        :param style_id:
        :return:
        '''
        theme_style = request.env["anita_theme_setting.theme_style"].sudo().browse(style_id)
        data = theme_style.with_context(export_style=True).get_styles()
        return request.make_response(
            data=json.dumps(data[0]), headers=[('Content-Type', 'application/json')])

    @http.route([
            '/web/binary/company_small_logo',
            '/small_logo',
            '/small_logo.png',
        ], type='http', auth="none", cors="*")
    def company_small_logo(self, dbname=None, **kw):
        '''
        get the small logo
        :param dbname:
        :param kw:
        :return:
        '''
        imgname = 'res_company_small_logo'
        imgext = '.png'
        _get_default_image = functools.partial(
            get_resource_path, 'anita_theme_setting', 'static', 'images')
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()

        if not uid:
            uid = odoo.SUPERUSER_ID

        if not dbname:
            response = http.send_file(_get_default_image(imgname + imgext))
        else:
            try:
                cr = http.request.env._cr
                company = int(kw['company']) if kw and kw.get('company') else False
                if company:
                    cr.execute("""SELECT logo_small, write_date
                                    FROM res_company
                                    WHERE id = %s
                                """, (company,))
                else:
                    cr.execute("""SELECT c.logo_small, c.write_date
                                    FROM res_users u
                                LEFT JOIN res_company c
                                        ON c.id = u.company_id
                                    WHERE u.id = %s
                                """, (uid,))
                row = cr.fetchone()
                if row and row[0]:
                    image_base64 = base64.b64decode(row[0])
                    image_data = io.BytesIO(image_base64)
                    mimetype = guess_mimetype(image_base64, default='image/png')
                    imgext = '.' + mimetype.split('/')[1]
                    if imgext == '.svg+xml':
                        imgext = '.svg'
                    response = http.send_file(
                        image_data, filename=imgname + imgext, mimetype=mimetype, mtime=row[1])
                else:
                    response = http.send_file(_get_default_image('res_company_small_logo.png'))
            except Exception as error:
                response = http.send_file(_get_default_image(imgname + imgext))

        return response

    @http.route('/anita_theme_setting/favicon', type='http', auth="none")
    def favicon(self):
        request = http.request
        if 'uid' in request.env.context:
            user = request.env['res.users'].browse(request.env.context['uid'])
            company = user.sudo().company_id
        else:
            company = request.env['res.company'].search([], limit=1)
        favicon = company.favicon_icon
        if not favicon:
            tmp_path = get_resource_path('anita_theme_setting', 'static', 'images', 'favicon.ico')
            favicon = open(tmp_path, 'rb')
            favicon_mimetype = 'image/x-icon'
        else:
            decoded_favicon_icon = base64.b64decode(company.favicon_icon)
            favicon_mimetype = guess_mimetype(decoded_favicon_icon)
            favicon = BytesIO(decoded_favicon_icon)
        return request.make_response(
            favicon.read(), [('Content-Type', favicon_mimetype)])
