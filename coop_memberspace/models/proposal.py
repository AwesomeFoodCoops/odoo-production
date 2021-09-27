import random
from datetime import datetime, timedelta

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.SystemRandom().choice(chars) for i in range(20))


class Proposal(models.Model):
    _name = "proposal"
    _description = "Proposal exchange the shift"

    src_registration_id = fields.Many2one(
        "shift.registration", "Source Registration", required=True,
        ondelete='cascade',
    )
    des_registration_id = fields.Many2one(
        "shift.registration", "Destination Registration", required=True,
        ondelete='cascade',
    )
    state = fields.Selection(
        [
            ("in_progress", "In Progress"),  # The proposal waiting confirm.
            ("cancel", "Cancelled"),  # The proposal canceled.
            ("refuse", "Refused"),  # The proposal was refused.
            ("accept", "Accepted"),  # The proposal was accepted.
        ],
        string="Status",
        default="in_progress",
    )
    token = fields.Char(string="Token", copy=False)
    token_valid = fields.Boolean("Token Valid", compute="_compute_token_valid")
    token_expiration = fields.Datetime("Token Expiration", copy=False)
    send_email_request_confirm = fields.Boolean(
        "Email sent to request confirm."
    )
    send_email_confirm_accept_done = fields.Boolean(
        "Email sent to confirm accept done."
    )
    send_email_refuse = fields.Boolean("Email sent to inform refused")
    send_email_accept = fields.Boolean("Email sent to inform accepted")

    @api.multi
    def _compute_token_valid(self):
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for proposal in self:
            proposal.token_valid = bool(proposal.token) and (
                not proposal.token_expiration
                or dt <= proposal.token_expiration
            )

    @api.constrains("src_registration_id", "des_registration_id")
    def _check_amount(self):
        # This constraint check if exists any proposal have
        # src_registration_id = self.des_registration_id and
        # des_registration_id = self.src_registration_id,
        # the system will raise an error.
        proposal = self.search(
            [
                ("src_registration_id", "=", self.des_registration_id.id),
                ("des_registration_id", "=", self.src_registration_id.id),
                ("state", "not in", ["cancel", "refuse"]),
            ],
            limit=1,
        )
        if proposal:
            raise ValidationError(
                _(
                    """You already have a proposal from this shift.
                    Please check and accept it."""
                )
            )

    @api.model
    def create(self, vals):
        src_registration_id = vals.get("src_registration_id", False)
        src = self.env["shift.registration"].browse(src_registration_id)
        if not src or src.exchange_state != "in_progress":
            raise ValidationError(
                _("The source shift registration not ready on the market.")
            )
        try:
            IrConfig = self.env["ir.config_parameter"]
            token_expiration = (
                safe_eval(
                    IrConfig.sudo().get_param("proposal_token_expiration")
                )
                or False
            )
            if token_expiration and token_expiration < 1:
                token_expiration = False
        except Exception:
            token_expiration = False
        if token_expiration:
            token_expiration = datetime.now() + timedelta(
                hours=token_expiration
            )
            vals.update({"token_expiration": token_expiration})
        vals.update({"token": random_token()})  # Init token
        res = super(Proposal, self).create(vals)
        res.send_email_request_confirm_proposal()
        return res

    @api.multi
    def send_email_request_confirm_proposal(self):
        mail_tmpl = self.env.ref("coop_memberspace.request_confirm_proposal")
        if mail_tmpl:
            for record in self:
                mail_tmpl.sudo().send_mail(record.id)
                record.send_email_request_confirm = True

    @api.multi
    def accept_proposal(self):
        confirm_exchange_done_mail_tmpl = self.env.ref(
            "coop_memberspace.confirm_exchange_done"
        )
        proposal_accepted_mail_tmpl = self.env.ref(
            "coop_memberspace.proposal_accepted"
        )
        proposal_cancelled_mail_tmpl = self.env.ref(
            "coop_memberspace.proposal_cancelled"
        )
        for record in self:
            if record.state != "in_progress":
                continue
            # Create new shift registration for member B
            # base on the shift registration of the member A
            new_src_reg_id = record.src_registration_id.copy(
                {
                    "partner_id": record.des_registration_id.partner_id.id,
                    "replaced_reg_id":
                        record.src_registration_id.id,  # The old shift of member A
                    "exchange_replaced_reg_id":
                        record.des_registration_id.id,  # The old shift of member B
                    "tmpl_reg_line_id": record.des_registration_id.tmpl_reg_line_id.id,
                    "template_created": True,
                    "state": "open",
                    "exchange_state": "replacing",
                }
            )
            # Create new shift registration for member A
            # base on the shift registration of the member B
            new_des_reg_id = record.des_registration_id.copy(
                {
                    "partner_id": record.src_registration_id.partner_id.id,
                    "replaced_reg_id":
                        record.des_registration_id.id,  # The old shift of member B
                    "exchange_replaced_reg_id":
                        record.src_registration_id.id,  # The old shift of member A
                    "tmpl_reg_line_id":
                        record.src_registration_id.tmpl_reg_line_id.id,
                        # use the run function absent - registration.
                    "template_created":
                        True,
                        # template_created = True to subtract the
                        # point counter if member don't go to work
                    "state": "open",
                    "exchange_state": "replacing",
                }
            )

            # Deactive shift registration
            # to not update point counter for member A
            record.src_registration_id.write(
                {
                    "state": "replaced",
                    "exchange_state": "replaced",
                    # This field use to track the new shift
                    # registration that member A replaced by member B.
                    "replacing_reg_id": new_src_reg_id.id,
                    # New shift that member A must be working on.
                    "exchange_replacing_reg_id": new_des_reg_id.id,
                }
            )

            # Deactive shift registration
            # to not update point counter for member B
            record.des_registration_id.write(
                {
                    "state": "replaced",
                    "exchange_state": "replaced",
                    # This field use to track the new shift
                    # registration that member B replaced by member A.
                    "replacing_reg_id": new_des_reg_id.id,
                    # New shift that member B must be working on.
                    "exchange_replacing_reg_id": new_src_reg_id.id,
                }
            )
            # Send email to member A to inform exchange done.
            if confirm_exchange_done_mail_tmpl:
                confirm_exchange_done_mail_tmpl.sudo().send_mail(record.id)
                record.send_email_confirm_accept_done = True
            # Send email to member B to inform exchange was acceted.
            if proposal_accepted_mail_tmpl:
                proposal_accepted_mail_tmpl.sudo().send_mail(record.id)
                record.send_email_accept = True
            # Send email to others member B to inform exchange was refuse.
            others_b = self.search(
                [
                    ("id", "!=", record.id),
                    ("state", "=", "in_progress"),
                    (
                        "src_registration_id",
                        "=",
                        record.src_registration_id.id,
                    ),
                ]
            )
            others_b.write({"state": "refuse"})
            if proposal_cancelled_mail_tmpl:
                for b in others_b:
                    proposal_cancelled_mail_tmpl.send_mail(b.id)
                    b.send_email_refuse = True
            # Send email to others member that proposal to member B
            # exchange was refuse.
            others_member = self.search(
                [
                    ("state", "=", "in_progress"),
                    (
                        "src_registration_id",
                        "=",
                        record.des_registration_id.id,
                    ),
                ]
            )
            others_member.write({"state": "refuse"})
            if proposal_cancelled_mail_tmpl:
                for m in others_member:
                    proposal_cancelled_mail_tmpl.send_mail(m.id)
                    m.send_email_refuse = True
            # Cancel all proposal that member A proposal to the others member.
            others_proposal_a = self.search(
                [
                    ("state", "=", "in_progress"),
                    (
                        "des_registration_id",
                        "=",
                        record.src_registration_id.id,
                    ),
                ]
            )
            # Cancel all proposal that member B proposal to the others member.
            others_proposal_b = self.search(
                [
                    ("id", "!=", record.id),
                    ("state", "=", "in_progress"),
                    (
                        "des_registration_id",
                        "=",
                        record.des_registration_id.id,
                    ),
                ]
            )
            others_proposal = others_proposal_a | others_proposal_b
            others_proposal.write({"state": "cancel"})
        self.write({"state": "accept"})

    @api.multi
    def refuse_proposal(self):
        proposal_cancelled_mail_tmpl = self.env.ref(
            "coop_memberspace.proposal_cancelled"
        )
        self.write({"state": "refuse"})
        if proposal_cancelled_mail_tmpl:
            for record in self:
                # Send email to member B to inform exchange was refused.
                proposal_cancelled_mail_tmpl.sudo().send_mail(record.id)
                record.send_email_refuse = True
