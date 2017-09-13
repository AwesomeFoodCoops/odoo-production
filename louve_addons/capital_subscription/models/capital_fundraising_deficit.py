# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class CapitalFundraisingDeficit(models.Model):
    _name = 'capital.fundraising.deficit'

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date")
    amount_by_share = fields.Float("Amount By Share", required=True)
    fund_cate_id = fields.Many2one(
        comodel_name="capital.fundraising.category",
        string="Fundraising Category")

    @api.model
    def create(self, vals):
        res = super(CapitalFundraisingDeficit, self).create(vals)
        res._check_overlap_dates()
        return res

    @api.multi
    def write(self, vals):
        res = super(CapitalFundraisingDeficit, self).write(vals)
        self._check_overlap_dates()
        return res

    @api.multi
    def _check_overlap_dates(self):
        for deficit_line in self:
            fund_cate = deficit_line.fund_cate_id
            start_date = deficit_line.start_date
            end_date = deficit_line.end_date

            if end_date and start_date > end_date:
                raise ValidationError(
                    _("Stop Date should be greater than "
                      "Start Date."))

            # Searching for deficit of the same category
            same_categ_deficits = self.search(
                [('fund_cate_id', '=', fund_cate.id),
                 ('id', '!=', deficit_line.id)])

            for check_deficit in same_categ_deficits:
                is_overlap = False
                if not deficit_line.end_date:
                    if not check_deficit.end_date or \
                        check_deficit.end_date >= \
                            deficit_line.start_date:
                        is_overlap = True
                else:
                    if (
                        not check_deficit.end_date and
                        check_deficit.start_date <= deficit_line.end_date
                    ) or (
                        check_deficit.end_date and
                        check_deficit.end_date >= deficit_line.start_date and
                            check_deficit.start_date <= deficit_line.end_date):
                        is_overlap = True
                if is_overlap:
                    raise ValidationError(_(
                        "You cannot have two Capital Fundraising "
                        "Deficit configuration lines that overlap"))
