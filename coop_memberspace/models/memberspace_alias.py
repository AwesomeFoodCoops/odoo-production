from odoo import models, fields, api


class MemberSpaceAlias(models.Model):
    _name = "memberspace.alias"
    _inherit = ["mail.thread"]
    _inherits = {"mail.alias": "alias_id"}

    name = fields.Char("Name", required=True)
    shift_id = fields.Many2one(
        "shift.template", "Shift Template", required=True
    )
    alias_id = fields.Many2one(
        "mail.alias",
        "Alias",
        ondelete="restrict",
        required=True,
        help="The email address associated with this alias.\
            New emails received will automatically \
            create new conversation assigned to the alias.",
    )
    type = fields.Selection(
        selection=[("coordinator", "Coordinators"), ("team", "Team")],
        string="Type",
        default="coordinator",
    )

    @api.model
    def create(self, vals):
        memberspace_alias = super(
            MemberSpaceAlias,
            self.with_context(
                alias_model_name="memberspace.conversation",
                mail_create_nolog=True,
                alias_parent_model_name=self._name,
            ),
        ).create(vals)
        memberspace_alias.alias_id.write(
            {
                "alias_parent_thread_id": memberspace_alias.id,
                "alias_defaults": {
                    "memberspace_alias_id": memberspace_alias.id
                },
            }
        )
        return memberspace_alias

    @api.multi
    def unlink(self):
        # Cascade-delete mail aliases as well
        # as they should not exist without the memberspace alias.
        aliases = self.mapped("alias_id")
        res = super(MemberSpaceAlias, self).unlink()
        aliases.unlink()
        return res
