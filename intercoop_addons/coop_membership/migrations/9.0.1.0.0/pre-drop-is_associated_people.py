# -*- coding: utf-8 -*-


def drop_is_associated_people(cr):
    cr.execute("""ALTER TABLE res_partner DROP COLUMN is_associated_people;""")


def migrate(cr, version):
    drop_is_associated_people(cr)
