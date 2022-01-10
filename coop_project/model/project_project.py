from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    privacy_visibility = fields.Selection([
        ('followers', 'On invitation only'),
        ('employees', 'Visible by all employees'),
    ], default='employees')
    project_categ_ids = fields.Many2many(
        'project.category', 'project_project_category_rel',
        'project_id', 'category_id', string='Categories')

    @api.multi
    def get_kanban_categories(self):
        res = []
        for project in self:
            for categ in project.project_categ_ids:
                res.append({
                    'name': categ.name,
                    'color': categ.color_code,
                    'id': categ.id,
                })
        return res
