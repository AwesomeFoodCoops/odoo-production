openerp.local_RESTcall_from_backend = function (instance) {
    instance.web.ActionManager.include({
        ir_actions_act_proxy: function (action, options) {
            action.request_list.forEach(function (request) {
                $.ajax({
                    url: request['url'],
                    type: 'POST',
                    timeout: 240000,
                    data: JSON.stringify(request['params']),
                    contentType: 'application/json',
                }).done(function (result) {
                    console.log("Proxy action have been done with sucess", result);
                    return result;
                    //TODO add an UI feedback
                }).fail(function (result) {
                    console.log('Proxy action have failed', result);
                    return result;
                    //TODO add an UI feedback
                })
            })
            //this.do_action({"type":"ir.actions.act_window_close"});
        }
    })
};
