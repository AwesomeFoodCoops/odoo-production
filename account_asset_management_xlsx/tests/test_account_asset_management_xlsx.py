from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase
from odoo import fields


class TestAccountAssetReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.journal = self.env['account.journal'].search(
            [('type', '=', 'general')], limit=1)
        account_obj = self.env['account.account']
        self.asset_account = account_obj.search(
            [('user_type_id.name', '=', 'Current Assets')], limit=1)
        self.depr_account = account_obj.search(
            [('user_type_id.name', '=', 'Depreciation')], limit=1)
        if not self.depr_account:
            self.depr_account = account_obj.create({
                'name': 'Test Depreciation Account',
                'code': 'TDA1',
                'user_type_id': self.env['account.account.type'].search(
                    [('name', '=', 'Depreciation')], limit=1
                ).id,
            })
        self.expense_depr_account = account_obj.search(
            [('user_type_id.name', '=', 'Expenses')], limit=1)
        self.asset_profile = self.env['account.asset.profile'].create({
            'name': 'Test Asset Profile',
            'journal_id': self.journal.id,
            'account_asset_id': self.asset_account.id,
            'account_depreciation_id': self.depr_account.id,
            'account_expense_depreciation_id': self.expense_depr_account.id,
        })
        self.asset_1 = self.env['account.asset'].create({
            'name': 'Test Asset1',
            'purchase_value': 100000.00,
            'profile_id': self.asset_profile.id,
            'date_start':
            str((fields.Date.today() - relativedelta(years=1)).year) +
            "-01-01",
        })
        self.asset_1.validate()
        self.asset_1.compute_depreciation_board()
        self.asset_1._compute_entries(fields.Date.today())

        self.asset_2 = self.env['account.asset'].create({
            'name': 'Test Asset2',
            'purchase_value': 200000.00,
            'profile_id': self.asset_profile.id,
            'date_start':
                str((fields.Date.today() - relativedelta(years=2)).year) +
                "-01-01",
        })
        self.asset_2.validate()
        self.asset_2.compute_depreciation_board()
        self.asset_2._compute_entries(fields.Date.today())

    def test_001_asset_report(self):
        wiz_obj = self.env['account.asset.xlsx.wizard']
        wiz_new = wiz_obj.new({
            'to_date': fields.Date.today(),
            'asset_state': 'all',
            'target_move': 'all',
            'asset_profile_ids': [(6, 0, [self.asset_profile.id])],
        })
        wiz_new.onchange_to_date()
        wiz_rec = wiz_obj.create(wiz_new._convert_to_write(wiz_new._cache))
        profile_datas_lst = wiz_rec.get_profile_datas()
        asset1 = profile_datas_lst[0].get('lines')[0]
        asset2 = profile_datas_lst[0].get('lines')[1]

        self.assertEqual(asset1['value_residual'], 80000.00,
                         'Residual Amount for Asset1 must be 80000.00!')
        self.assertEqual(asset2['value_residual'], 120000.00,
                         'Residual Amount for Asset1 must be 120000.00!')
