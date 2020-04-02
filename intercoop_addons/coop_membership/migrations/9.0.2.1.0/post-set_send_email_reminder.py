# -*- coding: utf-8 -*-


def drop_is_unsubscribed(cr):
    cr.execute("""update shift_holiday set send_email_reminder='f' where 
    holiday_type='single_day';""")


def migrate(cr, version):
    drop_is_unsubscribed(cr)
