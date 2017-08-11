# -*- encoding: utf-8 -*-
##############################################################################
#
##############################################################################


from openerp import fields, models


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    active = fields.Boolean(string='Active', default=True)
