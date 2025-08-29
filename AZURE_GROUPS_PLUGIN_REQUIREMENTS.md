# Azure Groups NetBox Plugin - Development Requirements

## Core Plugin Architecture

### Data Model Design

#### Group Types (Fixed Choices)
```python
GROUP_TYPE_CHOICES = [
    ('security', 'Security Group'),              # Standard AD security group
    ('microsoft365', 'Microsoft 365 Group'),     # Unified group with Teams/SharePoint
    ('mail_security', 'Mail-Enabled Security'),  # Security group with distribution list
    ('distribution', 'Distribution List'),       # Mail-only distribution
    ('dynamic_security', 'Dynamic Security'),    # Rule-based membership
    ('dynamic_m365', 'Dynamic Microsoft 365'),   # Dynamic M365 group
]
```
**Decision**: Hardcoded choices. No custom types allowed to maintain Azure AD compatibility.

#### Group Source (Management Control)
```python
GROUP_SOURCE_CHOICES = [
    ('azure_ad', 'Azure AD Native'),      # Created in cloud, fully manageable
    ('on_premises', 'On-Premises AD'),    # Synced from AD, read-only in cloud
    ('external', 'External Directory'),   # Future: B2B/partner directories
]
```

## Django Models

### AzureGroup Model
```python
class AzureGroup(NetBoxModel):
    """Azure AD group representation in NetBox."""
    
    # Azure AD Identity
    object_id = models.CharField(
        max_length=36, 
        unique=True,
        validators=[validate_uuid],
        help_text="Azure AD object GUID"
    )
    name = models.CharField(max_length=256, db_index=True)
    description = models.TextField(blank=True)
    
    # Classification
    group_type = models.CharField(
        max_length=50,
        choices=GROUP_TYPE_CHOICES,
        db_index=True
    )
    source = models.CharField(
        max_length=50,
        choices=GROUP_SOURCE_CHOICES,
        db_index=True,
        help_text="Where group is mastered"
    )
    
    # Azure AD Properties
    is_security_enabled = models.BooleanField(default=False)
    is_mail_enabled = models.BooleanField(default=False)
    mail = models.EmailField(blank=True, db_index=True)
    
    # Dynamic Membership
    membership_type = models.CharField(
        max_length=20,
        choices=[('assigned', 'Assigned'), ('dynamic', 'Dynamic')],
        default='assigned'
    )
    membership_rule = models.TextField(
        blank=True,
        help_text="Azure AD dynamic membership rule"
    )
    
    # Statistics (denormalized for performance)
    member_count = models.IntegerField(default=0)
    owner_count = models.IntegerField(default=0)
    
    # Azure AD Timestamps
    azure_created = models.DateTimeField(null=True, blank=True)
    azure_modified = models.DateTimeField(null=True, blank=True)
    
    # Plugin Tracking
    last_sync = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag for audit retention"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Azure Group'
        indexes = [
            models.Index(fields=['source', 'group_type']),
            models.Index(fields=['last_sync']),
        ]
    
    def clean(self):
        # Enforce read-only for on-premises groups
        if self.pk and self.source == 'on_premises':
            original = AzureGroup.objects.get(pk=self.pk)
            allowed_fields = {'tags', 'custom_field_data', 'comments'}
            for field in self._meta.fields:
                if field.name not in allowed_fields:
                    if getattr(self, field.name) != getattr(original, field.name):
                        raise ValidationError(
                            f"Cannot modify {field.name}: On-premises groups are read-only"
                        )
    
    @property
    def is_stale(self):
        """Check if data is older than 24 hours."""
        return self.last_sync < timezone.now() - timedelta(hours=24)
    
    @property
    def can_modify(self):
        """Check if group properties can be modified."""
        return self.source != 'on_premises'
```

### GroupMembership Model
```python
class GroupMembership(models.Model):
    """Many-to-many relationship between groups and contacts/devices."""
    
    group = models.ForeignKey(
        AzureGroup,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    # Member can be contact OR device
    contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='azure_group_memberships'
    )
    device = models.ForeignKey(
        'dcim.Device',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='azure_group_memberships'
    )
    
    membership_type = models.CharField(
        max_length=20,
        choices=[
            ('direct', 'Direct Member'),
            ('nested', 'Via Nested Group'),
            ('dynamic', 'Dynamic Rule Match'),
        ],
        default='direct'
    )
    
    # For nested memberships, store the path
    nested_via = models.JSONField(
        blank=True,
        null=True,
        help_text="Group IDs traversed for nested membership"
    )
    
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ['group', 'contact'],
            ['group', 'device'],
        ]
        indexes = [
            models.Index(fields=['group', 'membership_type']),
        ]
    
    def clean(self):
        # Ensure either contact OR device, not both
        if not (self.contact or self.device):
            raise ValidationError("Must specify either contact or device")
        if self.contact and self.device:
            raise ValidationError("Cannot specify both contact and device")
```

### GroupOwnership Model
```python
class GroupOwnership(models.Model):
    """Group ownership tracking separate from membership."""
    
    group = models.ForeignKey(
        AzureGroup,
        on_delete=models.CASCADE,
        related_name='ownerships'
    )
    contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.CASCADE,
        related_name='owned_azure_groups'
    )
    assigned_date = models.DateTimeField()
    
    class Meta:
        unique_together = [['group', 'contact']]
        verbose_name = 'Group Ownership'
```

## API Implementation

### ViewSet with Source-Based Permissions
```python
class AzureGroupViewSet(NetBoxModelViewSet):
    queryset = AzureGroup.objects.filter(is_deleted=False)
    serializer_class = AzureGroupSerializer
    filterset_class = AzureGroupFilterSet
    
    def get_serializer_class(self):
        # Use read-only serializer for on-premises groups
        if self.action in ['update', 'partial_update']:
            obj = self.get_object()
            if obj.source == 'on_premises':
                return AzureGroupReadOnlySerializer
        return super().get_serializer_class()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Quick statistics endpoint."""
        return Response({
            'total': self.queryset.count(),
            'by_source': {
                'azure_ad': self.queryset.filter(source='azure_ad').count(),
                'on_premises': self.queryset.filter(source='on_premises').count(),
            },
            'by_type': {
                choice[0]: self.queryset.filter(group_type=choice[0]).count()
                for choice in GROUP_TYPE_CHOICES
            },
            'stale_count': self.queryset.filter(
                last_sync__lt=timezone.now() - timedelta(hours=24)
            ).count(),
        })
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Paginated member list."""
        group = self.get_object()
        memberships = group.memberships.select_related('contact', 'device')
        
        # Pagination
        paginator = self.paginator
        page = paginator.paginate_queryset(memberships, request)
        serializer = GroupMembershipSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
```

## UI Components

### Template Tags for Read-Only Indication
```python
# templatetags/azure_groups.py
@register.simple_tag
def group_badge(group):
    """Generate badge HTML for group source/type."""
    badges = []
    
    if group.source == 'on_premises':
        badges.append('<span class="badge bg-warning">On-Premises</span>')
        badges.append('<i class="mdi mdi-lock" title="Read-only"></i>')
    
    if group.is_stale:
        badges.append('<span class="badge bg-danger">Stale</span>')
    
    if group.membership_type == 'dynamic':
        badges.append('<span class="badge bg-info">Dynamic</span>')
    
    return mark_safe(' '.join(badges))
```

### Forms with Conditional Fields
```python
class AzureGroupForm(NetBoxModelForm):
    class Meta:
        model = AzureGroup
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance.pk and self.instance.source == 'on_premises':
            # Make all fields except tags/comments read-only
            for field_name in self.fields:
                if field_name not in ['tags', 'comments']:
                    self.fields[field_name].disabled = True
                    self.fields[field_name].help_text = "On-premises groups are read-only"
```

## Why Limited Sync Features Belong in Plugin

### 1. **Data Freshness Indicators** (Essential)
Users must know if they're looking at current data:
- `last_sync` field shows when data was updated
- `is_stale` property warns about old data
- Visual indicators in UI prevent decisions on outdated info

### 2. **Source-Based Access Control** (Essential)
The plugin must enforce Azure AD's management model:
- On-premises groups are read-only at the model level
- API returns proper HTTP codes (403) with clear messages
- UI disables editing for on-premises groups

### 3. **Validation at Plugin Level** (Essential)
Data integrity must be enforced regardless of how data enters:
- UUID validation for object_id
- Email validation for mail-enabled groups
- Unique constraints on object_id
- Relationship integrity (contact OR device, not both)

### 4. **Simple Sync Status** (Optional but Valuable)
```python
# Just enough visibility without full sync orchestration
@action(detail=False, methods=['get'], url_path='sync-status')
def sync_status(self, request):
    """Basic sync health check."""
    return Response({
        'last_update': cache.get('azure_groups_last_sync'),
        'pending_changes': cache.get('azure_groups_pending_changes', 0),
        'health': 'healthy' if not self.queryset.filter(
            last_sync__lt=timezone.now() - timedelta(hours=24)
        ).exists() else 'stale'
    })
```

## Configuration

### Plugin Settings
```python
# configuration.py
class AzureGroupsConfig(PluginConfig):
    name = 'azure_groups'
    verbose_name = 'Azure Groups'
    version = '1.0.0'
    
    # Plugin-specific settings
    default_settings = {
        'allow_manual_creation': False,  # Prevent UI group creation in production
        'stale_threshold_hours': 24,     # When to show stale warnings
        'soft_delete_retention_days': 30,  # Audit trail retention
        'max_members_display': 100,       # UI pagination limit
    }
```

## Success Criteria (Plugin Only)

1. **Data Integrity**
   - On-premises groups cannot be modified via API/UI
   - Object IDs are unique and valid UUIDs
   - Relationships maintain referential integrity

2. **User Experience**
   - Clear visual indicators for group source
   - Stale data warnings when appropriate
   - Fast member/owner lookups with pagination

3. **API Compliance**
   - Returns 403 for unauthorized modifications
   - Provides clear error messages
   - Supports filtering by all key fields

4. **Performance**
   - Efficient queries with proper indexes
   - Denormalized counts for fast statistics
   - Pagination for large member lists