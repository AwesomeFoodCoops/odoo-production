# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MassMailingList(models.Model):
    _inherit = 'mail.mass_mailing.list'

    is_member_contact = fields.Boolean(
        default=False,
        help="Populate the contact from the members")

    def compute_contacts(self, limit=1000):
        self.remove_contacts()
        self.add_contacts(limit)

    def remove_contacts(self):
        if not self:
            return
        sql = """
        DELETE FROM mail_mass_mailing_contact_list_rel
        WHERE id IN (
            SELECT ctr.id
            FROM mail_mass_mailing_contact ct
            JOIN mail_mass_mailing_contact_list_rel ctr
                ON ctr.contact_id = ct.id
            JOIN (
                SELECT DISTINCT ON (email) id, email, is_member
                FROM res_partner
                ORDER BY email, is_member DESC NULLS LAST
            ) rp
                ON rp.email = ct.email
            WHERE rp.is_member IS FALSE
                AND ctr.list_id in {ctr_ids}
        )
        """.format(
            ctr_ids=str(tuple(self.ids + [-1]))
        )
        self._cr.execute(sql)

    def add_contacts(self, limit=1000):
        if not self:
            return
        sql = """
            SELECT rp.id, rp.name, rp.email, rp.opt_out
            FROM res_partner rp
            LEFT JOIN mail_mass_mailing_contact ct
                ON rp.email = ct.email
            WHERE ct.id ISNULL
                AND rp.email NOTNULL
                AND rp.is_member IS TRUE
            LIMIT {limit}
        """.format(
            limit=limit
        )
        self._cr.execute(sql)
        datas = self._cr.fetchall()
        for data in datas:
            vals = {
                'name': data[1],
                'email': data[2],
                'is_member_contact': True,
                'subscription_list_ids': []
            }
            for list in self:
                vals['subscription_list_ids'].append((0, 0, {
                    'list_id': list.id,
                    'opt_out': data[3]
                }))
            contact = self.env['mail.mass_mailing.contact'].create(vals)

    @api.model
    def cron_compute_contact(self, limit=1000):
        """
        F#44056 - Chaudron - Envoi en masse
        - Remove the contact which not the member anymore
        - Create new contact for a new member
        """
        list = self.search([
            ('is_member_contact', '=', True)
        ])
        list.compute_contacts(limit)
