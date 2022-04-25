# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class ShiftTypeMail(models.Model):
    _inherit = 'event.type.mail'
    _name = 'shift.type.mail'
    _description = 'Mail Scheduling on Shift Category'

    event_type_id = fields.Many2one(
        'shift.type', string='Event Type',
        ondelete='cascade', required=True)

class ShiftType(models.Model):
    """ Shift Type """
    _inherit = 'event.type'
    _name = 'shift.type'
    _description = 'Shift Type'

    @api.model
    def _default_to_none(self):
        return None

    name = fields.Char('Shift Type', required=True, translate=True)
    default_reply_to = fields.Char('Reply To')
    default_registration_min = fields.Integer(
        'Default Minimum Registration', default=0,
        help="""It will select this default minimum value when you choose
        this shift""")
    default_registration_max = fields.Integer(
        'Default Maximum Registration', default=0,
        help="""It will select this default maximum value when you choose
        this shift""")
    is_ftop = fields.Boolean("FTOP Shift", default=False)
    prefix_name = fields.Char(
        "Prefix Name",
        help="""this is configuration field, it uses to add prefix to
        the name of shift template or shift shift.""")
    event_type_mail_ids = fields.One2many(
        'shift.type.mail', 'event_type_id', string='Mail Schedule',
        default=_default_to_none,
        copy=False)
    event_ticket_ids = fields.One2many(default=_default_to_none)
