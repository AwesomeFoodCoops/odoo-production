# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from lxml import etree
from odoo import api, fields, models
from odoo.osv.orm import setup_modifiers


class ShiftCounterEvent(models.Model):
    _inherit = 'shift.counter.event'

    holiday_id = fields.Many2one('shift.holiday', string="Holiday")
    sum_current_qty = fields.Integer(
        compute="_compute_sum_current_qty",
        string="Sum",
        store=True)

    reason_ids = fields.Many2many(
        comodel_name='shift.counter.event.reason', string='Justification')

    @api.multi
    @api.depends('point_qty', 'partner_id', 'type')
    def _compute_sum_current_qty(self):
        for record in self:
            if record.partner_id and record.type == 'ftop':
                counter_event_before = \
                    record.partner_id.counter_event_ids.filtered(
                        # lambda c: c.create_date < record.create_date
                        lambda c: c.id < record.id
                        and c.type == 'ftop')
                record.sum_current_qty = record.point_qty
                for event in counter_event_before:
                    record.sum_current_qty += event.point_qty

    @api.model
    def create(self, vals):
        record = super(ShiftCounterEvent, self).create(vals)
        self.send_unsubscribed_ftop_member_email(record.partner_id)
        return record

    @api.model
    def send_unsubscribed_ftop_member_email(self, partner):
        unsubscribed_ftop_template = \
            self.env['ir.config_parameter'].sudo().get_param(
                'coop.membership.unsubscribed.ftop.template')
        notify_un_subscription_ftpop_email = self.env.ref(
            'coop_membership.notify_un_subscription_ftpop_email')
        if partner.display_ftop_points <= -8:
            if partner.current_template_name == unsubscribed_ftop_template:
                if not partner.is_unsubscribed:
                    partner.is_unsubscribed = True
                    notify_un_subscription_ftpop_email.send_mail(partner.id)

    @api.multi
    def update_write_date(self):
        sql = '''
            UPDATE shift_counter_event
            SET write_date = create_date
            WHERE is_manual = false
        '''
        self.env.cr.execute(sql)
        return True

    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(ShiftCounterEvent, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )
        doc = etree.fromstring(res['arch'])
        access_inform = self.user_has_groups(
            'coop_membership.coop_group_access_res_partner_inform')
        if not access_inform:
            node = doc.xpath("//field[@name='reason_ids']")
            options = {
                'no_create': True,
                'no_quick_create': True,
                'no_create_edit': True
            }
            if node:
                node[0].set("options", repr(options))
                setup_modifiers(node[0], res['fields']['reason_ids'])
                res['arch'] = etree.tostring(doc)
        return res
