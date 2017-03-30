# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ShiftCounterEvent(models.Model):
    _name = 'shift.counter.event'
    _order = 'date desc, partner_id asc'

    TYPE_SELECTION = [
        ('standard', 'Standard'),
        ('ftop', 'FTOP'),
    ]

    name = fields.Char(
        string='Name', compute='_compute_name', store=True, select=True)

    type = fields.Selection(
        string='Type', required=True, selection=TYPE_SELECTION)

    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner', required=True,
        select=True)

    date = fields.Date(string='Date', required=True)

    point_qty = fields.Integer(string='Point Quantity', required=True)

    note = fields.Char(
        string='Note', required=True)

    @api.depends('partner_id', 'date')
    def _compute_name(self):
        for event in self:
            if event.partner_id and event.date:
                event.name = '%s - %s' % (
                    event.partner_id.name, event.date)
            else:
                event.name = ''
