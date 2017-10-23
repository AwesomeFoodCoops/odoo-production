# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        ALTER TABLE res_partner
        DROP COLUMN IF EXISTS manual_standard_correction;
        ALTER TABLE res_partner
        DROP COLUMN IF EXISTS manual_ftop_correction;
       """)
