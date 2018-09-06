# -*- coding: utf-8 -*-

from openerp import api, models, _
from openerp.tools import float_is_zero


class ReportAgedPartnerBalance(models.AbstractModel):

    _inherit = 'report.account.report_agedpartnerbalance'

    def _get_partner_move_lines(
            self, form, account_type, date_from, target_move):
        res = []
        self.total_account = []
        cr = self.env.cr
        user_company = self.env.user.company_id.id
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type))
        # build the reconciliation clause to see what partner needs to be printed
        reconciliation_clause = '(l.reconciled IS FALSE)'
        cr.execute('''
        		SELECT debit_move_id, credit_move_id 
                FROM account_partial_reconcile 
               	WHERE create_date > %s 
           	''', (date_from,))
        reconciled_after_date = []
        for row in cr.fetchall():
            reconciled_after_date += [row[0], row[1]]
        if reconciled_after_date:
            reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
            arg_list += (tuple(reconciled_after_date),)
        arg_list += (date_from, user_company)
        query = '''
            SELECT DISTINCT res_partner.id AS id, res_partner.barcode_base AS barcode,
            COALESCE(res_partner.barcode_base || ' - ' , ' ') || res_partner.name AS name,
            UPPER(res_partner.name) AS uppername
            FROM res_partner,account_move_line AS l, account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.internal_type IN %s)
                AND ''' + reconciliation_clause + '''
                AND (l.partner_id = res_partner.id)
                AND (l.date <= %s)
                AND l.company_id = %s
            ORDER BY res_partner.barcode_base ASC,UPPER(res_partner.name) ASC'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            self.total_account.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['id'] for partner in partners]
        if not partner_ids:
            return []

        # This dictionary will store the not due amount of all partners
        future_past = {}
        query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) > %s)\
                    AND (l.partner_id IN %s)
                AND (l.date <= %s)
                AND l.company_id = %s'''
        cr.execute(query,
                   (tuple(move_state), tuple(account_type),
                    date_from, tuple(partner_ids), date_from, user_company))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            if line.partner_id.id not in future_past:
                future_past[line.partner_id.id] = 0.0
            line_amount = line.balance
            if line.balance == 0:
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.create_date[:10] <= date_from:
                    line_amount += partial_line.amount
            for partial_line in line.matched_credit_ids:
                if partial_line.create_date[:10] <= date_from:
                    line_amount -= partial_line.amount
            future_past[line.partner_id.id] += line_amount

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(
                account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if form[str(i)]['start'] and form[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (form[str(i)]['start'], form[str(i)]['stop'])
            elif form[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (form[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (form[str(i)]['stop'],)
            args_list += (date_from, user_company)

            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND (l.partner_id IN %s)
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id = %s'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                if line.partner_id.id not in partners_amount:
                    partners_amount[line.partner_id.id] = 0.0
                line_amount = line.balance
                if line.balance == 0:
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.create_date[:10] <= date_from:
                        line_amount += partial_line.amount
                for partial_line in line.matched_credit_ids:
                    if partial_line.create_date[:10] <= date_from:
                        line_amount -= partial_line.amount

                partners_amount[line.partner_id.id] += line_amount
            history.append(partners_amount)

        for partner in partners:
            at_least_one_amount = False
            values = {}
            # Query here is replaced by one query which gets the all the partners their 'after' value
            after = False
            # Making sure this partner actually was found by the query
            if partner['id'] in future_past:
                after = [future_past[partner['id']]]

            self.total_account[6] = self.total_account[6] + \
                (after and after[0] or 0.0)
            values['direction'] = after and after[0] or 0.0
            if not float_is_zero(
                    values['direction'],
                    precision_rounding=self.env.user.company_id.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['id'] in history[i]:
                    during = [history[i][partner['id']]]
                # Adding counter
                self.total_account[(i)] = self.total_account[(
                    i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(
                        values[str(i)],
                        precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] +
                                  [values[str(i)] for i in range(5)])
            # Add for total
            self.total_account[(i + 1)] += values['total']
            values['name'] = partner['name']

            if at_least_one_amount:
                res.append(values)

        total = 0.0
        totals = {}
        for r in res:
            total += float(r['total'] or 0.0)
            for i in range(5) + ['direction']:
                totals.setdefault(str(i), 0.0)
                totals[str(i)] += float(r[str(i)] or 0.0)
        return res
