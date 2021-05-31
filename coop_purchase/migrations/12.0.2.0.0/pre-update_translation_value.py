# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, installed_version):
    cr.execute("""
    update ir_translation set value='Prix de vente HT'
    where src='Sale Price Taxes Excluded' and lang='fr_FR'
    """)
    cr.execute("""
    update ir_translation set value='Prix de vente TTC'
    where src='Sale Price Taxes Included' and lang='fr_FR'
    """)
