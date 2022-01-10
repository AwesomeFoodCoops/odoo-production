/**
*
*    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
*
**/

odoo.define('coop_project.KanbanProjectRenderer', function (require) {
    "use strict";

    var core = require('web.core');
    var rpc = require('web.rpc');
    var KanbanRenderer = require('web.KanbanRenderer');
    var qweb = core.qweb;

    var ProjectLegendKanbanRenderer = KanbanRenderer.extend({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.projectView = params.projectView;
        },
        on_attach_callback: function () {
            this._super.apply(this, arguments)
            this._renderProjectLegend();
        },
        _renderProjectLegend: function(){
            var self = this;
            var categLegend = $('.o_kanban_project_panel_section');
            if (categLegend){
                categLegend.remove()
            }
            if (this.state.context.default_project_id === undefined){
                return;
            }
            rpc.query({
                model: 'project.project',
                method: 'get_kanban_categories',
                args: [[this.state.context.default_project_id]],
            })
            .then(function (categories){
                self.$el.before(self._renderProjectCategory(categories));
                $('.o_kanban_project_panel_section').on('click', '.block-color-act', function(ev){
                    var $el = ev.currentTarget;
                    var searchView = self.projectView.model.controller.searchView;
                    var query = $el.dataset.categName;
                    searchView.autocomplete.source({term:query}, function (results) {
                        if (results.length) {
                            var res = results.  find(function (res) {
                                return res.facet.field.attrs.name === 'project_categ_id';
                            });
                            if (res){
                                if(res.facet && res.facet.values && res.facet.values.length && String(res.facet.values[0].value).trim() !== "") {
                                    searchView.query.toggle(res.facet);
                                } else {
                                    searchView.query.trigger('add');
                                }
                            }
                        }
                    });
                });
            });
            
        },
        _renderProjectCategory: function (categories) {
            //var categories = [{'name': 'Membership', 'color': '#28a745'},{'name': 'IT', 'color': '#dc3545'}];
            return qweb.render('ProjectKanban.Category', {categories: categories});
        },
    });
    return ProjectLegendKanbanRenderer;
});
