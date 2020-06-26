# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Set attachments on non updatable email template
        mail_template_ftop = env.ref(
            'coop_membership.change_team_ftop_email')
        if not mail_template_ftop:
            return
        mail_template_ftop.attachment_ids = [(6, 0, [
            env.ref('coop_membership.volant_sheet_attachment').id,
            env.ref('coop_membership.volant_calendar_attachment').id,
        ])]
