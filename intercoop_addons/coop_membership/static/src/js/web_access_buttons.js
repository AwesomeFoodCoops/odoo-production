odoo.define('coop_membership.AccessButtons', function (require) {
  "use strict";

  var core = require('web.core');

  var FormView = require('web.FormView');
  var ListView = require('web.ListView');

  FormView.include({

    load_record: function() {
      var self = this;
      return this._super.apply(this, arguments)
        .then(function() {
          self.check_hide_buttons()
        });
    },

    on_button_edit: function() {
        var self = this;
        this._super.apply(this, arguments);        
    },

    on_form_changed: function() {
        var self = this;
        this._super.apply(this, arguments);
        self.check_hide_buttons()
    },

    check_hide_buttons: function() {
      var self = this;
      var model_name = self.dataset.model;
      this.dataset.call('check_access_buttons',
                        [[this.datarecord.id]])
        .then(function(result) {
          self.hide_button(result);
        });
    },

    hide_button: function(result) {
      if (result == 'lecture_group_partner') {
          self.$('.oe-cp-sidebar').hide();
          self.$('.o_chatter_topbar').hide();
          self.$('.oe-cp-buttons').hide();
          self.$('.oe_stat_button').prop('disabled', true);
      }
      else if (result == 'presence_group_partner') {
          self.$('.oe-cp-sidebar').hide();
          self.$('.o_chatter_topbar').hide();
          self.$('.oe-cp-buttons').hide();
          self.$('.oe_stat_button').prop('disabled', true);
      }
      else if (result == 'saisie_group_partner') {
          self.$('.oe-cp-sidebar').hide();
          self.$('.o_chatter_topbar').hide();
      }
      else if (result == 'presence_group_shift') {
          self.$('.oe-cp-sidebar').hide();
          self.$('.o_chatter_topbar').hide();
          self.$('.oe-cp-buttons').show();
          self.$('.oe_stat_button').prop('enable', true);
      }
      else if (result == 'saisie_group_shift') {
          self.$('.oe-cp-sidebar').hide();
          self.$('.o_chatter_topbar').hide();
      }
      else if (result == 'saisie_group_leave') {
          self.$('.oe-cp-sidebar').hide();
          self.$('.o_chatter_topbar').hide();
          self.$('.oe_stat_button').prop('disabled', true);
      }
      else{
          self.$('.oe-cp-sidebar').show();
          self.$('.o_chatter_topbar').show();
          self.$('.oe-cp-buttons').show();
          self.$('.oe_stat_button').prop('enable', true);
      }
    }



  });

  ListView.include({

    render_buttons: function($node) {
        var self = this;
        this._super.apply(this, arguments);
        self.check_hide_buttons();
    },

    do_select: function(ids, records) {
        var self = this;
        this._super(ids, records);
        self.check_hide_buttons_select()
    },

    check_hide_buttons: function() {
      var self = this;
      
      this.dataset.call('check_access_buttons',
                        [this.dataset.ids])
        .then(function(result) {
          self.hide_button(result);
        });
    },

    hide_button: function(result) {
      if (result) {
          self.$('.o_list_button_import').hide();
      }
      else{
        self.$('.o_list_button_import').show();
      }
    },

    check_hide_buttons_select: function() {
      var self = this;
      
      this.dataset.call('check_access_buttons',
                        [this.dataset.ids])
        .then(function(result) {
          self.hide_button_select(result);
        });
    },

    hide_button_select: function(result) {
      if (result) {
          self.$('.oe-cp-sidebar').hide();
      }
      else{
        self.$('.oe-cp-sidebar').show();
      }
    },



  })

});