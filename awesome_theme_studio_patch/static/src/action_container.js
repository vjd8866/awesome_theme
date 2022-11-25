/** @odoo-module **/

import { StudioClientAction } from "@web_studio/client_action/studio_client_action";

const { Component, tags } = owl;

StudioClientAction.components = {
    Editor,
    ComponentAdapter: class extends ComponentAdapter {
        setup() {
            super.setup();
            this.env = owl.Component.env;
        }
    },
};

StudioClientAction.target = "current";
StudioClientAction.displayName = "Studio";

// change the layout of the studio
StudioClientAction.template = tags.xml`
<t t-name="web.ActionContainer">
    <div>
        <div 
            t-props = "multi_tab_props" 
            t-ref="multi_tab" 
            t-on-akl-active-action="_on_active_action"
            t-on-akl-close-other-action="_on_close_other_action"
            t-on-akl-close-all-action="_on_close_all_action"
            t-on-akl-close-cur-action="_on_close_cur_action"
            t-on-akl-close-action="_on_close_action"/>
        <div t-if="action_info.active" t-foreach="action_infos" t-as="action_info" t-key="action_info.id" class="akl_tab_page_container ">
            <t t-if="action_info.Component" t-component="action_info.Component" t-props="action_info.componentProps" />
        </div>
    </div>
</t>`;