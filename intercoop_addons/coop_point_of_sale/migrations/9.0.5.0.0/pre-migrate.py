# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import SUPERUSER_ID, api


def migrate(cr, version):
    # Do not do it if we already have this column
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'pos_order'
        AND column_name = 'week_name'
    """)
    if env.cr.fetchall():
        return

    # Avoids recomputation of new field week_name
    cr.execute("ALTER TABLE pos_session     ADD COLUMN week_name VARCHAR")
    cr.execute("UPDATE      pos_session     SET week_name = week_number")
    cr.execute("ALTER TABLE pos_session     DROP COLUMN week_number")
    cr.execute("ALTER TABLE pos_session     ADD COLUMN week_number INTEGER")

    cr.execute("ALTER TABLE pos_order       ADD COLUMN week_name VARCHAR")
    cr.execute("UPDATE      pos_order       SET week_name = week_number")
    cr.execute("ALTER TABLE pos_order       DROP COLUMN week_number")
    cr.execute("ALTER TABLE pos_order       ADD COLUMN week_number INTEGER")

    cr.execute("ALTER TABLE pos_order_line  ADD COLUMN week_name VARCHAR")
    cr.execute("UPDATE      pos_order_line  SET week_name = week_number")
    cr.execute("ALTER TABLE pos_order_line  DROP COLUMN week_number")
    cr.execute("ALTER TABLE pos_order_line  ADD COLUMN week_number INTEGER")

    # populates week number
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        get_param = env['ir.config_parameter'].sudo().get_param
        weekA_date = get_param('coop_shift.week_a_date')
        n_weeks_cycle = int(get_param('coop_shift.number_of_weeks_per_cycle'))

        # helper function
        def _recompute_week_number(table, field_name, target_field):
            env.cr.execute("""
                UPDATE {table}
                SET {target_field} = (
                    1 +
                    MOD(DIV(ABS(
                        DATE_PART('day', AGE(%s, {field_name}))
                    )::integer, 7), %s))::integer
                WHERE {field_name} IS NOT NULL
            """.format(
                table=table,
                field_name=field_name,
                target_field=target_field,
            ), (weekA_date, n_weeks_cycle))

        _recompute_week_number(
            table='pos_session',
            field_name='start_at',
            target_field='week_number')
        _recompute_week_number(
            table='pos_order',
            field_name='date_order',
            target_field='week_number')
