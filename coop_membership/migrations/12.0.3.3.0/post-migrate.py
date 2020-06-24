# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Remove see associated people from Employee group
        groups_to_remove = [
            'coop_membership.group_membership_see_associated_people',
        ]
        env.ref('base.group_user').write({
            'implied_ids': [
                (3, env.ref(xmlid).id)
                for xmlid in groups_to_remove
            ]
        })
        # Don't imply any group here
        env.ref('coop_membership.group_see_contact_messeage').write({
            'implied_ids': [(5, 0)]
        })
        env.ref('coop_membership.group_membership_access_photo').write({
            'implied_ids': [(5, 0)]
        })
