# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)


from openerp import api, fields, models


class AccountAssetXlsxWizard(models.TransientModel):
    _name = 'account.asset.xlsx.wizard'

    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    asset_category_ids = fields.Many2many(
        comodel_name='account.asset.category',
        string='Asset Categories'
    )

    asset_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('open', 'Running'),
            ('close', 'Close'),
        ],
        string='Status'
    )

    @api.multi
    def export_report(self):
        self.ensure_one()
        datas = dict()
        res = self.env['report'].get_action(self, "report_account_asset_xlsx")
        datas['context'] = self._context
        datas['category_datas_lst'] = self.get_category_datas()

        res.update({
            'datas': datas,
        })
        return res

    @api.multi
    def get_category_datas(self):
        self.ensure_one()
        process_datas = []
        domain = []
        if self.asset_category_ids:
            domain.append(
                ('category_id', 'in', self.asset_category_ids.ids)
            )
        if self.asset_state:
            domain.append(
                ('state', '=', self.asset_state)
            )

        read_line_fields = [
            'name',
            'state',
            'date',
            'value',
            'salvage_value',
            'value_residual',
            'method',
            'method_number',
            'prorata'
        ]

        categories = self.asset_category_ids and self.asset_category_ids or \
            self.env['account.asset.category'].search([])
        if categories:
            category_datas = {
                category: {
                    'account_asset_code': category.account_asset_id.code,
                    'category_name': category.name,
                    'lines': []
                }
                for category in categories
            }

            # Mapping selection values
            fr_context = self._context.copy()
            fr_context.update({'lang': 'fr_FR'})
            selection_field_values = self.env['account.asset.asset'].fields_get(
                ['state', 'method'], context=fr_context
            )

            account_assets = self.env['account.asset.asset'].search(
                domain, order="category_id,id")

            asset_state_dict = dict(selection_field_values['state']['selection'])
            asset_method_dict = dict(selection_field_values['method']['selection'])
            for asset in account_assets:
                asset_category = asset.category_id
                asset_data = asset.sudo().read(read_line_fields)
                line_data = asset_data and asset_data[0] or {}
                for column, value in line_data.items():
                    new_value = False
                    if column == 'state':
                        new_value = asset_state_dict.get(value, value)
                    elif column == 'method':
                        new_value = asset_method_dict.get(value, value)

                    if new_value:
                       line_data[column] = new_value

                if line_data and asset_category:
                    account_amount_values = \
                        self.get_account_amount_values(asset)
                    having_account_amount = any(
                        value != 0 for value in account_amount_values.values()
                    )
                    if not having_account_amount:
                        continue
                    line_data.update(account_amount_values)
                    category_datas[asset_category]['lines'].append(line_data)

            for category_data in category_datas.values():
                if category_data.get('lines', []):
                    process_datas.append(category_data)
        return process_datas

    @api.multi
    def get_account_amount_values(self, asset=False):
        self.ensure_one()
        account_amount_values = {}

        # Significant for account move line value
        sign = -1
        if asset:
            asset_category = asset.category_id
            category_asset_depreciation_account = \
                asset_category.account_depreciation_id

            # Calculate history and the selected range account values
            account_move_line_before = self.env['account.move.line'].search([
                ('move_id.asset_id', '=', asset.id),
                ('account_id', '=', category_asset_depreciation_account.id),
                ('date', '<', self.from_date),
            ])

            account_move_line_in_range = self.env['account.move.line'].search([
                ('move_id.asset_id', '=', asset.id),
                ('account_id', '=', category_asset_depreciation_account.id),
                ('date', '>=', self.from_date),
                ('date', "<=", self.to_date),
            ])

            amount_before = sum(
                account_move_line_before.mapped(lambda l: l.credit - l.debit)
            )

            amount_in_range = sum(
                account_move_line_in_range.mapped(lambda l: l.credit - l.debit)
            )

            account_amount_values.update({
                'amo_ant': amount_before * sign,
                'cum_amo': amount_in_range * sign,
            })
        return account_amount_values
