odoo.define('anita_theme_setting.theme_editor', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var Customizer = require('anita_theme_setting.customizer')

    var AnitaThemeEditor = Customizer.extend({

        template: 'anita_theme_setting.customizer_panel',
        items: [],

        /**
         * rewrite to prevent use the backend setting
         * @param {} parent 
         */
        init: function (parent, action) {
            Widget.prototype.init.apply(this, arguments);
            
            var params = action.params;
            this.params = params;
            this.owner = params.owner;

            this.mode_id = params.cur_mode_id;
            this.style_id = params.cur_style_id;

            // this will affect the window click action
            this.is_dynamic = true;

            this.user_setting = {
                "theme_modes": params.theme_modes,
                "settings": params.settings
            }
            this.mode_data = params.theme_modes
        },

        start: function () {
            Widget.prototype.start.apply(this, arguments)

            this._init_tab();
            this.show_panel();

            // bind window
            $(document).on("click", this._on_window_click.bind(this));
        },

        /**
         * as the super class get the mode data from the backend, so rewrite to ignore it
         */
        willStart: function () {
            return $.when();
        },

        show_panel: function () {
            this.$el.addClass('open');
            // bind window
            $(document).on("click", this._on_window_click.bind(this));
        },

        hide_panel: function () {
            this.$el.removeClass('open');
            // bind window
            $(document).off("click", this._on_window_click.bind(this));
            setTimeout(() => {
                this.destroy();
            }, 300);
        },

        _on_customizer_close_click: function (event) {
            event.preventDefault();
            event.stopPropagation();

            this.hide_panel();
        },

        /**
         * @param {*} event 
         */
        _is_color_picker_click: function (event) {
            if (this.$el.is(':visible')
                && $(event.target).is($(".colorpicker-bs-popover, .colorpicker-bs-popover *"))) {
                return true
            } else {
                return false
            }
        },

        _on_cancel_btn_click: function (event) {
            event.preventDefault();
            event.stopPropagation();

            this.hide_panel();
        }
    });

    return AnitaThemeEditor;
});
