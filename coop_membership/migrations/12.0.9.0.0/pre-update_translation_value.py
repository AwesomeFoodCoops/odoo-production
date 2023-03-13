# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, installed_version):
    cr.execute("""
    update ir_translation set value='Désinscription'
    where value='Date de décinscription' and lang='fr_FR'
    """)
