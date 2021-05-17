# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, installed_version):
    cr.execute("""
    update ir_translation set value='Rattachées'
    where value='Personnes rattachées'
    """)
    cr.execute("""
    update ir_translation set value='Alerte entrée'
    where value='Alerte entrées'
    """)
    cr.execute("""
    update ir_translation set value='Opérations par lot'
    where value='Opérations en lot'
    """)
