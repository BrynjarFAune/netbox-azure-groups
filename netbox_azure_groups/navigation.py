from netbox.plugins import PluginMenuItem, PluginMenuButton, PluginMenu
from netbox.choices import ButtonColorChoices

azuregroup_buttons = [
    PluginMenuButton(
        link='plugins:netbox_azure_groups:azuregroup_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
    )
]

menu = PluginMenu(
    label='Azure AD Groups',
    groups=[
        ('Directory', [
            PluginMenuItem(
                link='plugins:netbox_azure_groups:azuregroup_list',
                link_text='Azure Groups',
                buttons=azuregroup_buttons
            ),
        ])
    ],
    icon_class='mdi mdi-account-group'
)