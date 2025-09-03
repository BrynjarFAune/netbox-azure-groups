from netbox.plugins import PluginMenuItem, PluginMenuButton, PluginMenu

# Create buttons using proper PluginMenuButton class
protected_resource_buttons = (
    PluginMenuButton(
        link='plugins:netbox_access_control:protectedresource_add',
        title='Add Protected Resource',
        icon_class='mdi mdi-plus-thick'
    ),
)

business_unit_buttons = (
    PluginMenuButton(
        link='plugins:netbox_access_control:businessunit_add',
        title='Add Business Unit',
        icon_class='mdi mdi-plus-thick'
    ),
)

access_method_buttons = (
    PluginMenuButton(
        link='plugins:netbox_access_control:accesscontrolmethod_add',
        title='Add Access Method',
        icon_class='mdi mdi-plus-thick'
    ),
)

access_grant_buttons = (
    PluginMenuButton(
        link='plugins:netbox_access_control:accessgrant_add',
        title='Add Access Grant',
        icon_class='mdi mdi-plus-thick'
    ),
)

# Create the menu with proper navigation structure
menu = PluginMenu(
    label='Access Control',
    groups=(
        ('Overview', (
            PluginMenuItem(
                link='plugins:netbox_access_control:dashboard',
                link_text='Dashboard'
            ),
        )),
        ('Directory', (
            PluginMenuItem(
                link='plugins:netbox_access_control:azuregroup_list',
                link_text='Azure Groups'
                # No add button - read-only interface
            ),
        )),
        ('Management', (
            PluginMenuItem(
                link='plugins:netbox_access_control:businessunit_list',
                link_text='Business Units',
                buttons=business_unit_buttons
            ),
            PluginMenuItem(
                link='plugins:netbox_access_control:protectedresource_list',
                link_text='Protected Resources',
                buttons=protected_resource_buttons
            ),
            PluginMenuItem(
                link='plugins:netbox_access_control:accesscontrolmethod_list',
                link_text='Access Control Methods',
                buttons=access_method_buttons
            ),
        )),
        ('Policies', (
            PluginMenuItem(
                link='plugins:netbox_access_control:fortigatepolicy_list',
                link_text='FortiGate Policies'
                # No add button - policies are read-only and imported
            ),
        )),
        ('Access Management', (
            PluginMenuItem(
                link='plugins:netbox_access_control:accessgrant_list',
                link_text='Access Grants',
                buttons=access_grant_buttons
            ),
        ))
    ),
    icon_class='mdi mdi-shield-lock'
)