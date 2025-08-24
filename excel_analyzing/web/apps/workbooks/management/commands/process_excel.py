"""Management command to process Excel files."""

import argparse
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from excel_analyzing.pipeline.orchestrator import ExcelPipeline
from excel_analyzing.models.schemas import ProcessingOptions


class Command(BaseCommand):
    """Django management command for processing Excel files."""
    
    help = 'Process Excel workbooks in the specified directory'
    
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            'path',
            type=str,
            help='Path to Excel file or directory'
        )
        parser.add_argument(
            '--recursive',
            action='store_true',
            help='Process subdirectories recursively'
        )
        parser.add_argument(
            '--drop-empty-rows',
            action='store_true',
            default=True,
            help='Drop completely empty rows'
        )
        parser.add_argument(
            '--drop-empty-columns',
            action='store_true',
            default=True,
            help='Drop completely empty columns'
        )
        parser.add_argument(
            '--clean-column-names',
            action='store_true',
            default=True,
            help='Clean and normalize column names'
        )
        parser.add_argument(
            '--null-threshold',
            type=float,
            default=0.9,
            help='Threshold for dropping columns with too many nulls'
        )
    
    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        path = Path(options['path'])
        
        if not path.exists():
            raise CommandError(f"Path does not exist: {path}")
        
        # Create processing options
        processing_options = ProcessingOptions(
            drop_empty_rows=options['drop_empty_rows'],
            drop_empty_columns=options['drop_empty_columns'],
            clean_column_names=options['clean_column_names'],
            null_threshold=options['null_threshold'],
        )
        
        # Initialize pipeline
        pipeline = ExcelPipeline(processing_options)
        
        self.stdout.write(f"Processing path: {path}")
        
        start_time = timezone.now()
        
        if path.is_file():
            # Process single file
            result = pipeline.process_workbook(path)
            results = [result]
        else:
            # Process directory
            results = pipeline.process_directory(path, options['recursive'])
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        # Summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nProcessing completed in {duration:.2f} seconds:"
            )
        )
        self.stdout.write(f"  Successful: {successful}")
        self.stdout.write(f"  Failed: {failed}")
        self.stdout.write(f"  Total: {len(results)}")
        
        if failed > 0:
            self.stdout.write("\nFailed files:")
            for result in results:
                if not result.success:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  {result.workbook.file_name}: {result.error_message}"
                        )
                    )