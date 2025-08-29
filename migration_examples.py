#!/usr/bin/env python3
"""
NetBox Migration Agent - Example Usage Scripts

Demonstrates common migration workflows using the NetBoxMigrationAgent.
These examples show how to use the agent for typical NetBox plugin development tasks.
"""

from netbox_migration_agent import NetBoxMigrationAgent, MigrationStatus
import sys
import time


def example_plugin_development_workflow():
    """
    Example: Complete plugin development workflow with migrations
    """
    print("=== NetBox Plugin Development Workflow ===")
    
    # Initialize agent
    agent = NetBoxMigrationAgent("brynjar@10.0.123.5", "netbox-docker/")
    
    # 1. Check Docker status first
    print("\n1. Checking Docker container status...")
    docker_result = agent.check_docker_status()
    print(f"   Status: {docker_result.status.value}")
    print(f"   Message: {docker_result.message}")
    
    if docker_result.status != MigrationStatus.SUCCESS:
        print("   ⚠️  Docker containers not running properly!")
        return False
    
    # 2. Check current migration status
    print("\n2. Checking current migration status...")
    status_result = agent.show_migrations("netbox_azure_groups")
    print(f"   Status: {status_result.status.value}")
    if status_result.output:
        print("   Current migrations:")
        for line in status_result.output.split('\n'):
            if 'netbox_azure_groups' in line:
                print(f"     {line.strip()}")
    
    # 3. Create new migrations (if model changes exist)
    print("\n3. Creating new migrations...")
    make_result = agent.makemigrations("netbox_azure_groups")
    print(f"   Status: {make_result.status.value}")
    print(f"   Message: {make_result.message}")
    
    if make_result.output:
        print("   Output:")
        for line in make_result.output.split('\n'):
            if line.strip():
                print(f"     {line}")
    
    # 4. Apply migrations
    if make_result.status == MigrationStatus.SUCCESS and "Created migration" in make_result.output:
        print("\n4. Applying new migrations...")
        migrate_result = agent.migrate("netbox_azure_groups")
        print(f"   Status: {migrate_result.status.value}")
        print(f"   Message: {migrate_result.message}")
        
        if migrate_result.output:
            print("   Migration output:")
            for line in migrate_result.output.split('\n'):
                if line.strip():
                    print(f"     {line}")
    else:
        print("\n4. No new migrations to apply")
    
    # 5. Final status check
    print("\n5. Final migration status...")
    final_result = agent.show_migrations("netbox_azure_groups")
    if final_result.output:
        print("   Final state:")
        for line in final_result.output.split('\n'):
            if 'netbox_azure_groups' in line:
                print(f"     {line.strip()}")
    
    print("\n✅ Plugin development workflow complete!")
    return True


def example_migration_rollback():
    """
    Example: Rolling back problematic migrations
    """
    print("=== Migration Rollback Example ===")
    
    agent = NetBoxMigrationAgent("brynjar@10.0.123.5", "netbox-docker/")
    
    # Show current status
    print("\n1. Current migration status:")
    status_result = agent.show_migrations("netbox_azure_groups")
    if status_result.output:
        for line in status_result.output.split('\n'):
            if 'netbox_azure_groups' in line:
                print(f"   {line.strip()}")
    
    # Example rollback to previous migration
    print("\n2. Rolling back to migration 0004...")
    rollback_result = agent.rollback("netbox_azure_groups", "0004")
    print(f"   Status: {rollback_result.status.value}")
    print(f"   Message: {rollback_result.message}")
    
    if rollback_result.output:
        print("   Rollback output:")
        for line in rollback_result.output.split('\n'):
            if line.strip():
                print(f"     {line}")
    
    # Verify rollback
    print("\n3. Verifying rollback...")
    verify_result = agent.show_migrations("netbox_azure_groups")
    if verify_result.output:
        for line in verify_result.output.split('\n'):
            if 'netbox_azure_groups' in line:
                print(f"   {line.strip()}")
    
    print("\n✅ Rollback example complete!")


def example_dry_run_testing():
    """
    Example: Using dry-run to test migrations safely
    """
    print("=== Dry Run Testing Example ===")
    
    agent = NetBoxMigrationAgent("brynjar@10.0.123.5", "netbox-docker/")
    
    # Test what migrations would be created
    print("\n1. Dry run - checking what migrations would be created...")
    dry_result = agent.makemigrations("netbox_azure_groups", dry_run=True)
    print(f"   Status: {dry_result.status.value}")
    print(f"   Message: {dry_result.message}")
    
    if dry_result.output:
        print("   Would create:")
        for line in dry_result.output.split('\n'):
            if line.strip():
                print(f"     {line}")
    
    # Check migration plan
    print("\n2. Checking migration plan...")
    plan_result = agent.show_migrations("netbox_azure_groups", plan=True)
    print(f"   Status: {plan_result.status.value}")
    
    if plan_result.output:
        print("   Migration plan:")
        for line in plan_result.output.split('\n'):
            if line.strip():
                print(f"     {line}")
    
    print("\n✅ Dry run testing complete!")


def example_comprehensive_summary():
    """
    Example: Getting comprehensive migration summary
    """
    print("=== Comprehensive Migration Summary ===")
    
    agent = NetBoxMigrationAgent("brynjar@10.0.123.5", "netbox-docker/")
    
    # Get full summary
    print("\n1. Generating comprehensive summary...")
    summary = agent.get_migration_summary("netbox_azure_groups")
    
    print("\nSummary Report:")
    print("-" * 50)
    
    # Docker status
    docker_info = summary.get("docker_status", {})
    print(f"Docker Status: {docker_info.get('status', 'unknown')}")
    print(f"Docker Healthy: {docker_info.get('healthy', False)}")
    print(f"Docker Message: {docker_info.get('message', 'N/A')}")
    
    # Migration status
    migration_info = summary.get("migration_status", {})
    print(f"\nMigration Status: {migration_info.get('status', 'unknown')}")
    
    # Applied migrations
    applied = summary.get("applied_migrations", [])
    if applied:
        print(f"\nApplied Migrations ({len(applied)}):")
        for migration in applied:
            print(f"  ✅ {migration}")
    
    # Pending migrations
    pending = summary.get("pending_migrations", [])
    if pending:
        print(f"\nPending Migrations ({len(pending)}):")
        for migration in pending:
            print(f"  ⏳ {migration}")
    else:
        print("\nNo pending migrations")
    
    # Errors
    errors = summary.get("errors", [])
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors:
            print(f"  ❌ {error}")
    
    print("-" * 50)
    print("✅ Summary complete!")


def example_custom_migration_workflow():
    """
    Example: Creating and applying custom named migrations
    """
    print("=== Custom Migration Workflow ===")
    
    agent = NetBoxMigrationAgent("brynjar@10.0.123.5", "netbox-docker/")
    
    # Create custom named migration
    custom_name = f"add_feature_{int(time.time())}"
    print(f"\n1. Creating custom migration: {custom_name}")
    
    make_result = agent.makemigrations(
        app_name="netbox_azure_groups",
        migration_name=custom_name
    )
    
    print(f"   Status: {make_result.status.value}")
    print(f"   Message: {make_result.message}")
    
    if make_result.output:
        print("   Output:")
        for line in make_result.output.split('\n'):
            if line.strip():
                print(f"     {line}")
    
    # Apply the specific migration
    if make_result.status == MigrationStatus.SUCCESS:
        print(f"\n2. Applying custom migration...")
        migrate_result = agent.migrate("netbox_azure_groups")
        print(f"   Status: {migrate_result.status.value}")
        print(f"   Message: {migrate_result.message}")
    
    print("\n✅ Custom migration workflow complete!")


def main():
    """
    Interactive example selector
    """
    print("NetBox Migration Agent - Example Usage")
    print("=" * 45)
    
    examples = {
        "1": ("Complete plugin development workflow", example_plugin_development_workflow),
        "2": ("Migration rollback example", example_migration_rollback),
        "3": ("Dry run testing", example_dry_run_testing),
        "4": ("Comprehensive summary", example_comprehensive_summary),
        "5": ("Custom migration workflow", example_custom_migration_workflow)
    }
    
    print("\nAvailable examples:")
    for key, (description, _) in examples.items():
        print(f"  {key}. {description}")
    
    print("  q. Quit")
    
    while True:
        choice = input("\nSelect example (1-5, q): ").strip().lower()
        
        if choice == "q":
            print("Goodbye!")
            break
        elif choice in examples:
            description, example_func = examples[choice]
            print(f"\nRunning: {description}")
            try:
                example_func()
            except KeyboardInterrupt:
                print("\n⚠️  Example interrupted by user")
            except Exception as e:
                print(f"❌ Error running example: {e}")
            
            input("\nPress Enter to continue...")
        else:
            print("Invalid choice. Please select 1-5 or q.")


if __name__ == "__main__":
    main()