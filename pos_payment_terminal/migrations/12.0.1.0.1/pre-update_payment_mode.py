def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        update account_journal
        set pos_terminal_payment_mode = payment_mode;
    """)
    return
