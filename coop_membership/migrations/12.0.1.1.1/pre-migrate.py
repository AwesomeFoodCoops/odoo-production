# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, installed_version):
    cr.execute("update res_partner set birthdate_date = birthdate")
