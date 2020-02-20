from odoo.tests.common import TransactionCase
from odoo import fields


class CoopBadgeReaderTest(TransactionCase):

    def setUp(self):
        super(CoopBadgeReaderTest, self).setUp()
        self.respartner = self.env['res.partner']
        self.modeldata = self.env['ir.model.data']
        self.res_partner_alert_obj = self.env['res.partner.alert']
        self.res_partner_move_obj = self.env['res.partner.move']
        self.shift_extension_type_obj = self.env['shift.extension.type']
        self.standard_member_1 = self.modeldata.xmlid_to_res_id(
            'coop_shift.standard_member_1')
        self.partner_id = self.respartner.browse(self.standard_member_1)
        self.standard_member_2 = self.modeldata.xmlid_to_res_id(
            'coop_shift.standard_member_2')
        self.partner_id_2 = self.respartner.browse(self.standard_member_2)

    def test_01_res_partner_alert(self):
        self.res_partner_alert = self.res_partner_alert_obj.create({
            'expected_member_id': self.partner_id.id,
            'partner_ids': [(6, 0, {
                self.partner_id_2.id
            })]
        })
        self.res_partner_alert.button_close()

    def test_02_res_partner_move(self):
        self.res_partner_move = self.res_partner_move_obj.create({
            'partner_id': self.partner_id.id,
            'action': 'in',
            'cooperative_state': 'up_to_date',
            'bootstrap_cooperative_state': 'success',
        })
        self.res_partner_move.set_badge_distributed()

    def test_03_res_partner_action_grace_partner(self):
        self.partner_id.cooperative_state = 'suspended'
        self.shift_extension_type_obj.create({
            'name': 'shift_1',
            'duration': 7,
            'is_grace_period': True,
        })
        self.partner_id.action_grace_partner()
        self.partner_id.log_move('in')
        self.partner_id.set_badge_distributed()
