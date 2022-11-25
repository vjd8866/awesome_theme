# -*- coding: utf-8 -*-
{
    'name': "awesome_theme_studio_patch",

    'summary': """
        this this the awesome theme studio patch, it is used to add a new menu item to the studio menu""",

    'description': """
        studio patch for awesome theme
    """,

    'author': "Funenc",
    'website': "https://www.funenc.com/?fw=2",

    'category': 'Theme/Backend',
    'version': '15.0.0.1',

    'depends': ['base', 'web_studio', 'awesome_theme_enterprise'],
    'price': 10,

    'images': [
        'static/description/awesome_description.gif',
        'static/description/awesome_screenshot.gif'
    ],

    'data': [],

    'assets': {
        'web.assets_backend': [
            'awesome_theme_studio_patch/static/css/style.scss',

            ('remove', 'web_studio/static/src/home_menu/home_menu.js'),
            ('remove', 'web_studio/static/src/systray_item/systray_item.js'),

            'awesome_theme_studio_patch/static/src/app_board_patch.js',
            'awesome_theme_studio_patch/static/src/studio_service.js',
            'awesome_theme_studio_patch/static/src/systray_item/systray_item.js',
        ],

        'web.assets_qweb': [
            ('remove', 'web_studio/static/src/home_menu/home_menu.xml'),
            'awesome_theme_studio_patch/static/xml/app_board.xml',
            'awesome_theme_studio_patch/static/src/systray_item/systray_item.xml',
        ]
    }
}
