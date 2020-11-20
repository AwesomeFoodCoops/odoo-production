# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, installed_version):
    cr.execute("""
    update res_partner set display_name = barcode_base || ' - ' || display_name
    WHERE position(barcode_base || ' -' in display_name) = 0 and barcode_base NOTNULL and barcode_base > 0
    """)
