/** @odoo-module alias=anita_theme_setting.menu_helpers **/

/**
 * Traverses the given menu tree, executes the given callback for each node with
 * the node itself and the list of its ancestors as arguments.
 *
 * @param {Object} tree tree of menus as exported by the menus service
 * @param {Function} cb
 * @param {[Object]} [parents] the ancestors of the tree root, if any
 */
 function traverseMenuTree(tree, cb, parents = []) {
    cb(tree, parents);
    tree.childrenTree.forEach((c) => traverseMenuTree(c, cb, parents.concat([tree])));
}

/**
 * Computes the "apps" and "menuItems" from a given menu tree.
 *
 * @param {Object} menuTree tree of menus as exported by the menus service
 * @returns {Object} with keys "apps" and "menuItems" (HomeMenu props)
 */
export function computeAppsAndMenuItems(menuTree) {
    const apps = [];
    const menuItems = [];
    const menu_icon_policy = menuTree.menu_icon_policy;
    traverseMenuTree(menuTree, (menuItem, parents) => {
        if (!menuItem.id || !menuItem.actionID) {
            return;
        }
        const isApp = menuItem.id === menuItem.appID;
        const item = {
            parents: parents
                .slice(1)
                .map((p) => p.name)
                .join(" / "),
            label: menuItem.name,
            id: menuItem.id,
            xmlid: menuItem.xmlid,
            actionID: menuItem.actionID,
            appID: menuItem.appID,
        };
        if (isApp) {
            
            // add web icon type, the priority has been deal by backend
            if (menu_icon_policy == "svg_icon") {
                item.svg_icon = menuItem.svg_icon;
                item.icon_type = 'svg_icon'
            } else if (menu_icon_policy == "font_icon") {
                item.font_icon = menuItem.font_icon;
                item.icon_type = 'font_icon'
            } else {
                item.icon_type == 'web_icon'
                if (menuItem.webIconData) {
                    item.webIconData = menuItem.webIconData;
                } else {
                    const [iconClass, color, backgroundColor] = (menuItem.webIcon || "").split(",");
                    if (backgroundColor !== undefined) {
                        // Could split in three parts?
                        item.webIcon = { iconClass, color, backgroundColor };
                    } else {
                        item.webIconData = "/anita_theme_setting/static/img/default_icon_app.png";
                    }
                }
            }
        } else {
            item.menuID = parents[1].id;
        }
        if (isApp) {
            apps.push(item);
        } else {
            menuItems.push(item);
        }
    });

    return { apps, menuItems };
}
