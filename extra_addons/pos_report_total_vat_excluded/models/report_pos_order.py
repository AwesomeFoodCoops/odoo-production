# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class ReportPosOrder(models.Model):
    _inherit = "report.pos.order"

    price_total_vat_excl = fields.Float(string='Total w/o Taxes',
                                        readonly=True)
    order_id = fields.Many2one('pos.order', 'Order', readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_pos_order')
        cr.execute("""
            create or replace view report_pos_order as (
                select
                    min(l.id) as id,
                    count(*) as nbr,
                    s.date_order as date,
                    s.id as order_id,
                    sum(l.qty) as product_qty,
                    sum(l.price_subtotal) as price_total_vat_excl,
                    sum(l.qty * l.price_unit) as price_sub_total,
                    sum((l.qty * l.price_unit) * (100 - l.discount) / 100)
                        as price_total,
                    sum((l.qty * l.price_unit) * (l.discount / 100))
                        as total_discount,
                    (sum(l.qty*l.price_unit)/sum(l.qty * u.factor))::decimal
                        as average_price,
                    sum(cast(to_char(date_trunc('day',s.date_order)
                        - date_trunc('day',s.create_date),'DD') as int))
                        as delay_validation,
                    s.partner_id as partner_id,
                    s.state as state,
                    s.user_id as user_id,
                    s.location_id as location_id,
                    s.company_id as company_id,
                    s.sale_journal as journal_id,
                    l.product_id as product_id,
                    pt.categ_id as product_categ_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    pt.pos_categ_id,
                    pc.stock_location_id,
                    s.pricelist_id,
                    s.invoice_id IS NOT NULL AS invoiced
                from pos_order_line as l
                    left join pos_order s on (s.id=l.order_id)
                    left join product_product p on (l.product_id=p.id)
                    left join product_template pt on (p.product_tmpl_id=pt.id)
                    left join product_uom u on (u.id=pt.uom_id)
                    left join pos_session ps on (s.session_id=ps.id)
                    left join pos_config pc on (ps.config_id=pc.id)
                group by
                    s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                    s.user_id,s.location_id,s.company_id,s.sale_journal,
                    s.pricelist_id,s.invoice_id,l.product_id,s.create_date,
                    pt.categ_id,pt.pos_categ_id,p.product_tmpl_id,
                    ps.config_id,pc.stock_location_id
                having
                    sum(l.qty * u.factor) != 0)""")
