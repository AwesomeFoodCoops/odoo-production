from .common import CoopShiftTest
from odoo.exceptions import ValidationError


class TestCoopShift(CoopShiftTest):

    def test_standard_member_event_registration(self):
        """ Test the it should create Shift Type """

        wiz = self.ShiftWizard.create({
            'date_from': self.date_from,
            'date_to': self.date_to,
            'template_ids': [(6, 0, {
                self.shift_template1
            })]
        })

        wiz.create_shifts()

        shift_id = self.Shift.search(
            [('shift_template_id', '=', self.shift_template1),
             ('state', '=', 'draft')])

        self.assertEqual(len(shift_id), 1, 'Shift: not created')
        self.assertEqual(
            shift_id[0].shift_type_id.id,
            self.shift_type_id,
            'shift type: incorrect shift type')

        # confirm shift
        shift_id.button_confirm()
        self.assertEqual(
            shift_id.state,
            'confirm',
            'Shift: confirmation of shift failed')

        # Standard member registrations for this shift
        shift_ticket_id = self.ShiftTicket.search(
            [('shift_id', '=', shift_id.id),
             ('product_id', '=', self.product_product_shift_standard)],
            limit=1)
        self.assertEqual(len(shift_ticket_id), 1, 'Shift Ticket: not created')

        test_std_reg1 = self.ShiftRegistration.create({
            'partner_id': self.standard_member_1,
            'shift_ticket_id': shift_ticket_id.id,
            'shift_id': shift_id.id,
        })

        self.assertEqual(test_std_reg1.shift_type, 'standard',
                         'Shift Type :is not standard failed')
        self.assertEqual(
            test_std_reg1.state,
            'open',
            'Shift: confirmation of registration failed')

    def test_ftop_member_event_registration(self):
        """ Test the it should create Shift Type """

        wiz = self.ShiftWizard.create({
            'date_from': self.date_from,
            'date_to': self.date_to,
            'template_ids': [(6, 0, {
                self.ftop_template_2
            })]
        })

        wiz.create_shifts()

        shift_id = self.Shift.search(
            [('shift_template_id', '=', self.ftop_template_2),
             ('state', '=', 'draft')])

        self.assertEqual(len(shift_id), 1, 'Shift: not created')
        self.assertEqual(
            shift_id[0].shift_type_id.id,
            self.shift_type_ftop_id,
            'shift type: incorrect shift type')

        # confirm shift
        shift_id.button_confirm()
        self.assertEqual(
            shift_id.state,
            'confirm',
            'Shift: confirmation of shift failed')

        # Standard member registrations for this shift
        shift_ticket_id = self.ShiftTicket.search(
            [('shift_id', '=', shift_id.id),
             ('product_id', '=', self.product_product_shift_ftop)], limit=1)
        self.assertEqual(len(shift_ticket_id), 1, 'Shift Ticket: not created')

        test_std_reg2 = self.ShiftRegistration.create({
            'partner_id': self.ftop_member_1,
            'shift_ticket_id': shift_ticket_id.id,
            'shift_id': shift_id.id,
        })

        self.assertEqual(test_std_reg2.shift_type, 'ftop',
                         'Shift Type :is not standard failed')

        self.assertEqual(
            test_std_reg2.state,
            'open',
            'Shift: confirmation of registration failed')

    def test_overlapping_registration(self):
        shift_template_ticket_id_2 = self.ShiftTemplateTicket.create({
            'name': 'Standard  2',
            'product_id': self.standard_member_1,
            'shift_template_id': self.shift_template2
        })

        self.ShiftTemplateRegistration.create({
            'partner_id': self.standard_member_1,
            'shift_ticket_id': self.shift_template_ticket_id,
            'shift_template_id': self.shift_template1,
        })
        with self.assertRaises(ValidationError):
            self.ShiftTemplateRegistration.create({
                'partner_id': self.standard_member_1,
                'shift_ticket_id': shift_template_ticket_id_2.id,
                'shift_template_id': self.shift_template2,
            })
