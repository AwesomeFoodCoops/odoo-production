# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import SUPERUSER_ID, api

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Do not do it if we already have this column
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'pos_order'
        AND column_name = 'week_name'
    """)
    if cr.fetchall():
        return

    # Avoids recomputation of new field week_name
    cr.execute("ALTER TABLE pos_session     DROP COLUMN week_number")
    cr.execute("ALTER TABLE pos_session     ADD COLUMN week_number INTEGER")
    cr.execute("ALTER TABLE pos_session     ADD COLUMN week_name VARCHAR")

    cr.execute("ALTER TABLE pos_order       DROP COLUMN week_number")
    cr.execute("ALTER TABLE pos_order       ADD COLUMN week_number INTEGER")
    cr.execute("ALTER TABLE pos_order       ADD COLUMN week_name VARCHAR")

    cr.execute("ALTER TABLE pos_order_line  DROP COLUMN week_number")
    cr.execute("ALTER TABLE pos_order_line  ADD COLUMN week_number INTEGER")
    cr.execute("ALTER TABLE pos_order_line  ADD COLUMN week_name VARCHAR")

    # populates week number
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        # Get parameters
        get_param = env['ir.config_parameter'].sudo().get_param
        weekA_date = get_param('coop_shift.week_a_date')
        n_weeks_cycle = 4  # hardcoded as this was the default value

        # Helper function
        def _recompute_week_number(
            table, field_date, field_week_number, field_week_name=None
        ):
            """
            Taken from coop_shift.config.settings
            Since this is a pre-migration script, we can't use it from env.
            That's why we copy & paste here
            """

            _logger.info(
                'Recomputing week_number and week_name for table %s', table)
            # Update week_number
            env.cr.execute("""
                UPDATE {table}
                SET {field_week_number} = (
                    1 +
                    MOD(DIV(ABS({field_date}::date - %s::date)::integer, 7),
                    %s)
                )::integer
                WHERE {field_date} IS NOT NULL
            """.format(
                table=table,
                field_date=field_date,
                field_week_number=field_week_number,
            ), (weekA_date, n_weeks_cycle))
            # Update week_name
            if field_week_name:
                env.cr.execute("""
                    UPDATE {table}
                    SET {field_week_name} = CHR(64 + {field_week_number})
                    WHERE {field_week_number} IS NOT NULL
                """.format(
                    table=table,
                    field_week_name=field_week_name,
                    field_week_number=field_week_number,
                ))

        # Update pos_session
        _recompute_week_number(
            'pos_session', 'start_at', 'week_number', 'week_name')
        # Update pos_order
        _recompute_week_number(
            'pos_order', 'date_order', 'week_number', 'week_name')
        # Update pos_order_line
        env.cr.execute("""
            UPDATE pos_order_line pol
            SET
                week_number = po.week_number,
                week_name = po.week_name,
                cycle = po.cycle
            FROM pos_order po
            WHERE pol.order_id = po.id
        """)
