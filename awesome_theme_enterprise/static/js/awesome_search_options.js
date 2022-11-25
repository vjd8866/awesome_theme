odoo.define('awesome_theme_enterprise.search_options', function (require) {
    "use strict";

    const FilterMenu = require('web.FilterMenu')
    const GroupByMenu = require('web.GroupByMenu')
    const FavoriteMenu = require('web.FavoriteMenu')
    const ComparisonMenu = require('web.ComparisonMenu')

    class AwesomeFilterMenu extends FilterMenu {}
    AwesomeFilterMenu.template = "awesome_theme_enterprise.legacy.FilterMenu"

    class AwesomeGroupMenu extends GroupByMenu {}
    AwesomeGroupMenu.template = "awesome_theme_enterprise.GroupByMenu"

    class AwesomeFavoriteMenu extends FavoriteMenu {}
    AwesomeFavoriteMenu.template = "awesome_theme_enterprise.FavoriteMenu"

    class AwesomeComparisonMenu extends ComparisonMenu {}
    AwesomeComparisonMenu.template = "awesome_theme_enterprise.ComparisonMenu"

    return {
        AwesomeFilterMenu,
        AwesomeGroupMenu,
        AwesomeFavoriteMenu,
        AwesomeComparisonMenu
    }
})