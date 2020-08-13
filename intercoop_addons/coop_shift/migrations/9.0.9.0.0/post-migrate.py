# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Compute new week_name field
        _logger.info("Computing week_name in shift.template..")
        env['shift.template'].with_context(
            active_test=False,
        ).search([])._compute_week_name()
        _logger.info("Computing week_name in shift.shift..")
        env['shift.shift'].with_context(
            active_test=False,
        ).search([])._compute_week_name()
