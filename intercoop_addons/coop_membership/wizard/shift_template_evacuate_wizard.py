# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Iván Todorovich (https://twitter.com/ivantodorovich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, _
from openerp.exceptions import UserError
from dateutil.relativedelta import relativedelta

from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession

import logging
_logger = logging.getLogger(__name__)


class ShiftTemplateEvacuateWizard(models.TransientModel):
    _name = "shift.template.evacuate.wizard"
    _description = "Shift Template Evacuate Wizard"

    @api.model
    def default_get(self, fields):
        res = super(ShiftTemplateEvacuateWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model')
        if active_model == 'shift.template' and active_ids:
            res['template_ids'] = active_ids
        return res

    template_ids = fields.Many2many(
        "shift.template",
        string="Templates",
        readonly=True,
    )
    template_count = fields.Integer(
        "Selected Templates",
        compute="_compute_template_count",
    )
    date = fields.Date(
        help="The date where the changes are applied",
        default=fields.Date.today,
        required=True,
    )
    strategy = fields.Selection(
        [
            ('move to',   'Move to another template'),
            ('create',    'Create new templates'),
            ('create and move',
                'Create new templates and move participants to the childs'),
            ('move back', 'Move back to the original template'),
            ('cancel',    'Cancel registrations'),
        ],
        required=True,
        default='cancel',
    )
    validate_team_change = fields.Boolean(
        help="If not, the change teams will be created, but not executed",
    )
    mail_template_id = fields.Many2one(
        "mail.template",
        string="Notification Email Template",
        help="If not set, the default change team notification will be sent",
        domain=[('model', '=', 'shift.change.team')],
        required=False,
    )

    # move to strategy fields
    target_template_id = fields.Many2one(
        "shift.template",
        string="Target Template",
        help="Used by the 'move to' strategy",
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
    )
    interval = fields.Integer(
        'Repeat Every',
        help="Repeat every (Days/Week/Month/Year)",
        default=4,
        required=True,
    )
    quantity = fields.Integer(
        'Template Quantity',
        help="Number of templates to create",
        default=2,
        required=True,
    )
    offset = fields.Integer(
        help="Number of (interval type) to offset the created templates.\n"
             "Only used when quantity > 1.\n\n"
             "* If it's 0: The created templates will be on the same week "
             "than the original. They'll overlap.\n\n"
             "* If it's set: The created templates will be consecuently "
             "shifted the number of offset specified.",
        default=0,
    )

    @api.depends('template_ids')
    def _compute_template_count(self):
        for rec in self:
            rec.template_count = len(rec.template_ids)

    @api.model
    def _mass_change_team(
        self, registrations, target_template, date,
        validate=True, mail_template_id=None,
    ):
        """ Mass create and confirm change team objects """
        for reg in registrations:
            _logger.debug(
                'Creating shift.change.team for %s', reg.partner_id.name)
            change_team = self.env['shift.change.team'].create({
                'partner_id': reg.partner_id.id,
                'new_shift_template_id': target_template.id,
                'new_next_shift_date': date,
                'mail_template_id': mail_template_id,
            })
            if validate:
                if self.env.context.get('delay_shift_change_validation'):
                    session = ConnectorSession(self._cr, self._uid)
                    _job_validate_change_team.delay(session, change_team.ids)
                else:
                    change_team.with_context(
                        skip_sanity_checks=True,
                        delay_email=True,
                    ).button_close()

    @api.model
    def _execute_move(
        self, templates, target_template, date, validate, mail_template_id
    ):
        current_registrations = \
            self.env['shift.template.registration'].search([
                ('shift_template_id', 'in', templates.ids),
                ('is_current_participant', '=', True),
            ])
        self._mass_change_team(
            registrations=current_registrations,
            target_template=target_template,
            date=date,
            validate=validate,
            mail_template_id=mail_template_id,
        )

    @api.model
    def _execute_create(
        self, templates, rrule_type, interval, quantity, offset, date
    ):
        """
        Creates child templates using the strategy 'create'
        """
        res = {}
        for template in templates:
            # Create destination templates
            _logger.debug('Creating destination templates for: %s', template)
            child_template_ids = self.env['shift.template']
            # Get date of next shift, starting from date
            next_date = template.get_recurrent_dates(
                after=date,
                before=fields.Date.to_string(
                    fields.Date.from_string(date) + relativedelta(days=90))
            )[0]
            for i in range(0, quantity):
                # Computes the template date
                # considering the offset and rrule_type
                delay, mult = {
                    'daily': ('days', 1),
                    'weekly': ('days', 7),
                    'monthly': ('months', 1),
                    'yearly': ('years', 1),
                }[rrule_type]
                start_date = (
                    next_date +
                    relativedelta(**{delay: mult * (offset * i)})
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
                    'interval': interval,
                    'rrule_type': rrule_type,
                    'original_shift_template_id': template.id,
                })
            res[template.id] = child_template_ids
        return res

    @api.model
    def _execute_create_and_move(
        self, templates, rrule_type, interval, quantity, offset, date,
        validate, mail_template_id
    ):
        """
        This strategy was designed to migrate 4-week cycle templates
        to 8-week cycle templates.

        It'll create the new template based on the original, and move the
        participants using shift.change.team.
        """
        # Utility method: Split list in equal chunks
        def split(a, n):
            k, m = divmod(len(a), n)
            return (
                a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
                for i in range(n)
            )
        # Create child templates
        childs = self._execute_create(
            templates, rrule_type, interval, quantity, offset, date)
        for template in templates:
            # The childs for this template
            child_template_ids = childs[template.id]
            _logger.debug('Moving participants to the new templates')
            # Get the current participants
            current_registrations = \
                self.env['shift.template.registration'].search([
                    ('shift_template_id', '=', template.id),
                    ('is_current_participant', '=', True),
                ])

            chunked_registrations = \
                list(split(current_registrations, quantity))
            # Mass move them
            for i in range(0, quantity):
                self._mass_change_team(
                    registrations=chunked_registrations[i],
                    target_template=child_template_ids[i],
                    date=date,
                    validate=validate,
                    mail_template_id=mail_template_id,
                )

    @api.model
    def _execute_move_back(self, templates, date, validate, mail_template_id):
        missing_original_template_ids = templates.filtered(
            lambda rec: not rec.original_shift_template_id)
        if missing_original_template_ids:
            raise UserError(_(
                "Some templates haven't been created from another "
                "template, hence there's no relation with an original "
                "template. It's not possible to move back participants "
                "if we don't know the destination.\n\n"
                "Templates IDS: %s") % missing_original_template_ids.ids)
        # Group by original template and move one by one
        original_templates = templates.mapped('original_shift_template_id')
        for original_template in original_templates:
            templates = self.env['shift.template'].search([
                ('id', 'in', templates.ids),
                ('original_shift_template_id', '=', original_template.id),
            ])
            self.with_context(
                delay_shift_change_validation=True,
            )._execute_move(
                templates=templates,
                target_template=original_template,
                date=date,
                validate=validate,
                mail_template_id=mail_template_id,
            )

    @api.multi
    def execute(self):
        self.ensure_one()
        # If we're dealing with more than 1 template, it'll be delayed
        if len(self.template_ids) > 1:
            self = self.with_context(delay_shift_change_validation=True)
        # Strategy picker
        if self.strategy == 'move to':
            self._execute_move(
                templates=self.template_ids,
                target_template=self.target_template_id,
                date=self.date,
                validate=self.validate_team_change,
                mail_template_id=self.mail_template_id,
            )
        elif self.strategy == 'create':
            self._execute_create(
                templates=self.template_ids,
                rrule_type=self.rrule_type,
                interval=self.interval,
                quantity=self.quantity,
                offset=self.offset,
                date=self.date,
            )
        elif self.strategy == 'create and move':
            self._execute_create_and_move(
                templates=self.template_ids,
                rrule_type=self.rrule_type,
                interval=self.interval,
                quantity=self.quantity,
                offset=self.offset,
                date=self.date,
                validate=self.validate_team_change,
                mail_template_id=self.mail_template_id,
            )
        elif self.strategy == 'move back':
            self._execute_move_back(
                templates=self.template_ids,
                date=self.date,
                validate=self.validate_team_change,
                mail_template_id=self.mail_template_id,
            )
        else:
            raise UserError(_(
                "Strategy '%s' not implemented!") % self.strategy)


@job
def _job_validate_change_team(session, change_team_ids):
    session.env['shift.change.team'].browse(change_team_ids).with_context(
        skip_sanity_checks=True,
    ).button_close()
