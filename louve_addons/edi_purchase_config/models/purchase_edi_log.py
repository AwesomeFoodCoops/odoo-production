# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.io/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


from openerp import models, api, fields


class PurchaseEdiLog(models.Model):
    _name = 'purchase.edi.log'
    _inherit = 'ir.needaction_mixin'
    _order = 'log_date desc, id desc'

    log_date = fields.Datetime(string="Log Date", required=True)
    user_id = fields.Many2one(comodel_name="res.users", string="User")
    name = fields.Char(string="Interface", required=True)
    edi_system_id = fields.Many2one(comodel_name="edi.config.system", string="EDI System", required=True)
    sent = fields.Boolean(string="Successfull ?")

    # View Section
    def _needaction_count(self, cr, uid, domain=None, context=None):
        return len(self.search(cr, uid, [('sent', '=', False)], context=context))

    @api.model
    def create_log_history(self, supplier_interface, edi_system):
        return self.create({'user_id': self.env.user.id,
                            'log_date': fields.datetime.now(),
                            'name': supplier_interface,
                            'edi_system_id': edi_system,
                            'sent': True})
