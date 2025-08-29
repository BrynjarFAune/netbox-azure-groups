from django import template
from django.utils.safestring import mark_safe
from ..models.azure_groups import GroupSourceChoices

register = template.Library()


@register.simple_tag
def group_badge(group):
    """Generate badge HTML for group source/type."""
    badges = []
    
    # Source indicator
    if group.source == GroupSourceChoices.ON_PREMISES:
        badges.append('<span class="badge bg-warning text-dark">AD Group</span>')
    elif group.source == GroupSourceChoices.EXTERNAL:
        badges.append('<span class="badge bg-info text-white">External</span>')
    else:
        badges.append('<span class="badge bg-primary text-white">Azure AD</span>')
    
    # Status indicators
    if group.is_stale:
        badges.append('<span class="badge bg-danger text-white">Stale</span>')
    
    if group.membership_type == MembershipTypeChoices.DYNAMIC:
        badges.append('<span class="badge bg-secondary text-white">Dynamic</span>')
    
    return mark_safe(' '.join(badges))


@register.simple_tag
def group_type_badge(group):
    """Generate badge for group type."""
    type_colors = {
        'security': 'bg-success',
        'microsoft365': 'bg-primary',
        'mail_security': 'bg-warning text-dark',
        'distribution': 'bg-info',
        'dynamic_security': 'bg-secondary',
        'dynamic_m365': 'bg-dark',
    }
    
    color = type_colors.get(group.group_type, 'bg-secondary')
    display_name = group.get_group_type_display()
    
    return mark_safe(f'<span class="badge {color} text-white">{display_name}</span>')


@register.simple_tag
def membership_badge(membership_type, nested_via=None):
    """Generate badge for membership type."""
    badges = []
    
    if membership_type == 'direct':
        badges.append('<span class="badge bg-primary text-white">Direct</span>')
    elif membership_type == 'nested':
        badges.append('<span class="badge bg-info text-white">Nested</span>')
        if nested_via:
            count = len(nested_via)
            badges.append(f'<small class="text-muted ms-1">({count} levels)</small>')
    elif membership_type == 'dynamic':
        badges.append('<span class="badge bg-warning text-dark">Dynamic</span>')
    
    return mark_safe(' '.join(badges))


@register.simple_tag  
def readonly_indicator(group):
    """Show management indicator - all groups are read-only in UI."""
    if group.source == GroupSourceChoices.ON_PREMISES:
        return mark_safe('<i class="mdi mdi-domain text-warning ms-1" title="Managed by On-Premises Active Directory"></i>')
    else:
        return mark_safe('<i class="mdi mdi-cloud text-primary ms-1" title="Managed by Azure Active Directory"></i>')


@register.simple_tag
def sync_status_badge(group):
    """Show sync status badge."""
    if group.is_deleted:
        return mark_safe('<span class="badge bg-danger text-white">Deleted</span>')
    elif group.is_stale:
        return mark_safe('<span class="badge bg-warning text-dark">Sync Needed</span>')
    else:
        return mark_safe('<span class="badge bg-success text-white">Up to Date</span>')


@register.inclusion_tag('netbox_azure_groups/inc/group_summary.html')
def group_summary(group):
    """Render a summary card for a group."""
    return {
        'group': group,
        'member_count': group.member_count,
        'owner_count': group.owner_count,
    }


@register.filter
def can_edit_group(group):
    """Check if group can be edited."""
    return group.can_modify


@register.simple_tag
def group_mail_badge(group):
    """Show mail-enabled badge if applicable."""
    if group.is_mail_enabled and group.mail:
        return mark_safe(
            f'<span class="badge bg-info text-white">'
            f'<i class="mdi mdi-email"></i> {group.mail}'
            f'</span>'
        )
    elif group.is_mail_enabled:
        return mark_safe('<span class="badge bg-info text-white"><i class="mdi mdi-email"></i> Mail-Enabled</span>')
    return ''