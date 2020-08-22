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
    if cr.fetchall():
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
        _recompute_week_number = \
            env['coop_shift.config.settings']._recompute_week_number
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
