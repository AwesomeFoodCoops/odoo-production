odoo.define('coop_account.export_wrong_reconciliation_move_lines', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var crash_manager = require('web.crash_manager');
var Model = require('web.Model');

function export_wrong_reconciliation_move_lines(){
     var model = 'account.move.line';
     var method = 'export_wrong_reconciliation_ml';
     var def = new Model(model).call(method, [], {context: session.user_context || {}})
     def.then(function(data){
         $.blockUI();
         session.get_file({
            url: '/web/export/xls_view',
            data: {data: data},
            complete: $.unblockUI
         });
     })
     .fail(function(){
        crash_manager.rpc_error.bind(crash_manager)
     });
}

core.action_registry.add("export_wrong_reconciliation_move_lines", export_wrong_reconciliation_move_lines);
});
