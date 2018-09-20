# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools.safe_eval import safe_eval as eval


class MemberSpaceAlias(models.Model):
    _name = 'memberspace.alias'
    _inherit = ['mail.thread']
    _inherits = {'mail.alias': 'alias_id'}

    name = fields.Char("Name", required=True)
    shift_id = fields.Many2one(
        "shift.template", "Shift Template", required=True)
    alias_id = fields.Many2one(
        'mail.alias', 'Alias',
        ondelete="restrict", required=True,
        help="The email address associated with this alias.\
            New emails received will automatically \
            create new conversation assigned to the alias.")
    type = fields.Selection(
        selection=[('coordinator', 'Coordinators'), ('team', 'Team')],
        string="Type", default="coordinator"
    )

    def _auto_init(self, cr, context=None):
        """Installation hook to create aliases for all conversation
            and avoid constraint errors."""
        alias_context = dict(
            context, alias_model_name='memberspace.conversation')
        return self.pool.get('mail.alias').migrate_to_alias(
            cr, self._name, self._table,
            super(MemberSpaceAlias, self)._auto_init,
            'memberspace.conversation', self._columns['alias_id'],
            'name', alias_prefix='conversation+',
            alias_defaults={'memberspace_alias_id': 'id'},
            context=alias_context)

    @api.model
    def create(self, vals):
        memberspace_alias = super(MemberSpaceAlias, self.with_context(
            alias_model_name='memberspace.conversation',
            mail_create_nolog=True,
            alias_parent_model_name=self._name)).create(vals)
        memberspace_alias.alias_id.write(
            {
                'alias_parent_thread_id': memberspace_alias.id,
                "alias_defaults": {
                    'memberspace_alias_id': memberspace_alias.id
                }
            }
        )
        return memberspace_alias

    @api.multi
    def unlink(self):
        # Cascade-delete mail aliases as well
        # as they should not exist without the memberspace alias.
        aliases = self.mapped('alias_id')
        res = super(MemberSpaceAlias, self).unlink()
        aliases.unlink()
        return res
