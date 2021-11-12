from datetime import datetime, timedelta

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ShiftRegistration(models.Model):
    _inherit = "shift.registration"

    exchange_replaced_reg_id = fields.Many2one(
        "shift.registration",
        "Exchange Registration Replaced",
        required=False,
        help="The old shift registration of the member before exchange",
    )
    exchange_replacing_reg_id = fields.Many2one(
        "shift.registration",
        "Exchange Registration Replacing",
        required=False,
        help="The new shift registration of the member after exchange",
    )

    @api.model
    def create(self, vals):
        # To check constrains limit of registration in module coop_membership
        return super(
            ShiftRegistration, self.with_context(check_limit=True)
        ).create(vals)

    @api.model
    def get_coordinators(
        self, shift_regis_id=None, get_alias_coordinator=False
    ):
        # Function return name of the coordinators with format:
        #   A, B, C, D

        # @param shift_id: Use to call function in js.
        shift = (
            shift_regis_id
            and self.browse(shift_regis_id)
            and self.browse(shift_regis_id).shift_id
            or self.shift_id
        )
        coordinators = shift.user_ids and shift.user_ids.mapped("name") or []

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
        coordinators = ", ".join(coordinators) if coordinators else ""
        if get_alias_coordinator:
            return coordinators, alias_coordinator
        return coordinators

    @api.model
    def create_proposal(self, src_registration_id, des_registration_id, src_shift_id):
        if not ((src_registration_id or src_shift_id) and des_registration_id):
            raise UserError(
                _(
                    "Source Shift Registration and "
                    + "Destination Shift Registration are require."
                )
            )
        if src_registration_id == des_registration_id:
            raise UserError(
                _(
                    "Source Shift Registration and "
                    + "Destination Shift Registration must be different."
                )
            )
        proposal = self.env["proposal"].create(
            {
                "src_shift_id": src_shift_id,
                "src_registration_id": src_registration_id,
                "des_registration_id": des_registration_id,
                "state": "in_progress",
            }
        )
        proposal.sudo().do_proposal()

    @api.multi
    def remove_shift_regis_from_market(self):
        for record in self:
            proposals = self.env["proposal"].search(
                [
                    "|",
                    ("src_registration_id", "=", record.id),
                    ("des_registration_id", "=", record.id),
                ]
            )
            if any(proposal.state == "accept" for proposal in proposals):
                raise UserError(
                    _("Your exchange was done, you cannot remove it.")
                )
            proposals.filtered(lambda r: r.state == "in_progress").write(
                {"state": "cancel"}
            )
            record.write({"exchange_state": "draft"})

    @api.multi
    def add_shift_regis_to_market(self):
        for record in self:
            if not record.check_exchangable():
                icp_sudo = self.env['ir.config_parameter'].sudo()
                shift_exchange_duration = int(icp_sudo.get_param(
                    'coop.shift.shift_exchange_duration', 24))
                return {
                    'code': 0,
                    'msg': _(
                        'You cannot propose to change the shift within {} hours before the beginning of the shift.'
                    ).format(shift_exchange_duration)
                }
            record.write({"exchange_state": "in_progress"})
        return {
            'code': 1,
        }

    @api.multi
    def shifts_to_proposal(self):
        user = self.env.user
        partner = user.partner_id
        self.ensure_one()
        shifts = self.search(
            [
                ("partner_id", "=", partner.id),
                ("state", "!=", "cancel"),
                ("exchange_state", "=", "in_progress"),
                ("exchange_replacing_reg_id", '=', False),
                (
                    "date_begin",
                    ">=",
                    datetime.now(),
                ),
            ],
            order="date_begin",
        )
        rs = []
        for shift in shifts:
            exist_proposal = self.env["proposal"].search(
                [
                    ("state", "not in", ["cancel", "refuse"]),
                    "|",
                    "&",
                    ("src_registration_id", "=", self.id),
                    ("des_registration_id", "=", shift.id),
                    "&",
                    ("src_registration_id", "=", shift.id),
                    ("des_registration_id", "=", self.id),
                ],
                limit=1,
            )
            if not exist_proposal:
                date_begin = user.get_time_by_user_lang(
                    shift.date_begin,
                    ["%A, %d %B %Hh%M", "%HH%M"],
                    lang=user.lang + ".utf8",
                )
                rs.append(
                    {
                        "id": shift.id,
                        "date": date_begin[0],
                        "hour": date_begin[1],
                    }
                )
        return rs

    def check_exchangable(self):
        self.ensure_one()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        shift_exchange_duration = int(icp_sudo.get_param(
            'coop.shift.shift_exchange_duration', 24))
        date_begin = self.date_begin - timedelta(
            hours=shift_exchange_duration)
        if date_begin < fields.Datetime.now():
            return False
        return True
