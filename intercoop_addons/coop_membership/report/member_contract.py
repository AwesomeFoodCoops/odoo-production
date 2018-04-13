# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime, timedelta


class report_contract_member(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(report_contract_member, self).__init__(cr, uid, name,
                                                     context=context)
        self.localcontext.update({
            "get_date_meeting": self.get_date_meeting,
        })

    def get_date_meeting(self, partner_id):
        event_reg_env = self.pool['event.registration']
        event_reg_id = event_reg_env.search(
            self.cr, self.uid, [('partner_id', '=', partner_id)],
            limit=1)
        event_reg = event_reg_env.browse(self.cr, self.uid, event_reg_id)
        if event_reg:
            return event_reg.event_id.date_begin and\
                event_reg.event_id.date_begin[:10] or False
        else:
            return False


class report_contract_member_abstract(osv.AbstractModel):
    _name = 'report.coop_membership.member_contract_template'
    _inherit = 'report.abstract_report'
    _template = 'coop_membership.member_contract_template'
    _wrapped_report_class = report_contract_member
