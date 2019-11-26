# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        louve_custom_cpo = env['ir.module.module'].search([
            ('name', '=', 'louve_custom_cpo'),
            ('state', 'in', ['installed', 'to upgrade', 'to install']),
        ])

        if louve_custom_cpo:
            _logger.info('Uninstalling louve_custom_cpo..')
            louve_custom_cpo.button_immediate_uninstall()

            # Reordering cpo lines
            _logger.info('Updating sequence of previous orders..')
            cr.execute("""
                UPDATE computed_purchase_order_line AS cpol
                SET sequence = ol.rownum
                FROM (
                    SELECT
                        id,
                        ROW_NUMBER() OVER (
                            PARTITION BY computed_purchase_order_id
                            ORDER BY product_code asc
                        ) AS rownum
                    FROM computed_purchase_order_line
                ) AS ol
                WHERE cpol.id = ol.id
            """)
