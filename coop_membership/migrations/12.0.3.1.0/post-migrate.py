# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    '''
    Fix wrong setup of BDM groups.
    If an user has a BDM Group, and also a membership user group.
    Remove the BDM group from the user
    '''
    env = api.Environment(cr, SUPERUSER_ID, {})
    users = env['res.users'].with_context(active_test=False).search([])
    group_bdm_lecture_id = env.ref(
        'coop_membership.group_membership_bdm_lecture').id
    group_bdm_presence_id = env.ref(
        'coop_membership.group_membership_bdm_presence').id
    group_bdm_saisie_id = env.ref(
        'coop_membership.group_membership_bdm_saisie').id
    for user in users:
        if (
            user.has_group('coop_membership.group_membership_bdm_lecture')
            and user.has_group('coop_membership.group_membership_access_user')
        ):
            _logger.info("Removing BDM groups from: %s" % user.name)
            user.write({
                'groups_id': [
                    (3, group_bdm_lecture_id),
                    (3, group_bdm_presence_id),
                    (3, group_bdm_saisie_id),
                ]
            })
