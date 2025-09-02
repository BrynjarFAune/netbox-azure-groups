from netbox.plugins import PluginMenuItem, PluginMenu

# Create the menu with proper navigation structure
menus = [
    PluginMenu(
        label='Access Control',
        groups=[
            ('Directory', [
                PluginMenuItem(
                    link='plugins:netbox_azure_groups:azuregroup_list',
                    link_text='Azure Groups',
                    # No add button - read-only interface
                ),
            ]),
            ('Resources', [
                PluginMenuItem(
                    link='plugins:netbox_azure_groups:protectedresource_list',
                    link_text='Protected Resources',
                    buttons=[
                        PluginMenuItem(
                            link='plugins:netbox_azure_groups:protectedresource_add',
                            link_text='Add'
                        )
                    ]
                ),
                PluginMenuItem(
                    link='plugins:netbox_azure_groups:accesscontrolmethod_list',
                    link_text='Access Control Methods',
                    buttons=[
                        PluginMenuItem(
                            link='plugins:netbox_azure_groups:accesscontrolmethod_add',
                            link_text='Add'
                        )
                    ]
                ),
            ]),
            ('Policies', [
                PluginMenuItem(
                    link='plugins:netbox_azure_groups:fortigatepolicy_list',
                    link_text='FortiGate Policies',
                    # No add button - policies are read-only and imported
                ),
            ]),
            ('Access Management', [
                PluginMenuItem(
                    link='plugins:netbox_azure_groups:accessgrant_list',
                    link_text='Access Grants',
                    buttons=[
                        PluginMenuItem(
                            link='plugins:netbox_azure_groups:accessgrant_add',
                            link_text='Add'
                        )
                    ]
                ),
            ])
        ],
        icon_class='mdi mdi-shield-lock'
    )
]