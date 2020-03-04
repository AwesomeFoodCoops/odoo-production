# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Artem Shurshilov <shurshilov.a@yandex.ru>
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Widget image preview',
    'summary': """Adds functional preview (open/popup) image in original size 
    Enlarge image Enlarge images product images preview product images picture
    foto product photo product preview enlarge """,
    'description': """
This is extension for <field widget="image"> widget image
==============================================
* STOCK and CONTACT example:
    * open image on click in original size in popup
    * close on close button
    * close on click on/out image

""",
    'author': 'Shurshilov Artem, Druidoo',
    'website': "http://www.eurodoo.com",

    'category': "Tools",
    'version': '12.0.1.0.0',
    'depends': ['web', 'mail'],
    'license': 'AGPL-3',
    'images': [
        'static/description/stock_open2.png',
        'static/description/stock_open.png',
        'static/description/stock_cursor.png',
    ],
    'data': ['views/assets.xml'],
    'qweb': ['static/src/xml/image.xml', ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
