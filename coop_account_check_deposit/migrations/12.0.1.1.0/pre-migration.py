def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        update account_check_deposit
        set bank_journal_id = journal_destination_id;
    """)
