# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shift_ok = fields.Boolean(
        'Shift Subscription', help="""Determine if a product needs to create
        automatically an event registration at the confirmation of a sales
        order line.""")
    shift_type_id = fields.Many2one(
        'shift.type', 'Type of Shift', help="""Select event types so when
        we use this product in sales order lines, it will filter events of
        this type only.""")

    @api.onchange('type', 'shift_ok')
    def onchange_shift_ok(self):
        if self.shift_ok:
            self.type = 'service'
            self.sale_ok = False
            self.purchase_ok = False
            self.event_ok = True


class ProductProduct(models.Model):
    _inherit = 'product.product'
    shift_ticket_ids = fields.One2many(
        'shift.ticket', 'product_id', 'Shift Tickets')

    @api.onchange('type', 'shift_ok')
    def onchange_shift_ok(self):
        """Redirection, inheritance mechanism hides the method on the model"""
        if self.shift_ok:
            self.type = 'service'
            self.sale_ok = False
            self.purchase_ok = False
            self.event_ok = True
