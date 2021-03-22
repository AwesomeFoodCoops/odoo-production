# -*- coding: utf-8 -*-

import json
from openerp import api, models, fields, _
from openerp.exceptions import UserError, Warning
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
    other_balance = fields.Monetary(
        string='Other Balance',
        default=0.0)

    @api.model
    def create(self, vals):
        debit = vals.get('debit', 0)
        credit = vals.get('credit', 0)
        vals.update({
            'other_balance': credit - debit
        })
        return super(AccountMoveLine, self).create(vals)

    @api.multi
    def write(self, vals):
        self.calculate_orther_balance(vals)
        return super(AccountMoveLine, self).write(vals)

    @api.multi
    def calculate_orther_balance(self, vals):
        for record in self:
            if 'debit' in vals or 'credit' in vals:
                debit = vals.get('debit', record.debit)
                credit = vals.get('credit', record.credit)
                vals.update({
                    'other_balance': credit - debit,
                })
        return True

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

    @api.multi
    def unmatch_bankstatement_wizard(self):
        active_ids = self._context.get('active_ids', [])
        active_model = self._context.get('active_model', [])

        view_id = self.env.ref(
            'coop_account.view_unmatch_bank_statement_wizard_form')

        mess_confirm = _('Are you sure you want to unmatch %s transactions?') %\
            (len(active_ids))

        wizard = self.env['unmatch.bank.statement.wizard'].create({
            'mess_confirm': mess_confirm
        })

        return {
            'name': _('Unmatch Bank Statement'),
            'type': 'ir.actions.act_window',
            'view_id': view_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wizard.id,
            'res_model': 'unmatch.bank.statement.wizard',
            'target': 'new',
            'context': {'active_ids': active_ids, 'active_model': active_model}
        }

    @api.model
    def export_wrong_reconciliation_ml(self):
        wrong_reconciliation_ml_data = self.get_wrong_reconciliation_ml_data()
        data = {
            'model': self._name,
            'headers': wrong_reconciliation_ml_data['headers'],
            'rows': wrong_reconciliation_ml_data['rows']
        }
        return json.dumps(data)

    @api.model
    def get_wrong_reconciliation_ml_data(self):
        read_columns = [
            'name', 'journal_id', 'ref', 'date', 'partner_id', 'company_id',
            'check_holder_name', 'account_id', 'move_id', 'debit', 'credit',
            'quantity', 'statement_line_id', 'statement_id', 'payment_id',
            'check_deposit_id'
        ]
        model_fields = self._fields
        header_columns = [getattr(model_fields[column], 'string') for column in read_columns]
        header_columns = ['External ID'] + header_columns
        read_columns = ['id'] + read_columns
        wrong_move_lines = self.get_wrong_reconciliation_ml()
        if not wrong_move_lines:
            raise Warning(_('Found no wrong account move lines.'))
        record_values_dict = wrong_move_lines.export_data(read_columns)
        converted_data_rows = [
            [unicode(cell_data) for cell_data in data_row]
            for data_row in record_values_dict['datas']
        ]
        return {
            'rows': converted_data_rows,
            'headers': header_columns,
        }

    @api.model
    def get_wrong_reconciliation_ml(self):
        wrong_move_lines = self
        selected_journals = self.env['account.journal'].search([
            ('name', 'not like', '%Chèques%'),
            '|',
            ('name', 'like', 'CCOOP - compte courant'),
            ('name', 'ilike', '%cep%'),
        ])
        bank_statement_line_query = """
            select statement_line_id
            from account_move
            where statement_line_id is not null and journal_id in {} 
            group by statement_line_id
            having count(statement_line_id) > 1
        """.format(tuple(selected_journals.ids))

        self.env.cr.execute(bank_statement_line_query)
        results = self.env.cr.fetchall()
        line_ids = [id_tuple[0] for id_tuple in results]
        bank_statement_line_ids = self.env['account.bank.statement.line']\
            .browse(line_ids)
        for stml in bank_statement_line_ids:
            stml_date = fields.Date.from_string(stml.date)
            move_ids = stml.journal_entry_ids
            move_line_ids = move_ids.mapped('line_ids')
            if len(move_ids) == 1 and len(move_line_ids) == 2:
                continue
            for aml in move_line_ids.filtered(lambda ml: not ml.statement_id):
                aml_date = fields.Date.from_string(aml.date)
                if aml_date.year <= stml_date.year and \
                        aml_date.month <= stml_date.month:
                    continue
                else:
                    wrong_move_lines |= aml
        return wrong_move_lines

    @api.model
    def run_reconcile_411_pos(self, nb_lines_per_job=100):
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid,
                                   context=self.env.context)
        parameter_obj = self.env['ir.config_parameter']
        reconcile_pos_account = parameter_obj.get_param(
            'to.reconcile.pos.account', False)
        reconcile_pos_account = self.env['account.account'].search(
            [('code', '=', reconcile_pos_account)], limit=1)
        if not reconcile_pos_account:
            _logger.warn(
                "Couldn't find account with code %s,"
                "please set value for key 'to.reconcile.pos.account'"
                " in config_parameter",
                reconcile_pos_account)
            return True

        debit_moves_domain = [
            ('reconciled', '=', False),
            ('account_id', '=', reconcile_pos_account and
                reconcile_pos_account.id or False),
            ('partner_id', '!=', None),
            ('debit', '>', 0),
            ('credit', '=', 0)
        ]
        # Create jobs
        lines = self.search(debit_moves_domain, order='id')

        # Reconcile the journal items by partner
        partner_ids = list(set(lines.mapped('partner_id.id')))
        total_lines = len(partner_ids)
        job_lines = nb_lines_per_job

        number_of_jobs = int(total_lines / job_lines) + \
            (total_lines % job_lines > 0)
        start_line = 0
        for i in range(1, number_of_jobs + 1):
            start_line = i * job_lines - job_lines
            end_line = i * job_lines
            chunk_ids = partner_ids[start_line:end_line]
            if i == number_of_jobs:
                chunk_ids = partner_ids[start_line:]

            session = ConnectorSession(self._cr, self._uid,
                                       context=self.env.context)
            job_reconcile_411_pos_by_ref.delay(
                session, 'res.partner', chunk_ids, reconcile_pos_account.id)

@job
def job_reconcile_411_pos_by_ref(
    session, model_name, partner_ids, reconcile_pos_account_id):
    ''' Reconcile account 411100 by partner reference (Pos Session)'''
    AccountMoveLine = session.env['account.move.line']
    domains = [
        ('reconciled', '=', False),
        ('account_id', '=', reconcile_pos_account_id),
        ('partner_id', 'in', partner_ids)
    ]
    lines = AccountMoveLine.search(domains)
    data_dict = {}  # {partner_id-ref: [move_line_ids]}
    for line in lines:
        k = "{partner_id}-{ref}".format(
            partner_id=line.partner_id.id,
            ref=line.ref or ''
        )
        if k not in data_dict:
            data_dict.update({
                k: [line.id]
            })
        else:
            data_dict[k].append(line.id)

    for move_line_ids in data_dict.values():
        _logger.info(
            ">>>> there are %s lines to reconciled : %s",
            len(move_line_ids), move_line_ids)
        reconcil_obj = session.env[
            'account.move.line.reconcile'].with_context(
            active_ids=move_line_ids)
        reconcil_obj.trans_rec_reconcile_full()
        _logger.info(">>>> reconciled object: %s", reconcil_obj)

@job
def job_reconcile_411_pos(
        session, model_name, move_line_ids, reconcile_pos_account_id):
    ''' Reconcile account 411100'''
    AccountMoveLine = session.env[model_name]
    debit_moves_domain = [
        ('reconciled', '=', False),
        ('account_id', '=', reconcile_pos_account_id),
        ('partner_id', '!=', None),
        ('debit', '>', 0),
        ('credit', '=', 0),
        ('id', 'in', move_line_ids)
    ]
    # before running, we research again
    # for sure there isn't any reconciled record
    debit_moves = AccountMoveLine.search(debit_moves_domain, order='id')
    ok_plusieurs_possibilites = 0
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
            " - ok_plusieurs_possibilites = %s", ok_plusieurs_possibilites)
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
            ('account_id', '=', reconcile_pos_account_id),
            ('debit', '=', 0),
            ('credit', '>', round(debit_to_reconcile.debit - 0.01, 2)),
            ('credit', '<', round(debit_to_reconcile.debit + 0.01, 2)),
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
            somme_credit = 0.0
            for payment_moveline in credit_candidates:
                somme_credit += payment_moveline.credit
                line_to_reconcil.append(payment_moveline.id)
            if (abs(somme_credit - debit_to_reconcile.debit) < 0.01):
                ok_plusieurs_possibilites += 1
                _logger.info("     => Total credit lines of the"
                             "day for this partner corresponds")
                _logger.info(
                    "     -> there are %s lines to reconciled : %s",
                    len(line_to_reconcil), line_to_reconcil)
                reconcil_obj = session.env[
                    'account.move.line.reconcile'].with_context(
                    active_ids=line_to_reconcil)
                reconcil_obj.trans_rec_reconcile_full()
                _logger.info(">>>> reconciled object: %s", reconcil_obj)
            else:
                ko_plusieurs_possibilites += 1
                _logger.info(
                    "    =>Total credit lines of the date: %s "
                    "for partner %s at account %s != total debit",
                    debit_to_reconcile.date,
                    debit_to_reconcile.partner_id.name,
                    debit_to_reconcile.account_id.name)
        if len(credit_candidates) == 0:
            ko_aucune_possibilite += 1
            _logger.info("     => No possibility")
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
            reconcil_obj = session.env['account.move.line.reconcile'].with_context(
                active_ids=line_to_reconcil)
            reconcil_obj.trans_rec_reconcile_full()
            _logger.info(">>>> reconciled object: %s", reconcil_obj)
