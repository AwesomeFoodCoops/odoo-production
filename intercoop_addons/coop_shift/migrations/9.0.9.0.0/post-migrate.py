# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, SUPERUSER_ID


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Recompute week name and number
        _recompute_week_number = \
            env['coop_shift.config.settings']._recompute_week_number
        _recompute_week_number(
            'shift_template', 'start_date', 'week_number', 'week_name')
        _recompute_week_number(
            'shift_shift', 'date_without_time', 'week_number', 'week_name')
