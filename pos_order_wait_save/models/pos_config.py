# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    order_wait_save_timeout = fields.Float(
        "Wait order to be saved",
        default=7.5,
        help=(
            "Number of seconds to wait for the order to be saved "
            "before printing the ticket.\n"
            "Set to 0 to disable."
        ),
    )
