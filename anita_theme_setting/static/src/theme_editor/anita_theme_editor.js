/** @odoo-module **/

import { registry } from "@web/core/registry";

import AnitaThemeEditor from 'anita_theme_setting.theme_editor'
import core from 'web.core'
import { ComponentAdapter } from 'web.OwlCompatibility';
import Widget from 'web.Widget';

const { Component, tags } = owl;

export class ThemeEditor extends ComponentAdapter {
    constructor(parent, props) {
        super(parent, props);
        core.bus.on('anita_show_theme_editor', this, this.show_theme_editor.bind(this))
        this.env = Component.env;
    }

    show_theme_editor(action) {
        this.theme_editor = new AnitaThemeEditor(this, action);
        this.theme_editor.appendTo(document.body);
    }
}

registry.category("main_components").add("ThemeEditor", {
    Component: ThemeEditor,
    props: {
        Component: Widget
    }
});
