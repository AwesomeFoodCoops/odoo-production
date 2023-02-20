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

    src_shift_id = fields.Many2one(
        comodel_name="shift.shift",
        ondelete='cascade',
    )
    src_registration_id = fields.Many2one(
        "shift.registration", "Source Registration",
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
            proposal.token_valid = False
            '''
            proposal.token_valid = bool(proposal.token) and (
                not proposal.token_expiration
                or dt <= proposal.token_expiration
            )
            '''

    @api.constrains("src_registration_id", "des_registration_id")
    def _check_amount(self):
        # This constraint check if exists any proposal have
        # src_registration_id = self.des_registration_id and
        # des_registration_id = self.src_registration_id,
        # the system will raise an error.
        if (not self.src_shift_id and (not self.src_registration_id.exchange_replacing_reg_id or \
                self.src_registration_id.exchange_state != 'in_progress')) or \
                self.des_registration_id.exchange_replacing_reg_id or \
                self.des_registration_id.exchange_state != 'in_progress':
            raise ValidationError(
                _(
                    """The shift is not available in the market. Please reload the page."""
                )
            )

    @api.model
    def create(self, vals):
        if not vals.get("src_shift_id"):
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
        return res

    @api.multi
    def send_email_request_confirm_proposal(self):
        mail_tmpl = self.env.ref("coop_memberspace.request_confirm_proposal")
        if mail_tmpl:
            for record in self:
                mail_tmpl.sudo().send_mail(record.id)
                record.send_email_request_confirm = True

    @api.multi
    def do_proposal(self):
        for rec in self:
            if rec.src_registration_id:
                rec.do_proposal_registration()
            elif rec.src_shift_id:
                rec.do_proposal_shift()

    @api.multi
    def do_proposal_shift(self):
        confirm_exchange_done_mail_tmpl = self.env.ref(
            "coop_memberspace.inform_exchange_done"
        )
        for record in self:
            if record.state != "in_progress":
                continue
            # Create new shift registration for member B
            shift_ticket_id = False
            for ticket in record.src_shift_id.shift_ticket_ids:
                if ticket.seats_available > 0:
                    shift_ticket_id = ticket.id
                    break
            if not shift_ticket_id:
                continue
            
            new_src_reg_id = self.env['shift.registration'].create({
                "shift_id": record.src_shift_id.id,
                "shift_ticket_id": shift_ticket_id,
                "partner_id": record.des_registration_id.partner_id.id,
                #"replaced_reg_id":
                #    record.src_registration_id.id,  # The old shift of member A
                "exchange_replaced_reg_id":
                    record.des_registration_id.id,  # The old shift of member B
                "tmpl_reg_line_id": record.des_registration_id.tmpl_reg_line_id.id,
                "template_created": True,
                # "state": "open",
                "exchange_state": "replacing",
            })

            # Deactive shift registration
            # to not update point counter for member B
            record.des_registration_id.write(
                {
                    # "state": "replaced",
                    # "exchange_state": "replaced",
                    # This field use to track the new shift
                    # registration that member B replaced by member A.
                    # "replacing_reg_id": new_des_reg_id.id,
                    # New shift that member B must be working on.
                    "exchange_replacing_reg_id": new_src_reg_id.id,
                    "state": "waiting",
                }
            )
            # Send email to member A to inform exchange done.
            if confirm_exchange_done_mail_tmpl:
                confirm_exchange_done_mail_tmpl.sudo().send_mail(record.id)
                record.send_email_confirm_accept_done = True
        self.write({"state": "accept"})

    @api.multi
    def do_proposal_registration(self):
        confirm_exchange_done_mail_tmpl = self.env.ref(
            "coop_memberspace.inform_exchange_done"
        )
        user_partner = self._context.get("user_partner")

        for record in self:
            if record.state != "in_progress":
                continue
            # Create new shift registration for member B
            # base on the shift registration of the member A
            if user_partner == record.src_registration_id.partner_id:
                # Partner exchanges his own shift (which exchanged by mistake before)
                record.src_registration_id.write(
                    {
                        "replaced_reg_id":
                            record.src_registration_id.id,  # The old shift of member A
                        "exchange_replaced_reg_id":
                            record.des_registration_id.id,  # The old shift of member B
                        "state": "open",
                        "exchange_state": "replacing",
                    }
                )
                new_src_reg_id = record.src_registration_id
            else:
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
                        # "exchange_replacing_reg_id": new_des_reg_id.id,
                    }
                )

            # Deactive shift registration
            # to not update point counter for member B
            record.des_registration_id.write(
                {
                    # "state": "replaced",
                    # "exchange_state": "replaced",
                    # This field use to track the new shift
                    # registration that member B replaced by member A.
                    # "replacing_reg_id": new_des_reg_id.id,
                    # New shift that member B must be working on.
                    "exchange_replacing_reg_id": new_src_reg_id.id,
                    "state": "waiting",
                }
            )
            # Send email to member A to inform exchange done.
            if confirm_exchange_done_mail_tmpl:
                confirm_exchange_done_mail_tmpl.sudo().send_mail(record.id)
                record.send_email_confirm_accept_done = True

        self.write({"state": "accept"})

    @api.multi
    def accept_proposal(self):
        return False

    @api.multi
    def refuse_proposal(self):
        return False
