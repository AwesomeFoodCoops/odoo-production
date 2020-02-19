def migrate(cr, version):
    if not version:
        return
    cr.execute('''
        update product_product p set weight=weight_net
        from product_template pt where p.product_tmpl_id=pt.id;''')
    return
