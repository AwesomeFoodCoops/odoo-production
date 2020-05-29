# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def _remove_view_and_childs(view):
    for child in view.with_context(active_test=False).inherit_children_ids:
        _logger.info('Removing child view: %s' % child.id)
        _remove_view_and_childs(child)
    view.unlink()


def _safe_remove_view(env, xmlid):
    view_id = env.ref(xmlid, raise_if_not_found=False)
    if view_id:
        _logger.info('Removing view: %s' % xmlid)
        _remove_view_and_childs(view_id)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Migrate old sex field to new gender field
    env.cr.execute("update res_partner set gender='male' where sex='m' ")
    env.cr.execute("update res_partner set gender='female' where sex='f' ")
    env.cr.execute("update res_partner set gender='other' where sex='o' ")
    # Remove views that somehow are conflicting on module install (weird error)
    views_to_remove = [
        'coop_membership.view_res_partner_form',
        'coop_membership.view_bdm_search',
        'coop_membership.view_res_partner_form_membership',
        'coop_membership.view_res_partner_form_membership_manager',
    ]
    for view in views_to_remove:
        _safe_remove_view(env, view)
