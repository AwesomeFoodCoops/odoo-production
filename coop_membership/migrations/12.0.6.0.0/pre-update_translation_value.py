# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, installed_version):
    cr.execute("""
    update ir_translation set value='Rattachées'
    where value='Personnes rattachées' and lang='fr_FR'
    """)
    cr.execute("""
    update ir_translation set value='Alerte entrée'
    where value='Alerte entrées' and lang='fr_FR'
    """)
    cr.execute("""
    update ir_translation set value='Opérations par lot'
    where value='Opérations en lot' and lang='fr_FR'
    """)
