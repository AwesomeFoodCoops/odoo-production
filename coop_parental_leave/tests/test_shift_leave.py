from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.tests.common import TransactionCase


class CoopshiftLeaveTest(TransactionCase):

    def setUp(self):
        super(CoopshiftLeaveTest, self).setUp()
        self.res_partner = self.env['res.partner']
        self.model_data = self.env['ir.model.data']
        self.shift_leave_type = self.env['shift.leave.type']
        self.shift_leave_obj = self.env['shift.leave']
#         Create Shift leave type
        self.shiftleave_id = self.shift_leave_type.create({
            'name': 'Congé Parental'
            })
        self.standard_member_1 = self.model_data.xmlid_to_res_id(
            'coop_shift.standard_member_1')
        self.partner_id = self.res_partner.browse(self.standard_member_1)
        self.start_date = fields.Date.today()
        self.stop_date = fields.Date.today() + timedelta(days=1)
        self.expected_birthdate = fields.Date.today() + timedelta(days=25)
        self.regular_stop_date = self.expected_birthdate + \
            relativedelta(years=1)
        self.leave = self.shift_leave_obj.create({
            'partner_id': self.partner_id.id,
            'start_date': self.start_date,
            'type_id': self.shiftleave_id.id,
            'stop_date': self.stop_date,
            'expected_birthdate': self.expected_birthdate,
            'is_parental_leave': True,
            'regular_stop_date': self.regular_stop_date,
        })

    def test_01_shif_leave_validate_email(self):
        self.leave.send_validated_parental_leave_email()

    def test_01_shif_leave_revert_stop_date(self):
        self.leave.revert_stop_date_parental_leave()

    def test_01_shif_leave_ok(self):
        self.leave.ok()
