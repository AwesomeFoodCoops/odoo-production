def migrate(cr, version):
    cr.execute("""
        WITH raw_rows AS (
            SELECT a.id,
                b.journal_id
            FROM account_check_deposit a
                JOIN account_move b ON a.move_id = b.id
            WHERE a.bank_journal_id ISNULL
        )
        UPDATE account_check_deposit d
        SET bank_journal_id = raw_rows.journal_id
        FROM raw_rows
        WHERE d.id = raw_rows.id
    """)
