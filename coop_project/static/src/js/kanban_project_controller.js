odoo.define('coop_project.KanbanProjectController', function (require) {
"use strict";

var core = require('web.core');
var _t = core._t;
var KanbanController = require('web.KanbanController');

var ProjectLegendKanbanController = KanbanController.extend({
    /**
     * @override
     */
    
    init: function (parent, model, renderer, params) {
        //this.context = session.user_context;
        this.model = model;
        this.model.controller = this;
        return this._super.apply(this, arguments);
    },
    
});

return ProjectLegendKanbanController;

});