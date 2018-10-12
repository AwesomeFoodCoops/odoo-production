# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp.tests.common import TransactionCase


class TestCreateUser(TransactionCase):

    def test_create_users_for_partners(self):

        account_receivable = self.env['account.accpunt'].search(
            ['code', '=', '410000', 'user_type_id.name', '=', 'Receivable'],
            limit=1)
        account_payable = self.env['account.accpunt'].search(
            ['code', '=', '410000', 'user_type_id.name', '=', 'Payable'],
            limit=1)
        partner = self.env['res.partner'].create({
            'name': 'partner_test',
            'sex': 'male',
            'email': 'partner_test@email.com',
            'target_type': 'product_price_inv_eq',
            'property_account_receivable_id': account_receivable and
            account_receivable.id or False,
            'property_account_payable_id': account_payable and
            account_payable.id or False,
        })

        if partner:

            self.env['res.users'].create({
                'partner_id': partner.id,
                'name': partner.name,
                'login': partner.email,
                'email': partner.email
            })

        return True
