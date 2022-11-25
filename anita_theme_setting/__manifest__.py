# -*- coding: utf-8 -*-
{
    'name': "anita_theme_setting",

    'summary': """
        Theme Setting For Odoo
    """,

    'description': """
        Anita theme setting for odoo, common theme setting for odoo.
    """,

    'author': "Funenc Odoo Team",
    'website': "https://odoo.funenc.com",
    'live_test_url': "https://odoo.funenc.com",

    'category': 'Theme/Backend',
    'version': '15.0.0.10',

    'images': ['static/description/screen_shot.png',
               'static/description/banner.png',
               'static/description/banner.png'],

    'license': 'OPL-1',

    'price': 60.00,
    'currency': 'USD',
    'license': 'OPL-1',
    'depends': ['base', 'web', 'anita_theme_base'],

    'data': [
        'security/ir.model.access.csv',
        
        'views/anita_res_setting.xml',
        'views/anita_theme_mode.xml',
        'views/anita_theme_style.xml',
        'views/anita_theme_style_group.xml',
        'views/anita_theme_style_item.xml',
        'views/anita_theme_style_item_sub_group.xml',
        'views/anita_theme_var.xml',
        'views/anita_user_view.xml',
        'views/anita_company_view.xml',
        'views/anita_import_theme_style.xml',
        # 'views/anita_web.xml',
        'views/anita_background_image.xml',
        'views/anita_bk_image_wizard.xml',
    ],

    'assets': {
        'web.assets_backend': [
            ('remove', 'anita_theme_base/static/js/anita_customizer.js'),
            
            'anita_theme_setting/static/lib/bootstrap_color_picker/css/bootstrap-colorpicker.min.css',
            'anita_theme_setting/static/lib/bootstrap_color_picker/js/bootstrap-colorpicker.min.js',

            'anita_theme_setting/static/css/anita_customizer.scss',
            'anita_theme_setting/static/js/anita_customizer.js',

            'anita_theme_setting/static/css/anita_setting.scss',
            'anita_theme_setting/static/js/anita_setting.js',
            'anita_theme_setting/static/src/anita_menu_helper.js',

            'anita_theme_setting/static/js/anita_theme_editor.js',
            'anita_theme_setting/static/js/anita_theme_edit_action.js',
            'anita_theme_setting/static/src/theme_editor/anita_theme_editor.js',

            'anita_theme_setting/static/src/anita_webclient.js'
        ],

        'web.assets_qweb': [ 
            'anita_theme_setting/static/xml/customizer.xml'
        ]
    }
}
