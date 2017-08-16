# -*- coding: utf-8 -*-
###############################################################################
#
#   account_check_deposit for Odoo
#   Copyright (C) 2012-2016 Akretion (http://www.akretion.com/)
#   @author: Benoît GUILLOT <benoit.guillot@akretion.com>
#   @author: Chafique DELLI <chafique.delli@akretion.com>
#   @author: Alexis de Lattre <alexis.delattre@akretion.com>
#   @author: Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
#   @author: La Louve (<http://www.lalouve.net/>)
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
###############################################################################

from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    bank_acc_id = fields.Many2one('res.partner.bank', string="Bank Account")
    bank_acc_number = fields.Char(related="bank_acc_id.acc_number",
                                  readonly=True)
