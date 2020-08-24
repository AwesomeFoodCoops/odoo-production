# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Iván Todorovich (https://twitter.com/ivantodorovich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, _
from openerp.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)


class ShiftTemplateOperation(models.Model):
    _name = "shift.template.operation"
    _description = "Shift Template Operation"
    _inherit = ['mail.thread']
    _order = "id desc"

    @api.model
    def default_get(self, fields):
        res = super(ShiftTemplateOperation, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model')
        if active_model == 'shift.template' and active_ids:
            res['template_ids'] = active_ids
        return res

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in progress', 'In progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
        ],
        default='draft',
        required=True,
        track_visibility="onchange",
        copy=False,
    )
    name = fields.Char(
        required=True,
        default="/",
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
    )
    description = fields.Text()
    template_ids = fields.Many2many(
        "shift.template",
        string="Templates",
        ondelete="set null",
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
        copy=False,
    )
    generated_template_ids = fields.One2many(
        "shift.template",
        "shift_template_operation_id",
        string="Generated Templates",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    change_team_ids = fields.One2many(
        "shift.change.team",
        "shift_template_operation_id",
        string="Change Teams",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    template_count = fields.Integer(
        "Selected Templates",
        compute="_compute_counts",
    )
    generated_template_count = fields.Integer(
        "Generated Templates",
        compute="_compute_counts",
    )
    change_team_count = fields.Integer(
        "Change Teams",
        compute="_compute_counts",
    )
    change_team_draft_count = fields.Integer(
        "Pending Change Teams",
        compute="_compute_counts",
    )
    change_team_error_count = fields.Integer(
        "Change Teams with errors",
        compute="_compute_counts",
    )
    change_team_done_percent = fields.Integer(
        "Completed Change Teams (%)",
        compute="_compute_counts",
    )
    date = fields.Date(
        help="The date where the changes are applied",
        default=fields.Date.today,
        required=True,
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )
    strategy = fields.Selection(
        [
            ('create',    'Split templates'),
            ('create and move', 'Split templates and move participants'),
            ('move back', 'Move back to the original template'),
            ('move to',   'Move to another template'),
            ('cancel',    'Cancel registrations'),
        ],
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )
    validate_team_change = fields.Boolean(
        help="If not, the change teams will be created, but not executed",
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )
    confirm_if_full_seats_mess = fields.Boolean(
        string="Confirm full seats warnings",
        help="Automatically ignore full seats warnings on change teams",
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )
    confirm_if_change_team_mess = fields.Boolean(
        string="Confirm date difference warnings",
        help="Automatically ignore date-related warnings on change teams",
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )
    mail_template_id = fields.Many2one(
        "mail.template",
        string="Notification Email Template",
        help="If not set, the default change team notification will be sent",
        domain=[('model', '=', 'shift.change.team')],
        required=False,
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )

    # move to strategy fields
    target_template_id = fields.Many2one(
        "shift.template",
        string="Target Template",
        help="Used by the 'move to' strategy",
        copy=False,
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
    )

    # create strategy fields
    rrule_type = fields.Selection(
        [
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('yearly', 'Year(s)'),
        ],
        string='Recurrency',
        help="Let the shift automatically repeat at that interval",
        default='weekly',
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )
    interval = fields.Integer(
        string='Repeat Every',
        help="Repeat every (Days/Week/Month/Year)",
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
        required=True,
        default=lambda self:
            int(self.env['ir.config_parameter'].sudo().get_param(
                'coop_shift.number_of_weeks_per_cycle')),
    )
    quantity = fields.Integer(
        'Split Quantity',
        help="Number of templates to create",
        default=2,
        required=True,
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )
    offset = fields.Integer(
        string="Split Recurrence Offset",
        help="Number of (interval type) to offset the created templates.\n"
             "Only used when quantity > 1.\n\n"
             "* If it's 0: The created templates will be on the same week "
             "than the original. They'll overlap.\n\n"
             "* If it's set: The created templates will be consecuently "
             "shifted the number of offset specified.",
        default=0,
        states={
            'done': [('readonly', True)],
            'in progress': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    )

    @api.model
    def create(self, vals):
        if vals.get('name') == '/':
            vals['name'] = fields.Date.context_today(self)
        return super(ShiftTemplateOperation, self).create(vals)

    @api.onchange('interval', 'quantity')
    def _onchange_interval_quantity(self):
        if not self.offset:
            if self.interval and self.quantity:
                self.offset = self.interval // self.quantity

    @api.depends('template_ids', 'generated_template_ids', 'change_team_ids')
    def _compute_counts(self):
        for rec in self:
            rec.template_count = len(rec.template_ids)
            rec.generated_template_count = len(rec.generated_template_ids)
            rec.change_team_count = len(rec.change_team_ids)
            rec.change_team_draft_count = len(
                rec.change_team_ids.filtered(lambda r: r.state == 'draft'))
            rec.change_team_error_count = len(
                rec.change_team_ids.filtered('has_delayed_execution_errors'))
            if rec.change_team_count:
                rec.change_team_done_percent = int((
                    float(rec.change_team_count - rec.change_team_draft_count)
                    / rec.change_team_count) * 100)

    @api.multi
    def action_view_templates(self):
        res = self.env.ref('coop_shift.action_shift_template').read()[0]
        res['domain'] = [('id', 'in', self.template_ids.ids)]
        return res

    @api.multi
    def action_view_generated_templates(self):
        res = self.env.ref('coop_shift.action_shift_template').read()[0]
        res['domain'] = [('shift_template_operation_id', 'in', self.ids)]
        return res

    @api.multi
    def action_view_change_teams(self):
        res = self.env.ref(
            'coop_membership.action_shift_change_teams').read()[0]
        res['domain'] = [('shift_template_operation_id', 'in', self.ids)]
        return res

    @api.multi
    def _mass_change_team(self, registrations, target_template):
        """ Mass create and confirm change team objects """
        self.ensure_one()
        for reg in registrations:
            _logger.debug(
                'Creating shift.change.team for %s', reg.partner_id.name)
            change_team = self.env['shift.change.team'].create({
                'partner_id': reg.partner_id.id,
                'new_shift_template_id': target_template.id,
                'new_next_shift_date': self.date,
                'shift_template_operation_id': self.id,
                'mail_template_id': self.mail_template_id.id,
            })
            # Automatically confirm change team warnings
            if self.confirm_if_change_team_mess:
                change_team.btn_change_team_process()
            if self.confirm_if_full_seats_mess:
                change_team.btn_full_seats_process()
            # Automatically validate
            # We skip auto validation on records that have warnings
            if (
                self.validate_team_change
                and not change_team.is_full_seats_mess
                and not change_team.is_mess_change_team
            ):
                if self.env.context.get('delay_shift_change_validation'):
                    change_team.close_delayed()
                else:
                    change_team.with_context(
                        delay_email=True,
                    ).button_close()

    @api.multi
    def _execute_move(self, templates, target_template):
        self.ensure_one()
        self._mass_change_team(
            registrations=templates.mapped('current_registration_ids'),
            target_template=target_template,
        )

    @api.multi
    def _execute_create(self):
        """
        Creates child templates using the strategy 'create'
        """
        self.ensure_one()
        res = {}
        for template in self.template_ids:
            # Create destination templates
            _logger.debug('Creating destination templates for: %s', template)
            child_template_ids = self.env['shift.template']
            # Get date of next shift, starting from date
            next_date = template.get_recurrent_dates(
                after=self.date,
                before=fields.Date.to_string(
                    fields.Date.from_string(self.date)
                    + relativedelta(days=90))
            )[0]
            for i in range(0, self.quantity):
                # Computes the template date
                # considering the offset and rrule_type
                delay, mult = {
                    'daily': ('days', 1),
                    'weekly': ('days', 7),
                    'monthly': ('months', 1),
                    'yearly': ('years', 1),
                }[self.rrule_type]
                start_date = (
                    next_date +
                    relativedelta(**{delay: mult * (self.offset * i)})
                )
                # Creates a new one
                child_template_ids += template.copy({
                    'start_datetime': fields.Datetime.to_string(
                        fields.Datetime.from_string(
                            template.start_datetime).replace(
                                year=start_date.year,
                                month=start_date.month,
                                day=start_date.day,
                            )
                        ),
                    'end_datetime': fields.Datetime.to_string(
                        fields.Datetime.from_string(
                            template.end_datetime).replace(
                                year=start_date.year,
                                month=start_date.month,
                                day=start_date.day,
                            )
                        ),
                    'interval': self.interval,
                    'rrule_type': self.rrule_type,
                    'original_shift_template_id': template.id,
                    'shift_template_operation_id': self.id,
                })
            res[template.id] = child_template_ids
        return res

    @api.multi
    def _execute_create_and_move(self):
        """
        This strategy was designed to migrate 4-week cycle templates
        to 8-week cycle templates.

        It'll create the new template based on the original, and move the
        participants using shift.change.team.
        """
        self.ensure_one()

        # Utility method: Split list in equal chunks
        def split(a, n):
            k, m = divmod(len(a), n)
            return (
                a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
                for i in range(n)
            )
        # Create child templates
        childs = self._execute_create()
        for template in self.template_ids:
            # The childs for this template
            child_template_ids = childs[template.id]
            _logger.debug('Moving participants to the new templates')
            # Get the current participants
            chunked_registrations = \
                list(split(template.current_registration_ids, self.quantity))
            # Mass move them
            for i in range(0, self.quantity):
                self._mass_change_team(
                    registrations=chunked_registrations[i],
                    target_template=child_template_ids[i],
                )

    @api.multi
    def _execute_move_back(self):
        self.ensure_one()
        missing_original_template_ids = self.template_ids.filtered(
            lambda rec: not rec.original_shift_template_id)
        if missing_original_template_ids:
            raise UserError(_(
                "Some templates haven't been created from another "
                "template, hence there's no relation with an original "
                "template. It's not possible to move back participants "
                "if we don't know the destination.\n\n"
                "Templates IDS: %s") % missing_original_template_ids.ids)
        # Group by original template and move one by one
        original_templates = self.template_ids.mapped(
            'original_shift_template_id')
        for original_template in original_templates:
            templates = self.env['shift.template'].search([
                ('id', 'in', self.template_ids.ids),
                ('original_shift_template_id', '=', original_template.id),
            ])
            self.with_context(
                delay_shift_change_validation=True,
            )._execute_move(
                templates=self.template_ids,
                target_template=original_template,
            )

    @api.multi
    def execute(self):
        self.ensure_one()
        if not self.strategy:
            raise UserError(_("Please select a strategy."))
        if not self.template_ids:
            raise UserError(_("You need to select a few templates first!"))
        # We always delay operations, they're too intensive
        self = self.with_context(delay_shift_change_validation=True)
        # Strategy picker
        if self.strategy == 'move to':
            self._execute_move(
                templates=self.template_ids,
                target_template=self.target_template_id,
            )
        elif self.strategy == 'create':
            self._execute_create()
        elif self.strategy == 'create and move':
            self._execute_create_and_move()
        elif self.strategy == 'move back':
            self._execute_move_back()
        else:
            raise UserError(_(
                "Strategy '%s' not implemented!") % self.strategy)
        # Update state
        self.state = 'in progress'

    @api.multi
    def unlink(self):
        if any([rec.state != 'draft' for rec in self]):
            raise ValidationError(_("You only delete draft operations."))

    @api.multi
    def action_close(self):
        if any(rec.change_team_draft_count > 0 for rec in self):
            raise UserError(_(
                "You can't close an operation that has pending change teams. "
                "Please process them first!"))
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        self.mapped('change_team_ids').unlink()
        self.mapped('generated_template_ids').unlink()
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
