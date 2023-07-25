# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ShiftCounterEvent(models.Model):
    _name = 'shift.counter.event'
    _description = 'Shift Counter Event'
    _order = 'create_date desc, partner_id asc, id desc'

    TYPE_SELECTION = [
        ('standard', 'Standard'),
        ('ftop', 'FTOP'),
    ]

    name = fields.Char(string="Description", required=True)
    shift_id = fields.Many2one('shift.shift', string="Shift")
    type = fields.Selection(
        string='Type',
        required=True,
        selection=TYPE_SELECTION)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True)
    is_manual = fields.Boolean('Manual', readonly=True, default=True)
    point_qty = fields.Float(string='Point Quantity', required=True)
    ignored = fields.Boolean(
        string="Ignored",
        readonly=True,
        help="Don't take into account when evaluating the member's status")
    notes = fields.Text(string="Notes")
    is_changed = fields.Boolean("Changed", compute="_compute_is_changed")

    @api.model
    def create(self, vals):
        '''
        Overwrite the function to
            - Update manual update
        '''
        context = self._context
        if context.get('automatic', False):
            vals['is_manual'] = False

        return super(ShiftCounterEvent, self).create(vals)

    @api.multi
    @api.depends('create_date', 'write_date')
    def _compute_is_changed(self):
        for record in self:
            if record.create_date != record.write_date:
                record.is_changed = True
