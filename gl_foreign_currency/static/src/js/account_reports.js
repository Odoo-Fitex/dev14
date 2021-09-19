odoo.define('gl_foreign_currency.account_report', function (require) {
    'use strict';
    
    
    var core = require('web.core');
    var data = require('web.data');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var _t = core._t;

    var AccountReportWidget = require('account_reports.account_report');
    
    AccountReportWidget.include({
    	
        render_searchview_buttons: function() {
        	var self = this;
        	
        	_.each(this.$searchview_buttons.find('.account_currency_filter'), function(k) {
        		$(k).toggleClass('selected', (_.filter(self.report_options[$(k).data('filter')], function(el){return ''+el.id == ''+$(k).data('id') && el.selected === true;})).length > 0);
        	});
        	
            this._super.apply(this, arguments);
            this.$searchview_buttons.find('.account_currency_filter').click(function (event) {
                var option_value = $(this).data('filter');
                var option_id = $(this).data('id');
                _.filter(self.report_options[option_value], function(el) {
                    el.selected = false;
                    self.odoo_context['curr'] = option_id
                    return el;
                });
                self.reload();
            });
            
            } 
});
    });
