from netbox.plugins import PluginMenuItem, PluginMenu

# Create the menu with proper navigation structure
menus = [
    PluginMenu(
        label='Azure AD Groups',
        groups=[
            ('Directory', [
                PluginMenuItem(
                    link='plugins:netbox_azure_groups:azuregroup_list',
                    link_text='Azure Groups',
                    # No add button - read-only interface
                ),
            ])
        ],
        icon_class='mdi mdi-account-group'
    )
]