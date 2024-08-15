# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    store_field_stored_other_balance(cr)


def store_field_stored_other_balance(cr):
    """Store other_balance in the account move line."""
    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move_line' AND
    column_name='other_balance'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE account_move_line
            ADD COLUMN other_balance float;
            COMMENT ON COLUMN account_move_line.other_balance
            IS 'Other Balance';
            """)

    logger.info('Computing field other_balance on account.move.line')

    cr.execute(
        """
        UPDATE account_move_line
        SET other_balance = credit - debit
        """
    )
