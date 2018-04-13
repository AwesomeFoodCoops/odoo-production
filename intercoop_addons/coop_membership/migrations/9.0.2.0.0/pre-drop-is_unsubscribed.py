# -*- coding: utf-8 -*-


def drop_is_unsubscribed(cr):
    cr.execute("""ALTER TABLE res_partner DROP COLUMN is_unsubscribed;""")


def migrate(cr, version):
    drop_is_unsubscribed(cr)
