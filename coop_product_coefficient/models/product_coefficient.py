# Copyright (C) 2015-Today: Smile (<http://www.smile.fr>)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2012-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ProductCoefficient(models.Model):
    _name = "product.coefficient"
    _order = "name"

    _SELECT_OPERATION_TYPE = [
        ("multiplier", "Multiplier"),
        ("fixed", "Fixed Amount"),
    ]

    name = fields.Char(required=True)
    value = fields.Float()
    operation_type = fields.Selection(
        selection=_SELECT_OPERATION_TYPE,
        required=True,
        default="multiplier",
    )
    active = fields.Boolean(
        help="If unchecked, it will allow you to hide"
        " the coefficient without removing it.",
        default=True,
    )
    note = fields.Text()

    # Compute Section
    @api.model
    def compute_price(self, coefficient, reference_price):
        if not coefficient:
            return reference_price
        if coefficient.operation_type == "multiplier":
            return reference_price * (1 + coefficient.value)
        return reference_price + coefficient.value
