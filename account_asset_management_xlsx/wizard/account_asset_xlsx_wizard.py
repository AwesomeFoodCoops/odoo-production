# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountAssetXlsxWizard(models.TransientModel):
    _name = "account.asset.xlsx.wizard"
    _description = "Account Asset XLSX Wizard"

    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    asset_profile_ids = fields.Many2many(
        comodel_name="account.asset.profile",
        string="Asset Profiles",
    )

    asset_state = fields.Selection(
        selection=[("all", "All assets"), ("open", "Open only")],
        string="Status",
        default="all",
        required=True,
    )
    target_move = fields.Selection(
        selection=[("all", "All moves"), ("posted", "Posted moves")],
        default="all",
    )

    @api.onchange("to_date")
    def onchange_to_date(self):
        if self.to_date:
            self.from_date = str(self.to_date.year) + "-01-01"
        else:
            self.from_date = False

    @api.multi
    def export_report(self):
        self.ensure_one()
        datas = dict()
        report_name = 'account_asset_management_xlsx.report_account_asset_xlsx'
        return self.env.ref(report_name).report_action(self, data=datas)

    @api.multi
    def get_profile_datas(self):
        self.ensure_one()
        process_datas = []
        domain = []
        if self.asset_profile_ids:
            domain.append(("profile_id", "in", self.asset_profile_ids.ids))
        if self.asset_state and self.asset_state != "all":
            domain.append(("state", "=", self.asset_state))

        read_line_fields = [
            "name",
            "state",
            "date_start",
            "purchase_value",
            "salvage_value",
            "method",
            "method_number",
            "prorata",
        ]

        profiles = (
            self.asset_profile_ids
            and self.asset_profile_ids
            or self.env["account.asset.profile"].search([])
        )
        if profiles:
            profile_datas = {
                profile: {
                    "account_asset_code": profile.account_asset_id.code,
                    "profile_name": profile.name,
                    "lines": [],
                }
                for profile in profiles
            }

            # Mapping selection values
            fr_context = self._context.copy()
            fr_context.update({"lang": "fr_FR"})
            selection_field_values = (
                self.with_context(fr_context)
                .env["account.asset"]
                .fields_get(["state", "method"])
            )

            account_assets = self.env["account.asset"].search(
                domain, order="profile_id,id"
            )

            asset_state_dict = dict(
                selection_field_values["state"]["selection"]
            )
            asset_method_dict = dict(
                selection_field_values["method"]["selection"]
            )
            for asset in account_assets:
                asset_profile = asset.profile_id
                asset_data = asset.sudo().read(read_line_fields)
                line_data = asset_data and asset_data[0] or {}
                for column, value in list(line_data.items()):
                    new_value = False
                    if column == "state":
                        new_value = asset_state_dict.get(value, value)
                    elif column == "method":
                        new_value = asset_method_dict.get(value, value)

                    if new_value:
                        line_data[column] = new_value

                if line_data and asset_profile:
                    account_amount_values = self.get_account_amount_values(
                        asset
                    )
                    having_account_amount = any(
                        value != 0 for value in list(
                            account_amount_values.values())
                    )
                    if not having_account_amount:
                        continue
                    line_data.update(account_amount_values)
                    profile_datas[asset_profile]["lines"].append(line_data)

            for profile_data in list(profile_datas.values()):
                if profile_data.get("lines", []):
                    process_datas.append(profile_data)
        return process_datas

    @api.multi
    def get_account_amount_values(self, asset=False):
        self.ensure_one()
        account_amount_values = {}

        # Significant for account move line value
        sign = -1
        if asset:
            asset_profile = asset.profile_id
            profile_asset_depreciation_account = (
                asset_profile.account_depreciation_id
            )
            # Calculate history and the selected range account values
            aml_period_domain = [
                ("asset_id", "=", asset.id),
                ("account_id", "=", profile_asset_depreciation_account.id),
            ]
            state_domain = []
            if self.target_move == "posted":
                state_domain.append(("move_id.state", "=", "posted"))
                aml_period_domain += state_domain

            read_fields = ["credit", "debit"]
            aml_before_date_start = self.env["account.move.line"].search_read(
                [("date", "<", self.from_date)] + aml_period_domain,
                read_fields,
            )

            aml_in_range = self.env["account.move.line"].search_read(
                [("date", ">=", self.from_date), ("date", "<=", self.to_date)]
                + aml_period_domain,
                fields=read_fields,
            )

            amount_before_date_start = sum(
                [(l["credit"] - l["debit"]) for l in aml_before_date_start]
            )

            amount_in_range = sum(
                [(l["credit"] - l["debit"]) for l in aml_in_range]
            )

            cum_amo = amount_in_range + amount_before_date_start
            account_amount_values.update(
                {
                    "amo_ant": amount_before_date_start * sign,
                    "amo_de_lan": amount_in_range * sign,
                    "cum_amo": cum_amo * sign,
                    "value_residual": asset.purchase_value - cum_amo,
                }
            )
        return account_amount_values
