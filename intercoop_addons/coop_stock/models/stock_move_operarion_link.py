from openerp import fields, models


class StockMoveOperationLink(models.Model):
    _inherit = 'stock.move.operation.link'

    reserved_quant_id = fields.Many2one(index=True)
    operation_id = fields.Many2one(index=True)
    move_id = fields.Many2one(index=True)
