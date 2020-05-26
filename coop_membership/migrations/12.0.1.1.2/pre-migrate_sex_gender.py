def migrate(cr, version):
    if not version:
        return
    cr.execute("update res_partner set gender='male' where sex='m' ")
    cr.execute("update res_partner set gender='female' where sex='f' ")
    cr.execute("update res_partner set gender='other' where sex='o' ")
