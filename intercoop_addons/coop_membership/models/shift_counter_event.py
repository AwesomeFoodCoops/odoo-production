# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from lxml import etree
from openerp import api, fields, models, _
from openerp.osv.orm import setup_modifiers


class ShiftCounterEvent(models.Model):
    _inherit = 'shift.counter.event'

    holiday_id = fields.Many2one('shift.holiday', string="Holiday")
    sum_current_qty = fields.Integer(
        compute="compute_sum_current_qty",
        string="Sum",
        store=True)

    reason_ids = fields.Many2many(
        comodel_name='shift.counter.event.reason', string='Justification')

    @api.multi
    @api.depends('point_qty', 'partner_id', 'type')
    def compute_sum_current_qty(self):
        for record in self:
            if record.partner_id and record.type == 'ftop':
                counter_event_before =\
                    record.partner_id.counter_event_ids.filtered(
                        lambda c: c.create_date < record.create_date
                        and c.type == 'ftop')
                record.sum_current_qty = record.point_qty
                for event in counter_event_before:
                    record.sum_current_qty += event.point_qty

    @api.multi
    def update_write_date(self):
        sql = '''
            UPDATE shift_counter_event
            SET write_date = create_date
            WHERE is_manual = false
        '''
        self.env.cr.execute(sql)
        return True

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(ShiftCounterEvent, self).fields_view_get(
            cr, uid,
            view_id=view_id,
            view_type=view_type,
            context=context,
            toolbar=toolbar,
            submenu=submenu
        )
        doc = etree.fromstring(res['arch'])
        access_inform = self.user_has_groups(
            cr, uid,
            'coop_membership.coop_group_access_res_partner_inform'
        )
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
