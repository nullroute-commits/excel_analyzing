"""Management command to create cache tables for database cache backend."""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    """Create cache tables for database cache backend."""
    
    help = "Create cache tables for database cache backend"
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        self.stdout.write("Creating cache tables...")
        
        try:
            # Create cache table using Django's built-in command
            call_command("createcachetable")
            self.stdout.write(
                self.style.SUCCESS("Successfully created cache tables")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to create cache tables: {e}")
            )
            raise