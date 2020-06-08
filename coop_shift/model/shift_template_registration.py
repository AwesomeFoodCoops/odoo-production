# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ShiftTemplateRegistration(models.Model):
    _inherit = 'event.registration'
    _name = 'shift.template.registration'
    _description = 'Attendee'
    _order = 'shift_ticket_id,name'

    event_id = fields.Many2one(required=False)
    shift_template_id = fields.Many2one(
        'shift.template', string='Template', required=True, ondelete='cascade')
    email = fields.Char(readonly=True, related='partner_id.email')
    phone = fields.Char(readonly=True, related='partner_id.phone')
    name = fields.Char(readonly=True, related='partner_id.name', store=True)
    partner_id = fields.Many2one(required=True)
    user_ids = fields.Many2many(related="shift_template_id.user_ids")
    shift_ticket_id = fields.Many2one(
        'shift.template.ticket', 'Shift Ticket', required=True,
        default=lambda rec: rec._get_default_ticket(), copy=True)
    shift_ticket_product_id = fields.Many2one(
        'product.product', 'Ticket Product',
        related='shift_ticket_id.product_id', store=True)
    line_ids = fields.One2many(
        'shift.template.registration.line', 'registration_id', string='Lines',
        default=lambda rec: rec._default_lines(), copy=True)
    state = fields.Selection()
    template_start_date = fields.Date(
        string="Template Start Date", related='shift_template_id.start_date',
        readonly=True)
    template_start_time = fields.Float(
        string="Template Start Time", related='shift_template_id.start_time',
        readonly=True)
    is_current = fields.Boolean(compute="_compute_current", multi="current")
    is_future = fields.Boolean(compute="_compute_current", multi="current")
    is_past = fields.Boolean(compute="_compute_current", multi="current")

    _sql_constraints = [(
        'template_registration_uniq',
        'unique (shift_template_id, partner_id)',
        'This partner is already registered on this Shift Template !'),
    ]

    @api.multi
    @api.constrains('shift_template_id', 'shift_ticket_product_id')
    def _check_registration_type(self):
        for rec in self:
            if rec.shift_template_id.shift_type_id == rec.env.ref(
                    'coop_shift.shift_type') and \
                    rec.shift_ticket_product_id != \
                    rec.env.ref('coop_shift.product_product_shift_standard'):
                raise ValidationError(_(
                    'Inscriptions on ABCD Templates must be Standard type!'))
            if rec.shift_template_id.shift_type_id == rec.env.ref(
                    'coop_shift.shift_type_ftop') and\
                    rec.shift_ticket_product_id != rec.env.ref(
                    'coop_shift.product_product_shift_ftop'):
                raise ValidationError(_(
                    'Inscriptions on FTOP Templates must be FTOP type!'))

    @api.multi
    @api.model
    def _compute_current(self):
        for reg in self:
            reg.is_current = any(line.is_current for line in reg.line_ids)
            if reg.is_current:
                reg.is_future = False
                reg.is_past = False
            else:
                reg.is_future = any(line.is_future for line in reg.line_ids)
                if reg.is_future:
                    reg.is_past = False
                else:
                    reg.is_past = any(line.is_past for line in reg.line_ids)

    @api.model
    def _get_default_ticket(self):
        if self.env.context.get('active_model', False) != "shift.template":
            return False
        active_id = self.env.context.get('active_id', False)
        if active_id:
            template = self.env['shift.template'].browse(
                active_id)
            if template.shift_type_id ==\
                    self.env.ref('coop_shift.shift_type'):
                return template.shift_ticket_ids.filtered(
                    lambda t, s=self: t.product_id == s.env.ref(
                        'coop_shift.product_product_shift_standard'))[0] or\
                    False
            else:
                return template.shift_ticket_ids.filtered(
                    lambda t, s=self: t.product_id == s.env.ref(
                        'coop_shift.product_product_shift_ftop'))[0] or\
                    False
        else:
            return False

    @api.model
    def _default_lines(self):
        if self.env.context.get('no_default_line', False):
            return None
        return [
            {
                'state': 'open',
                'date_begin': fields.Date.today(),
            }]

    @api.model
    def _get_state(self, date_check):
        for line in self.line_ids:
            if (
                (not line.date_begin or date_check >= line.date_begin)
                and (not line.date_end or date_check <= line.date_end)
            ):
                return line.state, line.id
        return False, False

    @api.multi
    @api.constrains('line_ids')
    def _check_dates(self):
        for reg in self:
            ok = True
            for line in reg.line_ids:
                if line.date_begin and line.date_end and\
                        line.date_begin > line.date_end:
                    raise ValidationError(_(
                        """Begin date is greater than End date:"""
                        """ \n begin: %s    end: %s    state: %s;""" % (
                            line.date_begin, line.date_end, line.state)))
                for line2 in reg.line_ids:
                    if line2 == line:
                        continue
                    b1 = line.date_begin or min(
                        line.date_end, line2.date_begin, line2.date_end)
                    b2 = line2.date_begin or min(
                        line.date_begin, line.date_end, line2.date_end)
                    e1 = line.date_end or max(
                        line.date_begin, line2.date_begin, line2.date_end)
                    e2 = line2.date_end or max(
                        line.date_begin, line.date_end, line2.date_begin)
                    if b1 <= e2 and b2 <= e1:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                raise ValidationError(_(
                    """These dates overlap:"""
                    """ \n - Line1: begin: %s    end: %s    state: %s;"""
                    """ \n - Line2: begin: %s    end: %s    state: %s;""" % (
                        line.date_begin, line.date_end, line.state,
                        line2.date_begin, line2.date_end, line2.state)))

    @api.multi
    @api.onchange("shift_template_id")
    def onchange_shift_id(self):
        standard_product = self.env.ref(
            "coop_shift.product_product_shift_standard")
        for reg in self:
            shift_ticket_ids = reg.shift_template_id.shift_ticket_ids. \
                filtered(lambda t: t.product_id == standard_product)
            if shift_ticket_ids:
                reg.shift_ticket_id = shift_ticket_ids[0]
