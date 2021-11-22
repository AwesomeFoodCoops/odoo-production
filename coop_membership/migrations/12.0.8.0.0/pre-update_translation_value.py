# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, installed_version):
    cr.execute("""
    update ir_translation set value='Date du changement d’équipe'
    where src='Start Date with the New Team' and lang='fr_FR'
    """)
