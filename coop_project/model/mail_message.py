from datetime import timedelta
from odoo import api, fields, models, _


class MailMessage(models.Model):
    _inherit = "mail.message"

    task_description = fields.Html(
        compute="_compute_task_description",
        string="Description"
    )

    @api.multi
    def _compute_task_description(self):
        for msg in self:
            if not msg.sudo().tracking_value_ids:
                msg.task_description = msg.body
                continue
            message_values = [{'id': msg.id}]
            message_tree = dict((m.id, m) for m in msg.sudo())
            self._message_read_dict_postprocess(message_values, message_tree)
            description = _('CHANGES: <ul>')
            for vals in message_values[0].get('tracking_value_ids'):
                description += '<li>{changed_field}: {old}{new}</li>'.format(
                    changed_field=vals.get('changed_field'),
                    old=vals.get('old_value') and \
                        vals['old_value'] + ' => ' or '',
                    new=vals['new_value']
                )
            description += '</ul>'
            msg.task_description = description

