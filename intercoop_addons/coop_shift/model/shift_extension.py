# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from dateutil.relativedelta import relativedelta


class ShiftExtension(models.Model):
    _name = 'shift.extension'
    _order = 'date_start, partner_id'

    name = fields.Char(string='Name', readonly=True)

    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner', required=True)

    type_id = fields.Many2one(
        string='Type', comodel_name='shift.extension.type', required=True)

    date_start = fields.Date(string='Begin Date', required=True)

    date_stop = fields.Date(string='End Date', required=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('shift.extension')
        return super(ShiftExtension, self).create(vals)

    @api.multi
    @api.onchange('type_id', 'date_start')
    def onchange_type_id(self):
        for extension in self:
            if extension.type_id and extension.type_id.duration\
                    and extension.date_start:
                date_start = fields.Date.from_string(extension.date_start)
                extension.date_stop = date_start +\
                    relativedelta(days=extension.type_id.duration)
