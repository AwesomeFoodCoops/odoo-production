from datetime import datetime, timedelta
from odoo.tests import common
from odoo import fields


class CoopShiftTest(common.TransactionCase):
    """ Base class - Test the Coop Shift.
    """

    def setUp(self):
        super(CoopShiftTest, self).setUp()

        ModelData = self.env['ir.model.data']
        self.ShiftWizard = self.env['create.shifts.wizard']
        self.Shift = self.env['shift.shift']
        self.ShiftRegistration = self.env['shift.registration']
        self.ShiftTemplateRegistration = self.env['shift.template.registration']
        self.ShiftTicket = self.env['shift.ticket']
        self.ShiftTemplateTicket = self.env['shift.template.ticket']
        self.ResPartner = self.env['res.partner']

        # Standard Template
        self.shift_template1 = ModelData.xmlid_to_res_id(
            'coop_shift.standard_template_1')

        self.shift_template2 = ModelData.xmlid_to_res_id(
            'coop_shift.standard_template_2')

        self.ftop_template_2 = ModelData.xmlid_to_res_id(
            'coop_shift.ftop_template_2')

        self.standard_member_1 = ModelData.xmlid_to_res_id(
            'coop_shift.standard_member_1')

        self.ftop_member_1 = ModelData.xmlid_to_res_id(
            'coop_shift.ftop_member')

        self.date_from = fields.Date.to_string(datetime.today())
        self.date_to = fields.Date.to_string(
            datetime.today() + timedelta(days=1))

        self.shift_type_id = ModelData.xmlid_to_res_id(
            'coop_shift.shift_type')

        self.shift_type_ftop_id = ModelData.xmlid_to_res_id(
            'coop_shift.shift_type_ftop')

        self.product_product_shift_standard = ModelData.xmlid_to_res_id(
            'coop_shift.product_product_shift_standard')

        self.product_product_shift_ftop = ModelData.xmlid_to_res_id(
            'coop_shift.product_product_shift_ftop')

        self.shift_template_ticket_id = ModelData.xmlid_to_res_id(
            'coop_shift.template_ticket_1_standard')
