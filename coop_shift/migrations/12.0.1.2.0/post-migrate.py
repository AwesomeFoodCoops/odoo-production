

def migrate(cr, version):
    '''
    name field is computed from partner,
    but it is stored, so we force recomputation
    '''
    cr.execute("""
        UPDATE shift_registration sr
        SET name = p.name
        FROM res_partner p
        WHERE p.id = sr.partner_id
    """)
