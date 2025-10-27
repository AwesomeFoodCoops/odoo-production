from odoo import api, fields, models


class Event(models.Model):
    _inherit = 'event.event'

    is_discovery_meeting = fields.Boolean('Discovery Meeting')
    room_preparation_member_ids = fields.Many2many(
        'res.partner',
        'rel_preparation_member_ids',
        string="Room preparation delegates",
        domain="[('is_member', '=', True)]",
        help="1 or 2 people to prepare the room (chairs,     tables, ...)"
    )
    leader_member_ids = fields.Many2many(
        'res.partner',
        'rel_leader_member_ids',
        string="Meeting leaders",
        domain="[('is_member', '=', True)]",
        help="1 or 2 people"
    )
    subscription_help_member_ids = fields.Many2many(
        'res.partner',
        'rel_help_member_ids',
        string="Subscription helpers",
        domain="[('is_member', '=', True)]",
        help="2 people (+ 1 or 2 members in shift)"
    )
    subscription_member_ids = fields.Many2many(
        'res.partner',
        'rel_subscription_member_ids',
        string="Subscription delegates",
        domain="[('is_member', '=', True)]",
        help="2 or 3 people"
    )
    seats_availability = fields.Selection(default='limited')
    seats_max = fields.Integer(
        default=lambda self: self._get_default_seats_max())

    @api.model
    def _get_default_seats_max(self):
        event_confg = self.env['res.config.settings'].sudo().get_values()
        return event_confg and event_confg.get('seats_max') or 0

    def _get_event_data_for_register_form(self):
        data = []
        REGISTER_USER_ID = \
            int(self.env['ir.config_parameter'].sudo(
            ).sudo().get_param('register_user_id'))
        user = self.env['res.users'].browse(REGISTER_USER_ID)

        for event in self:
            # Build address info event
            event_address = event.address_id
            street = event_address.street or ''
            zip_code = event_address.zip or ''
            city = event_address.city or ''
            address = u"{} {} {}".format(street, zip_code, city)
            # Get correct time
            date_tz = user.sudo().tz
            self_in_tz = event.with_context(tz=(date_tz or 'UTC'))
            date_begin = fields.Datetime.context_timestamp(
                self_in_tz, event.date_begin)
            data.append([event.id, address, date_begin.strftime('%d/%m/%Y %H:%M:%S'), date_begin])
        return data
