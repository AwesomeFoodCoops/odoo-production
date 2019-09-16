from .common import CoopMembershipTest


class TestCoopMembership(CoopMembershipTest):

    def test_member_not_concerned_to_up_to_date(self):
        """Test the Member Status."""

        partner_id = self.ResPartner.browse(self.standard_member_1)

        self.assertEqual(
            partner_id.cooperative_state,
            'not_concerned', 'Member Status: not Concerned state')

        self.assertEqual(
            partner_id.is_member,
            False, 'Member: not is member False')

        wiz = self.CapitalFundWizard.create({
            'date_invoice': self.date_invoice,
            'partner_id': partner_id.id,
            'category_id': self.capital_fundraising_category_A,
            'share_qty': 120,
            'payment_journal_id': self.payment_journal_id,
            'confirm_payment': True,
            'payment_term_id': self.payment_term_id
        })

        invoice_dict = wiz.button_confirm()
        invoice = self.env[invoice_dict['res_model']].browse(
            invoice_dict['res_id'])
        self.assertEqual(invoice.is_capital_fundraising, 1)
        self.assertEqual(invoice.fundraising_category_id.id,
                         self.capital_fundraising_category_A)
        self.assertEqual(invoice.invoice_line_ids[0].quantity, 120)
        self.assertEqual(invoice.state, 'paid')

        self.assertEqual(partner_id.cooperative_state, 'unsubscribed')
        self.assertEqual(partner_id.is_member, True)

        shift_ticket_id = self.ShiftTemplateTicket.search(
            [('shift_template_id', '=', self.shift_template),
             ('shift_type', '=', 'standard')])

        self.ShiftTemplateRegLine.create({
            'shift_template_id': self.shift_template,
            'shift_ticket_id': shift_ticket_id.id,
            'partner_id': partner_id.id,
            'date_begin': self.date_invoice,
            'date_end': self.date_invoice,
        })

        self.assertEqual(partner_id.cooperative_state, 'up_to_date')
