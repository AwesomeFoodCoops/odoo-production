# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    nb_of_leader = fields.Integer(
        'Number of Leader',
        config_parameter="coop_shift_qualification.nb_of_leader",
        default=1
    )
