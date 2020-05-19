def migrate(cr, version):
    if not version:
        return
    cr.execute("update res_partner set birthdate_date=birthdate")
