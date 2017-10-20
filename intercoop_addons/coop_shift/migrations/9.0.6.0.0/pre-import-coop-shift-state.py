# -*- coding: utf-8 -*-


def move_all_into_new_module(cr, old_module_name, new_module_name):
    # Remove duplicated keys
    cr.execute("""
        DELETE from ir_model_data
        WHERE module=%s
        AND name in (
            SELECT name FROM ir_model_data
            WHERE module=%s);
    """, (old_module_name, new_module_name))
    # Move xml ids from old module to the new one
    cr.execute("""
        update ir_model_data
        set module=%s
        where module = %s;
       """, (new_module_name, old_module_name))


def migrate(cr, version):
    move_all_into_new_module(cr, 'coop_shift_state', 'coop_shift')
