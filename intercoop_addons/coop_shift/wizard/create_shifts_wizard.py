# -*- encoding: utf-8 -*-
##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError


class CreateShifts(models.TransientModel):
    _name = 'create.shifts.wizard'
    _description = 'Create Shifts Wizard'

    @api.model
    def _get_last_shift_date(self):
        if self.template_ids:
            return min([t.last_shift_date for t in self.template_ids])
        elif self.env.context.get('active_ids', False):
            return min([
                t.last_shift_date for t in self.env['shift.template'].browse(
                    self.env.context['active_ids'])])
        else:
            return False

    @api.model
    def _get_default_date(self):
        lsd = self.last_shift_date or self._get_last_shift_date()
        if lsd:
            lsd = datetime.strptime(lsd, "%Y-%m-%d")
            return datetime.strftime(
                lsd + timedelta(days=1), "%Y-%m-%d")
        elif self.template_ids:
            return min([t.start_date for t in self.template_ids])
        else:
            return datetime.now()

    @api.model
    def _get_selected_templates(self):
        template_ids = self.env.context.get('active_ids', False)
        if template_ids:
            return template_ids
        template_id = self.env.context.get('active_id', False)
        if template_id:
            return template_id
        return []

    template_ids = fields.Many2many(
        'shift.template', 'template_createshift_rel', 'template_id',
        'wizard_id', string="Templates", default=_get_selected_templates)
    last_shift_date = fields.Date(
        'Last created shift date', default=_get_last_shift_date)
    date_from = fields.Date(
        'Plan this Template from', default=_get_default_date)
    date_to = fields.Date('Plan this Template until')

    @api.multi
    def create_shifts(self):
        for wizard in self:
            if wizard.date_from <= wizard.last_shift_date:
                raise ValidationError(_(
                    "'From date' can't be before 'Last shift date'"))
            for template in wizard.template_ids:
                template.create_shifts_from_template(
                    after=self.date_from, before=self.date_to)
