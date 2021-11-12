
from datetime import timedelta
from odoo import models, api, fields


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    ticket_seats_available = fields.Integer(compute='_compute_ticket_seats_shift')
    ticket_seats_max = fields.Integer(compute='_compute_ticket_seats_shift')
    css_color_style = fields.Char(
        compute="_compute_css_color_style"
    )

    def _compute_css_color_style(self):
        """
        - Start within 3 days:
            color: #fbd4d4; background-color: #ee2c2c;
        - More than 75% of seats are available on a future shift:
            color: #664200; background-color: #ffa500;
        - Between 50% and 75% of seats are available on a future shift:
            color: #665600; background-color: #ffd700
        - Less than 50% of seats are available on a future shift:
            color: #665b4e; background-color: #ffe4c4
        """
        today = fields.Datetime.now()
        tomorrow = today + timedelta(days=3)
        for shift in self:
            css_color_style = ''
            if shift.ticket_seats_available > 0 and \
                    shift.date_begin >= today and shift.date_begin <= tomorrow:
                css_color_style = 'color: #fbd4d4; background-color: #ee2c2c;'
            elif shift.ticket_seats_max > 0:
                available_rate = round(
                    shift.ticket_seats_available / shift.ticket_seats_max, 2)
                if available_rate > 0.75:
                    css_color_style = 'color: #664200; background-color: #ffa500;'
                elif available_rate >= 0.5:
                    css_color_style = 'color: #665600; background-color: #ffd700'
                else:
                    css_color_style = 'color: #665b4e; background-color: #ffe4c4'
            shift.css_color_style = css_color_style

    @api.multi
    @api.depends('shift_ticket_ids')
    def _compute_ticket_seats_shift(self):
        for shift in self:
            ticket_seats_available = ticket_seats_max = 0
            if shift.shift_ticket_ids:
                ticket_seats_available = sum(
                    shift.shift_ticket_ids.mapped('seats_available'))
                ticket_seats_max = sum(
                    shift.shift_ticket_ids.mapped('seats_max'))
            shift.ticket_seats_available = ticket_seats_available
            shift.ticket_seats_max = ticket_seats_max

    @api.multi
    def get_coordinators(
        self, get_alias_coordinator=False
    ):
        self.ensure_one()
        # Function return name of the coordinators with format:
        #   A, B, C, D
        shift = self
        coordinators = shift.user_ids and shift.user_ids.mapped("name") or []
        coordinators = ", ".join(coordinators) if coordinators else ""
        if get_alias_coordinator:
            # Get alias coordinator
            alias_coordinator = self.env["memberspace.alias"].search(
                [
                    ("shift_id", "=", shift.shift_template_id.id),
                    ("type", "=", "coordinator"),
                ],
                limit=1,
            )
            alias_coordinator = (
                alias_coordinator.alias_id.name_get()[0][1]
                if alias_coordinator
                else ""
            )
            return coordinators, alias_coordinator
        return coordinators
