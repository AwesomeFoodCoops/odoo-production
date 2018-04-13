# -*- coding: utf-8 -*-
import erppeek


def init_openerp(url, login, password, database):
    try:
        openerp = erppeek.Client(url)
        uid = openerp.login(login, password=password, database=database)
        return openerp, uid
    except:
        return False, False


# Enter your server information below
openerp, uid = init_openerp(
    'url e.g.: http://localhost:8069/',
    'login',
    'password',
    'database',
)


def fix_product_history():
    # You can modify the search criterias below

    # the limit=1000 is there to avoid that the script runs for too long
    # you'll have to launch it several times, until the number of histories
    # to delete is < 1000.
    ph_ids = openerp.ProductHistory.browse([
        ('to_date', '>=', '2016-12-12'),
    ], limit=1000)

    print "==============================================================="
    print "================= Deleting %s Histories=================" % (
        len(ph_ids))
    print "==============================================================="
    i = 0
    for ph in ph_ids:
        i += 1
        print "=== %s / %s" % (i, len(ph_ids))
        ph.unlink()
    print "==============================================================="
    print "============================= Done!============================"
    print "==============================================================="


fix_product_history()
