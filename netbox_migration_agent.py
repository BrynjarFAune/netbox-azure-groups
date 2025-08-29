#!/usr/bin/env python3
"""
NetBox Docker Migration Agent

A specialized agent for handling NetBox Docker migration workflows.
Provides SSH connectivity to remote NetBox Docker instances and executes
Django migration commands with proper error handling and status reporting.

Usage:
    agent = NetBoxMigrationAgent("brynjar@10.0.123.5", "/path/to/netbox-docker")
    result = agent.makemigrations("my_app", migration_name="custom_migration")
    result = agent.migrate("my_app", "0001")
    result = agent.show_migrations()
"""

import subprocess
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class MigrationStatus(Enum):
    """Migration operation status codes"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    NOT_FOUND = "not_found"


@dataclass
class MigrationResult:
    """Result of a migration operation"""
    status: MigrationStatus
    message: str
    output: str = ""
    error: str = ""
    command: str = ""
    exit_code: int = 0


class NetBoxMigrationAgent:
    """
    Specialized agent for NetBox Docker migration operations.
    
    Handles SSH connections to remote NetBox Docker instances and provides
    a clean interface for Django migration commands.
    """
    
    def __init__(self, ssh_target: str, netbox_docker_path: str = "netbox-docker/"):
        """
        Initialize the migration agent.
        
        Args:
            ssh_target: SSH connection string (e.g., "user@host")
            netbox_docker_path: Path to netbox-docker directory on remote host
        """
        self.ssh_target = ssh_target
        self.netbox_docker_path = netbox_docker_path
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _execute_ssh_command(self, command: str) -> MigrationResult:
        """
        Execute a command over SSH and return structured result.
        
        Args:
            command: Command to execute on remote host
            
        Returns:
            MigrationResult with status, output, and error information
        """
        # Build full SSH command
        ssh_command = [
            "ssh", self.ssh_target,
            f"cd {self.netbox_docker_path} && {command}"
        ]
        
        full_command = " ".join(ssh_command)
        self.logger.info(f"Executing: {full_command}")
        
        try:
            result = subprocess.run(
                ssh_command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            output = result.stdout.strip()
            error = result.stderr.strip()
            
            # Determine status based on exit code and output content
            if result.returncode == 0:
                status = MigrationStatus.SUCCESS
                message = "Command executed successfully"
                if "No changes detected" in output:
                    status = MigrationStatus.WARNING
                    message = "No changes detected in migration"
            else:
                status = MigrationStatus.ERROR
                message = f"Command failed with exit code {result.returncode}"
            
            return MigrationResult(
                status=status,
                message=message,
                output=output,
                error=error,
                command=full_command,
                exit_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return MigrationResult(
                status=MigrationStatus.ERROR,
                message="Command timed out after 5 minutes",
                command=full_command,
                exit_code=-1
            )
        except Exception as e:
            return MigrationResult(
                status=MigrationStatus.ERROR,
                message=f"Unexpected error: {str(e)}",
                command=full_command,
                exit_code=-1
            )
    
    def makemigrations(self, app_name: Optional[str] = None, 
                      migration_name: Optional[str] = None,
                      dry_run: bool = False) -> MigrationResult:
        """
        Create new Django migrations for the specified app.
        
        Args:
            app_name: Django app name (optional, creates for all apps if None)
            migration_name: Custom migration name (optional)
            dry_run: If True, show what would be created without making files
            
        Returns:
            MigrationResult with operation status and output
        """
        command_parts = ["docker", "compose", "exec", "netbox", "python", "manage.py", "makemigrations"]
        
        if dry_run:
            command_parts.append("--dry-run")
        
        if app_name:
            command_parts.append(app_name)
        
        if migration_name:
            command_parts.extend(["--name", migration_name])
        
        command = " ".join(command_parts)
        
        self.logger.info(f"Creating migrations for app: {app_name or 'all apps'}")
        if migration_name:
            self.logger.info(f"Migration name: {migration_name}")
        
        result = self._execute_ssh_command(command)
        
        # Log result
        if result.status == MigrationStatus.SUCCESS:
            self.logger.info("Migrations created successfully")
        elif result.status == MigrationStatus.WARNING:
            self.logger.warning("No migrations needed")
        else:
            self.logger.error(f"Migration creation failed: {result.message}")
        
        return result
    
    def migrate(self, app_name: Optional[str] = None, 
                migration_name: Optional[str] = None,
                fake: bool = False) -> MigrationResult:
        """
        Apply Django migrations for the specified app.
        
        Args:
            app_name: Django app name (optional, migrates all apps if None)
            migration_name: Specific migration to apply (optional)
            fake: If True, mark migration as applied without running SQL
            
        Returns:
            MigrationResult with operation status and output
        """
        command_parts = ["docker", "compose", "exec", "netbox", "python", "manage.py", "migrate"]
        
        if fake:
            command_parts.append("--fake")
        
        if app_name:
            command_parts.append(app_name)
            
            if migration_name:
                command_parts.append(migration_name)
        
        command = " ".join(command_parts)
        
        self.logger.info(f"Applying migrations for app: {app_name or 'all apps'}")
        if migration_name:
            self.logger.info(f"Target migration: {migration_name}")
        
        result = self._execute_ssh_command(command)
        
        # Log result
        if result.status == MigrationStatus.SUCCESS:
            self.logger.info("Migrations applied successfully")
        else:
            self.logger.error(f"Migration failed: {result.message}")
        
        return result
    
    def show_migrations(self, app_name: Optional[str] = None,
                       plan: bool = False) -> MigrationResult:
        """
        Show migration status for the specified app.
        
        Args:
            app_name: Django app name (optional, shows all apps if None)
            plan: If True, show migration plan instead of status
            
        Returns:
            MigrationResult with migration status information
        """
        command_parts = ["docker", "compose", "exec", "netbox", "python", "manage.py"]
        
        if plan:
            command_parts.extend(["migrate", "--plan"])
        else:
            command_parts.append("showmigrations")
        
        if app_name:
            command_parts.append(app_name)
        
        command = " ".join(command_parts)
        
        self.logger.info(f"Checking migration status for app: {app_name or 'all apps'}")
        
        result = self._execute_ssh_command(command)
        
        if result.status == MigrationStatus.SUCCESS:
            self.logger.info("Migration status retrieved successfully")
        else:
            self.logger.error(f"Failed to get migration status: {result.message}")
        
        return result
    
    def rollback(self, app_name: str, target_migration: str) -> MigrationResult:
        """
        Rollback migrations to a specific target.
        
        Args:
            app_name: Django app name
            target_migration: Migration to rollback to (e.g., "0001" or "zero")
            
        Returns:
            MigrationResult with rollback operation status
        """
        command_parts = [
            "docker", "compose", "exec", "netbox", 
            "python", "manage.py", "migrate", 
            app_name, target_migration
        ]
        
        command = " ".join(command_parts)
        
        self.logger.warning(f"Rolling back {app_name} to migration {target_migration}")
        
        result = self._execute_ssh_command(command)
        
        if result.status == MigrationStatus.SUCCESS:
            self.logger.info(f"Rollback completed successfully")
        else:
            self.logger.error(f"Rollback failed: {result.message}")
        
        return result
    
    def check_docker_status(self) -> MigrationResult:
        """
        Check if NetBox Docker containers are running.
        
        Returns:
            MigrationResult with Docker container status
        """
        command = "docker compose ps"
        
        self.logger.info("Checking Docker container status")
        
        result = self._execute_ssh_command(command)
        
        if result.status == MigrationStatus.SUCCESS:
            if "netbox" in result.output and "Up" in result.output:
                result.message = "NetBox container is running"
                self.logger.info("NetBox container is healthy")
            else:
                result.status = MigrationStatus.WARNING
                result.message = "NetBox container may not be running properly"
                self.logger.warning("NetBox container status unclear")
        
        return result
    
    def get_migration_summary(self, app_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a comprehensive migration summary for reporting.
        
        Args:
            app_name: Django app name (optional)
            
        Returns:
            Dictionary with migration summary information
        """
        summary = {
            "timestamp": None,
            "docker_status": None,
            "migration_status": None,
            "pending_migrations": [],
            "applied_migrations": [],
            "errors": []
        }
        
        try:
            # Check Docker status
            docker_result = self.check_docker_status()
            summary["docker_status"] = {
                "status": docker_result.status.value,
                "message": docker_result.message,
                "healthy": docker_result.status == MigrationStatus.SUCCESS
            }
            
            # Get migration status
            migration_result = self.show_migrations(app_name)
            summary["migration_status"] = {
                "status": migration_result.status.value,
                "output": migration_result.output,
                "error": migration_result.error
            }
            
            # Parse migration output to identify pending/applied
            if migration_result.status == MigrationStatus.SUCCESS:
                lines = migration_result.output.split('\n')
                for line in lines:
                    line = line.strip()
                    if '[X]' in line:
                        summary["applied_migrations"].append(line)
                    elif '[ ]' in line:
                        summary["pending_migrations"].append(line)
            
        except Exception as e:
            summary["errors"].append(f"Error generating summary: {str(e)}")
        
        return summary


def main():
    """Example usage and testing"""
    # Example configuration
    agent = NetBoxMigrationAgent("brynjar@10.0.123.5", "netbox-docker/")
    
    print("NetBox Migration Agent - Interactive Mode")
    print("Available commands:")
    print("1. check - Check Docker status")
    print("2. status - Show migration status")
    print("3. make [app] - Create migrations")
    print("4. migrate [app] - Apply migrations")
    print("5. summary - Get comprehensive summary")
    print("6. quit - Exit")
    
    while True:
        try:
            command = input("\n> ").strip().split()
            if not command:
                continue
                
            cmd = command[0].lower()
            
            if cmd == "quit":
                break
            elif cmd == "check":
                result = agent.check_docker_status()
                print(f"Status: {result.status.value}")
                print(f"Message: {result.message}")
                if result.output:
                    print(f"Output:\n{result.output}")
                    
            elif cmd == "status":
                app_name = command[1] if len(command) > 1 else None
                result = agent.show_migrations(app_name)
                print(f"Status: {result.status.value}")
                print(f"Output:\n{result.output}")
                
            elif cmd == "make":
                app_name = command[1] if len(command) > 1 else None
                result = agent.makemigrations(app_name)
                print(f"Status: {result.status.value}")
                print(f"Message: {result.message}")
                if result.output:
                    print(f"Output:\n{result.output}")
                    
            elif cmd == "migrate":
                app_name = command[1] if len(command) > 1 else None
                result = agent.migrate(app_name)
                print(f"Status: {result.status.value}")
                print(f"Message: {result.message}")
                if result.output:
                    print(f"Output:\n{result.output}")
                    
            elif cmd == "summary":
                app_name = command[1] if len(command) > 1 else None
                summary = agent.get_migration_summary(app_name)
                print("Migration Summary:")
                for key, value in summary.items():
                    print(f"  {key}: {value}")
                    
            else:
                print(f"Unknown command: {cmd}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()