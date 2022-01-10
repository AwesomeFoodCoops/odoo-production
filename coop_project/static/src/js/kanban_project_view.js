odoo.define('coop_project.KanbanProjectView', function (require) {
"use strict";

var KanbanProjectController = require('coop_project.KanbanProjectController');
var KanbanProjectRenderer = require('coop_project.KanbanProjectRenderer');
var KanbanView = require('web.KanbanView');
var viewRegistry = require('web.view_registry');

var ProjectLegendKanbanView = KanbanView.extend({
    config: _.extend({}, KanbanView.prototype.config, {
        Controller: KanbanProjectController,
        Renderer: KanbanProjectRenderer,
    }),
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);
        this.rendererParams.projectView = this;
    },

});

viewRegistry.add('project_legend_kanban', ProjectLegendKanbanView);

return ProjectLegendKanbanView;

});