# -*- coding: utf-8 -*-


def migrate(cr, installed_version):
    from openerp.addons.product_history.migrations.script import \
        product_history_update_background
    product_history_update_background(cr)
