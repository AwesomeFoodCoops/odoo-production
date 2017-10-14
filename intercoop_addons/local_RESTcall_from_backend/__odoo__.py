# coding: utf-8
# Copyright 2014 Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2017 Aurélien DUMAINE <aurelien.dumaine@free.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Proxy Action',
 'version': '9.0.0.0.1',
 'author': 'Akretion,Aurélien DUMAINE',
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Generic Modules',
 'description': """This module will helps you to call REST service on local network even if youre Odoo server is out of this local newtork without any NAT or firewall rules to implement.
 """,
 'depends': [
     'base',
 ],
 'data': [
    'static/src/xml/view.xml',
 ],
 'js': [
 ],
 'installable': True,
}
