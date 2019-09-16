from odoo import models, api


class ReportContractMemberAbstract(models.AbstractModel):
    _name = 'report.coop_membership.member_contract_template'
    _description = 'Report Coop Membership Contract Template'

    def get_date_meeting(self, partner_id):
        event_reg_env = self.env['event.registration']
        event_reg_id = event_reg_env.search(
            [('partner_id', '=', partner_id)], limit=1)

        if event_reg_id:
            return event_reg_id.event_id.date_begin and \
                event_reg_id.event_id.date_begin[:10] or False
        else:
            return False

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['res.partner'].browse(docids)
        return {
            'docs': docs,
            'event_date': self.get_date_meeting(docids[0])
        }
