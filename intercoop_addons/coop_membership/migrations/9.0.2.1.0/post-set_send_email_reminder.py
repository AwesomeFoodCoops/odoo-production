# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
    UPDATE shift_holiday
    SET send_email_reminder = 'f'
    WHERE holiday_type = 'single_day';
    """)
