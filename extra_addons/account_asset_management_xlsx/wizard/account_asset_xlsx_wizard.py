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
            ('all', 'All assets'),
            ('open', 'Open only'),
        ],
        string='Status',
        default='all',
        required=True
    )
    target_move = fields.Selection(
        selection=[
            ('all', 'All moves'),
            ('posted', 'Posted moves'),
        ],
        default='all'
    )

    @api.onchange('to_date')
    def onchange_to_date(self):
        if self.to_date:
            self.from_date = self.to_date[:5] + '01-01'
        else:
            self.from_date = False

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
        if self.asset_state and self.asset_state != 'all':
            domain.append(
                ('state', '=', self.asset_state)
            )

        read_line_fields = [
            'name',
            'state',
            'date',
            'value',
            'salvage_value',
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
            selection_field_values = self.with_context(fr_context).env[
                'account.asset.asset'].fields_get(
                    ['state', 'method'], context=fr_context
            )

            account_assets = self.env['account.asset.asset'].search(
                domain, order="category_id,id")

            asset_state_dict = dict(
                selection_field_values['state']['selection'])
            asset_method_dict = dict(
                selection_field_values['method']['selection'])
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
            fixed_asset_account_type = self.env.ref(
                'account.data_account_type_fixed_assets')

            # Calculate history and the selected range account values
            aml_period_domain = [
                ('move_id.asset_id', '=', asset.id),
                ('account_id', '=', category_asset_depreciation_account.id),
            ]
            state_domain = []
            if self.target_move == 'posted':
                state_domain.append(
                    ('move_id.state', '=', 'posted')
                )
                aml_period_domain += state_domain

            read_fields = ['credit', 'debit']
            aml_before_date_start = self.env['account.move.line'].search_read([
                ('date', '<', self.from_date),
            ] + aml_period_domain, fields=read_fields)

            aml_in_range = self.env['account.move.line'].search_read([
                ('date', '>=', self.from_date),
                ('date', "<=", self.to_date),
            ] + aml_period_domain, fields=read_fields)

            amount_before_date_start = sum(
                [(l['credit'] - l['debit']) for l in aml_before_date_start]
            )

            amount_in_range = sum(
                [(l['credit'] - l['debit']) for l in aml_in_range]
            )

            cum_amo = amount_in_range + amount_before_date_start
            account_amount_values.update({
                'amo_ant': amount_before_date_start * sign,
                'amo_de_lan': amount_in_range * sign,
                'cum_amo': cum_amo * sign,
                'value_residual': asset.value - cum_amo,
            })
        return account_amount_values
