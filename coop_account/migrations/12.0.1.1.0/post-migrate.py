# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    selected_journals = env['account.journal'].search([
        ('name', 'not like', '%Chèques%'),
        '|',
        ('name', 'like', 'CCOOP - compte courant'),
        ('name', 'ilike', '%cep%'),
    ])
    selected_journals.write({'export_wrong_reconciliation': True})
