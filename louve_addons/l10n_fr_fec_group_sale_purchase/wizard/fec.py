# -*- encoding: utf-8 -*-
from openerp import models, fields, api
import csv
import os


class AccountFrFec(models.TransientModel):
    _inherit = 'account.fr.fec'

    group_sale_purchase = fields.Boolean('Group Sale and Purchase Journals',
                                         default=True)

    @api.multi
    def write_fec_lines(self, file_path, delimiter, date_from, date_to):
        self.ensure_one()
        if not self.group_sale_purchase:
            return super(AccountFrFec, self).write_fec_lines(
                file_path, delimiter, date_from, date_to)
        if not os.path.exists(file_path):
            raise ValueError('File {} not found'.format(file_path))

        fec_file = open(file_path, 'a+')
        w = csv.writer(fec_file, delimiter=delimiter)
        sql_query = '''
                (SELECT
                    replace(aj.code, '|', '/') AS JournalCode,
                    replace(aj.name, '|', '/') AS JournalLib,
                    replace(am.name, '|', '/') AS EcritureNum,
                    TO_CHAR(am.date, 'YYYYMMDD') AS EcritureDate,
                    aa.code AS CompteNum,
                    replace(aa.name, '|', '/') AS CompteLib,
                    CASE WHEN rp.ref IS null OR rp.ref = ''
                    THEN COALESCE('ID ' || rp.id, '')
                    ELSE rp.ref
                    END
                    AS CompAuxNum,
                    COALESCE(replace(rp.name, '|', '/'), '') AS CompAuxLib,
                    CASE WHEN am.ref IS null OR am.ref = ''
                    THEN '-'
                    ELSE replace(am.ref, '|', '/')
                    END
                    AS PieceRef,
                    TO_CHAR(am.date, 'YYYYMMDD') AS PieceDate,
                    CASE WHEN aml.name IS NULL THEN '/'
                        WHEN aml.name SIMILAR TO '[\t|\s|\n]*' THEN '/'
                        ELSE replace(aml.name, '|', '/') END AS EcritureLib,
                    replace(CASE WHEN aml.debit = 0 THEN '0,00' ELSE 
                    to_char(aml.debit, '000000000000000D99') END, '.', ',') 
                    AS Debit,
                    replace(CASE WHEN aml.credit = 0 THEN '0,00' ELSE 
                    to_char(aml.credit, '000000000000000D99') END, '.', ',') 
                    AS Credit,
                    CASE WHEN rec.name IS NULL THEN '' ELSE rec.name 
                    END AS EcritureLet,
                    CASE WHEN aml.full_reconcile_id IS NULL THEN '' ELSE 
                    TO_CHAR(rec.create_date, 'YYYYMMDD') END AS DateLet,
                    TO_CHAR(am.date, 'YYYYMMDD') AS ValidDate,
                    CASE
                        WHEN aml.amount_currency IS NULL OR 
                        aml.amount_currency = 0 THEN ''
                        ELSE replace(to_char(aml.amount_currency, 
                                            '000000000000000D99'), '.', ',')
                    END AS Montantdevise,
                    CASE WHEN aml.currency_id IS NULL THEN '' ELSE rc.name END
                    AS Idevise,
                    TO_CHAR(aml.account_id, '0'),
                    TO_CHAR(aml.partner_id, '0')
                FROM
                    account_move_line aml
                    LEFT JOIN account_move am ON am.id=aml.move_id
                    LEFT JOIN res_partner rp ON rp.id=aml.partner_id
                    JOIN account_journal aj ON aj.id = am.journal_id
                    JOIN account_account aa ON aa.id = aml.account_id
                    LEFT JOIN res_currency rc ON rc.id = aml.currency_id
                    LEFT JOIN account_full_reconcile rec ON 
                                rec.id = aml.full_reconcile_id
                WHERE
                    am.date >= %s
                    AND aj.type not in ('sale', 'purchase')
                    AND am.date <= %s
                    AND am.company_id = %s
                    AND (aml.debit != 0 OR aml.credit != 0)
                '''

        # For official report: only use posted entries
        if self.export_type == "official":
            sql_query += '''
                    AND am.state = 'posted'
                    '''

        sql_query += '''
                ORDER BY
                    am.date,
                    am.name,
                    aml.id)
                '''

        sql_query2 = '''
                SELECT
                    replace(STRING_AGG(distinct aj.code, ';'), '|', '/') AS
                    JournalCode,
                    replace(STRING_AGG(distinct aj.name, ';'), '|', '/')
                    AS JournalLib,
                    replace(am.name, '|', '/') AS EcritureNum,
                    TO_CHAR(MAX(am.date), 'YYYYMMDD') AS
                    EcritureDate,
                    STRING_AGG(distinct aa.code, ';') AS CompteNum,
                    replace(STRING_AGG(distinct aa.name, ';'), '|', '/')
                    AS CompteLib,
                    CASE WHEN MIN(rp.ref) IS null OR MIN(rp.ref) = ''
                    THEN COALESCE('ID ' || min(rp.id), '')
                    ELSE MIN(rp.ref)
                    END
                    AS CompAuxNum,
                    COALESCE(replace(MAX(rp.name), '|', '/'), '') AS
                    CompAuxLib,
                    CASE WHEN MIN(am.ref) IS null OR MIN(am.ref) = ''
                    THEN '-'
                    ELSE replace(MIN(am.ref), '|', '/')
                    END
                    AS PieceRef,
                    TO_CHAR(MAX(am.date), 'YYYYMMDD') AS PieceDate,
                    CASE WHEN MIN(aml.name) IS NULL THEN '/'
                        WHEN MIN(aml.name) SIMILAR TO '[\t|\s|\n]*' THEN '/'
                        ELSE replace(MAX(aml.name), '|', '/') END AS
                        EcritureLib,
                    replace(CASE WHEN sum(aml.debit) = 0 THEN '0,00' ELSE
                    to_char(sum(aml.debit), '000000000000000D99') END, '.', ',
                    ') AS Debit,
                    replace(CASE WHEN sum(aml.credit) = 0 THEN '0,00' ELSE
                    to_char(sum(aml.credit), '000000000000000D99') END, '.', ',
                    ') AS Credit,
                    CASE WHEN MIN(rec.name) IS NULL THEN '' ELSE MIN(rec.name)
                    END AS EcritureLet,
                    CASE WHEN MIN(aml.full_reconcile_id) IS NULL THEN '' ELSE
                    TO_CHAR(MIN(rec.create_date), 'YYYYMMDD') END AS DateLet,
                    TO_CHAR(MIN(am.date), 'YYYYMMDD') AS ValidDate,
                    CASE
                        WHEN MIN(aml.amount_currency) IS NULL OR
                        MIN(aml.amount_currency) = 0 THEN ''
                        ELSE replace(to_char(MIN(aml.amount_currency),
                        '000000000000000D99'), '.', ',')
                    END AS Montantdevise,
                    CASE WHEN MIN(aml.currency_id) IS NULL THEN '' ELSE
                    MIN(rc.name) END AS Idevise,
                    TO_CHAR(aml.account_id, '0'),
                    TO_CHAR(aml.partner_id, '0')
                FROM
                    account_move_line aml
                    LEFT JOIN account_move am ON am.id=aml.move_id
                    LEFT JOIN res_partner rp ON rp.id=aml.partner_id
                    JOIN account_journal aj ON aj.id = am.journal_id
                    JOIN account_account aa ON aa.id = aml.account_id
                    LEFT JOIN res_currency rc ON rc.id = aml.currency_id
                    LEFT JOIN account_full_reconcile rec ON
                    rec.id = aml.full_reconcile_id
                WHERE
                    am.date >= %s
                    AND aj.type in ('sale', 'purchase')
                    AND am.date <= %s
                    AND am.company_id = %s
                    AND (aml.debit != 0 OR aml.credit != 0)
                '''

        # For official report: only use posted entries
        if self.export_type == "official":
            sql_query2 += '''
                    AND am.state = 'posted'
                    '''

        sql_query2 += '''
                GROUP BY
                    am.name,
                    aml.account_id,
                    aml.partner_id
                     '''
        sql_query2 += '''
                ORDER BY
                    MIN(am.date),
                    MIN(am.name),
                    MIN(aml.id)
                '''

        sql_query = sql_query + '''
                UNION (
                    ''' + sql_query2 + ''' )
                ORDER BY
                    PieceDate,
                    EcritureNum
                    '''

        company = self.env.user.company_id
        for row in self.minimize_execute(
                sql_query, (date_from, date_to, company.id, date_from,
                            date_to, company.id)):
            listrow = list(row)
            w.writerow([s.encode("utf-8") if s else '' for s in listrow])
        fec_file.close()
