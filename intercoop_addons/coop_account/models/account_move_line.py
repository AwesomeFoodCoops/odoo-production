# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import UserError
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.queue.job import job

import logging
_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    statement_line_id = fields.Many2one(
        'account.bank.statement.line',
        related='move_id.statement_line_id',
        string='Bank Statement Line')

    @api.multi
    @api.constrains('move_id', 'account_id')
    def check_account_type_bank(self):
        for line in self:
            if line.move_id:
                line_account_bank = line.move_id.line_ids.filtered(
                        lambda a: a.account_id.reconciled_account)
                if len(line_account_bank) > 1:
                    raise UserError(_(
                        'Only one journal item on an account requiring ' +
                        'bank reconciliation can be booked in this ' +
                        'account move. It is impossible to add another ' +
                        'one. Please create a distinct account move to ' +
                        'registrer this account.move.line and its ' +
                        'counterpart.'))

    def _create_writeoff(self, vals):
        res = super(AccountMoveLine, self)._create_writeoff(vals)
        partner = self.mapped('partner_id')
        lines = res.mapped('move_id.line_ids')
        for line in lines:
            line.partner_id = partner.id if len(partner) == 1 and\
                not any(not line.partner_id for line in self)\
                else False
        return res

    @api.model
    def run_reconcile_411_pos(self, nb_lines_per_job=100):
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid,
                                   context=self.env.context)
        account_411100 = self.env['account.account'].search(
            [('code', '=', '411100')]
        )

        debit_moves_domain = [
            ('reconciled', '=', False),
            ('account_id', '=', account_411100.id),
            ('partner_id', '!=', None),
            ('debit', '>', 0),
            ('credit', '=', 0)
        ]                                   
        # Create jobs
        lines = self.search(debit_moves_domain, order='id')
        line_ids = lines.mapped('id')
        total_lines = len(line_ids)        
        job_lines = nb_lines_per_job

        number_of_jobs = int(total_lines / job_lines) + (total_lines % job_lines > 0)    
        start_line = 0
        for i in range(1, number_of_jobs + 1):
            start_line = i * job_lines - job_lines
            end_line = i * job_lines
            chunk_ids = line_ids[start_line:end_line]
            if i == number_of_jobs:
                chunk_ids = line_ids[start_line:]

            session = ConnectorSession(self._cr, self._uid,
                                       context=self.env.context)
            job_reconcile_411_pos.delay(session, 'account.move.line',
                                        chunk_ids, account_411100.id)


@job
def job_reconcile_411_pos(session, model_name, move_line_ids, a411100_id):
    ''' Reconcile account 411100'''
    AccountMoveLine = session.env[model_name]
    debit_moves_domain = [
        ('reconciled', '=', False),
        ('account_id', '=', a411100_id),
        ('partner_id', '!=', None),
        ('debit', '>', 0),
        ('credit', '=', 0),
        ('id', 'in', move_line_ids)
    ]
    # before running, we research again
    # for sure there isn't any reconciled record
    debit_moves = AccountMoveLine.search(debit_moves_domain, order='id')
    ko_plusieurs_possibilites = 0
    ko_aucune_possibilite = 0
    exactement_une_possibilite = 0
    total_a_lettrer = len(debit_moves)
    i = 0

    for debit_to_reconcile in debit_moves:
        i += 1
        _logger.info("============================")
        _logger.info(" - Avancement : %s / %s", i, total_a_lettrer)
        _logger.info(
            " - ko_plusieurs_possibilites = %s", ko_plusieurs_possibilites)
        _logger.info(
            " - ko_aucune_possibilite = %s", ko_aucune_possibilite)
        _logger.info(
            " - exactement_une_possibilite = %s", exactement_une_possibilite)
        _logger.info("     %%%%%%%% ")
        _logger.info(
            " -Ecriture de vente (debit 411100) : %s %s %s %s %s %s %s %s %s",
            debit_to_reconcile.id, debit_to_reconcile.name,
            debit_to_reconcile.date,
            debit_to_reconcile.partner_id.name, debit_to_reconcile.debit,
            debit_to_reconcile.credit, debit_to_reconcile.name,
            debit_to_reconcile.ref, debit_to_reconcile.account_id.name)

        line_to_reconcil = [debit_to_reconcile.id]

        search_critera = [
            ('reconciled', '=', False),
            ('account_id', '=', a411100_id),
            ('debit', '=', 0),
            ('credit', '>', round(debit_to_reconcile.debit-0.01, 2)),
            ('credit', '<', round(debit_to_reconcile.debit+0.01, 2)),
            ('date', '=', debit_to_reconcile.date),
            ('partner_id', '=', debit_to_reconcile.partner_id.id)]
        _logger.info(
            ">> Criteria for credit move line: %s",
            search_critera)
        credit_candidates = AccountMoveLine.search(search_critera, order='id')

        if len(credit_candidates) > 1:
            ko_plusieurs_possibilites += 1
            _logger.info("=> Several possibilities")
            _logger.info(
                ">> Number of payment lines : %s",
                len(credit_candidates))
            for payment_moveline in credit_candidates:
                _logger.info(
                    ">> Ecriture de paiement : %s %s %s %s %s %s %s %s %s",
                    payment_moveline.id, payment_moveline.name,
                    payment_moveline.date,
                    payment_moveline.partner_id.name, payment_moveline.debit,
                    payment_moveline.credit, payment_moveline.name,
                    payment_moveline.ref, payment_moveline.account_id.name)
            continue
        if len(credit_candidates) == 0:
            ko_aucune_possibilite += 1
            _logger.info("     => No possibility")
            continue
        if len(credit_candidates) == 1:
            exactement_une_possibilite += 1
            payment_moveline = credit_candidates[0]
            _logger.info(
                    ">> payment info: %s %s %s %s %s %s %s %s %s",
                    payment_moveline.id, payment_moveline.name,
                    payment_moveline.date, payment_moveline.partner_id.name,
                    payment_moveline.debit, payment_moveline.credit,
                    payment_moveline.name, payment_moveline.ref,
                    payment_moveline.account_id.name)

            line_to_reconcil.append(payment_moveline.id)
            _logger.info(
                u"         -> total %s to be reconcile with ids:  %s",
                len(line_to_reconcil), line_to_reconcil)
            reconcil_obj = session.env['account.move.line.reconcile'].with_context(active_ids=line_to_reconcil)
            reconcil_obj.trans_rec_reconcile_full()
            _logger.info(">>>> reconciled object: %s", reconcil_obj)