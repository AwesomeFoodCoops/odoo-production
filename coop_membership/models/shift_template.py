# Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class ShiftTemplate(models.Model):
    _inherit = 'shift.template'

    user_ids = fields.Many2many(
        domain=[('is_worker_member', '=', True)],
    )
    warning_leader_unsubscribed = fields.Html(
        compute="_compute_warning_leader_unsubscribed",
        string="Warning unsubscribed leader",
        store=True,
    )
    current_registration_ids = fields.Many2many(
        "shift.template.registration",
        compute="_compute_current_registration_ids",
    )
    registration_qty = fields.Integer(
        string='Number of Attendees',
        compute='_compute_registration_qty',
    )
    required_skill_ids = fields.Many2many(
        'hr.skill',
        string="Required Skills",
        domain=[('child_ids', '=', False)],
    )
    original_shift_template_id = fields.Many2one(
        "shift.template",
        string="Original Template",
        help="The template from which this template was created, using "
             "the Shift Template Evacuate Wizard.\n\n"
             "It's used to execute the 'move back' strategy",
        ondelete="set null",
    )
    shift_template_operation_id = fields.Many2one(
        "shift.template.operation",
        string="Template Operation",
        readonly=True,
        ondelete="set null",
    )

    # This field help to re-add member as a leader after his/her leave
    removed_user_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='removed_res_partner_shift_template_rel',
        column1='shift_template_id',
        column2='partner_id',
        string='Removed Leaders'
    )

    @api.multi
    @api.depends('registration_ids')
    def _compute_current_registration_ids(self):
        for rec in self:
            rec.current_registration_ids = \
                rec.registration_ids.filtered('is_current_participant')

    @api.multi
    @api.depends('current_registration_ids')
    def _compute_registration_qty(self):
        for rec in self:
            rec.registration_qty = len(rec.current_registration_ids)

    @api.multi
    @api.depends('user_ids', 'user_ids.is_unsubscribed')
    def _compute_warning_leader_unsubscribed(self):
        for template in self:
            if len(template.user_ids) == 1 and \
                    template.user_ids[0].is_unsubscribed:
                template.warning_leader_unsubscribed = (_(
                    "Please choose another leader because" +
                    " the current leader is unsubscribed"))
            else:
                template.warning_leader_unsubscribed = False
