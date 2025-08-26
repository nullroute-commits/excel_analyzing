"""Command-line interface for Excel analyzing."""

import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .core.config import settings
from .models.database import db_manager
from .models.schemas import ProcessingOptions
from .pipeline.orchestrator import ExcelPipeline

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("excel_analyzing.log"),
        ],
    )


@click.group()
@click.option("--log-level", default="INFO", help="Logging level")
@click.pass_context
def cli(ctx: click.Context, log_level: str) -> None:
    """Excel Analyzing CLI - Analyze Excel workbooks like databases."""
    ctx.ensure_object(dict)
    ctx.obj["log_level"] = log_level
    setup_logging(log_level)


@cli.command()
def init_db() -> None:
    """Initialize the database tables."""
    try:
        db_manager.create_tables()
        console.print("✅ Database tables created successfully!", style="green")
    except Exception as e:
        console.print(f"❌ Failed to create database tables: {e}", style="red")
        raise click.Abort()


@cli.command()
@click.option("--confirm", is_flag=True, help="Confirm database reset")
def reset_db(confirm: bool) -> None:
    """Reset the database (drop and recreate tables)."""
    if not confirm:
        if not click.confirm("This will delete all data. Are you sure?"):
            console.print("Operation cancelled.", style="yellow")
            return

    try:
        db_manager.drop_tables()
        db_manager.create_tables()
        console.print("✅ Database reset successfully!", style="green")
    except Exception as e:
        console.print(f"❌ Failed to reset database: {e}", style="red")
        raise click.Abort()


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    default=True,
    help="Process subdirectories recursively",
)
@click.option(
    "--drop-empty-rows", is_flag=True, default=True, help="Drop completely empty rows"
)
@click.option(
    "--drop-empty-columns",
    is_flag=True,
    default=True,
    help="Drop completely empty columns",
)
@click.option(
    "--clean-column-names",
    is_flag=True,
    default=True,
    help="Clean and normalize column names",
)
@click.option(
    "--null-threshold",
    type=float,
    default=0.9,
    help="Threshold for dropping columns with too many nulls",
)
def process(
    path: Path,
    recursive: bool,
    drop_empty_rows: bool,
    drop_empty_columns: bool,
    clean_column_names: bool,
    null_threshold: float,
) -> None:
    """Process Excel workbooks in the specified path."""

    # Create processing options
    try:
        options = ProcessingOptions(
            drop_empty_rows=drop_empty_rows,
            drop_empty_columns=drop_empty_columns,
            clean_column_names=clean_column_names,
            null_threshold=null_threshold,
        )
    except Exception as e:
        console.print(f"❌ Invalid options: {e}", style="red")
        raise click.BadParameter(str(e))

    # Initialize pipeline
    pipeline = ExcelPipeline(options)

    console.print(f"🔍 Discovering Excel files in: {path}")

    # Discover files
    files = list(pipeline.discover_workbooks(path, recursive))

    if not files:
        console.print("No Excel files found.", style="yellow")
        return

    console.print(f"📊 Found {len(files)} Excel file(s)")

    # Process files with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("Processing files...", total=len(files))

        successful = 0
        failed = 0

        for file_path in files:
            progress.update(task, description=f"Processing {file_path.name}")

            result = pipeline.process_workbook(file_path)

            if result.success:
                successful += 1
                console.print(f"✅ {file_path.name}", style="green")
            else:
                failed += 1
                console.print(
                    f"❌ {file_path.name}: {result.error_message}", style="red"
                )

            progress.advance(task)

    # Summary
    console.print("\n📈 Processing Summary:")
    console.print(f"  ✅ Successful: {successful}")
    console.print(f"  ❌ Failed: {failed}")
    console.print(f"  📁 Total: {len(files)}")


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def analyze(path: Path) -> None:
    """Analyze a specific Excel workbook and show detailed information."""

    if path.is_dir():
        console.print("❌ Please specify a file, not a directory", style="red")
        return

    # Initialize pipeline
    pipeline = ExcelPipeline()

    console.print(f"🔍 Analyzing: {path}")

    try:
        # Process the workbook
        result = pipeline.process_workbook(path)

        if not result.success:
            console.print(f"❌ Failed to process: {result.error_message}", style="red")
            return

        workbook = result.workbook

        # Display workbook information
        console.print(f"\n📊 Workbook: {workbook.file_name}")
        console.print(f"   📂 Size: {workbook.file_size_bytes / 1024 / 1024:.2f} MB")
        console.print(f"   📋 Sheets: {workbook.sheet_count}")
        console.print(f"   ⏱️  Processing time: {result.processing_time_seconds:.2f}s")

        # Display sheet information
        for sheet in workbook.sheets:
            console.print(f"\n📄 Sheet: {sheet.name}")
            console.print(
                f"   📏 Dimensions: {sheet.row_count} rows × "
                f"{sheet.column_count} columns"
            )
            console.print(
                f"   📝 Header: Row {sheet.header_row} "
                f"({'Yes' if sheet.has_header else 'No'})"
            )

            # Create columns table
            if sheet.columns:
                table = Table(title=f"Columns in '{sheet.name}'")
                table.add_column("Name", style="cyan")
                table.add_column("Type", style="magenta")
                table.add_column("Nulls", style="yellow")
                table.add_column("Unique", style="green")
                table.add_column("Sample", style="dim")

                for col in sheet.columns:
                    sample_str = ", ".join(str(v) for v in col.sample_values[:3])
                    if len(col.sample_values) > 3:
                        sample_str += "..."

                    table.add_row(
                        col.name,
                        col.data_type.value,
                        str(col.null_count),
                        (
                            str(col.unique_count)
                            if col.unique_count is not None
                            else "N/A"
                        ),
                        sample_str,
                    )

                console.print(table)

    except Exception as e:
        console.print(f"❌ Error analyzing workbook: {e}", style="red")


@cli.command()
def list_workbooks() -> None:
    """List all processed workbooks in the database."""
    from sqlalchemy.orm import Session

    from .models.database import WorkbookModel

    session: Session = next(db_manager.get_session())

    try:
        workbooks = (
            session.query(WorkbookModel).order_by(WorkbookModel.created_at.desc()).all()
        )

        if not workbooks:
            console.print("No workbooks found in database.", style="yellow")
            return

        table = Table(title="Processed Workbooks")
        table.add_column("File Name", style="cyan")
        table.add_column("Sheets", style="magenta")
        table.add_column("Size (MB)", style="yellow")
        table.add_column("Processed", style="green")

        for wb in workbooks:
            size_mb = wb.file_size_bytes / 1024 / 1024
            processed_time = (
                wb.processed_at.strftime("%Y-%m-%d %H:%M")
                if wb.processed_at
                else "Never"
            )

            table.add_row(
                wb.file_name,
                str(wb.sheet_count),
                f"{size_mb:.2f}",
                processed_time,
            )

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error listing workbooks: {e}", style="red")
    finally:
        session.close()


@cli.command()
@click.argument("workbook_name")
@click.argument("sheet_name")
@click.option("--filter", "filter_condition", help="Pandas query filter condition")
@click.option("--limit", type=int, default=10, help="Limit number of rows to display")
def query(
    workbook_name: str, sheet_name: str, filter_condition: Optional[str], limit: int
) -> None:
    """Query data from a specific sheet."""

    # Initialize pipeline
    pipeline = ExcelPipeline()

    # Get dataframe
    df = pipeline.processor.get_dataframe(workbook_name, sheet_name)

    if df is None:
        console.print(
            f"❌ Sheet '{sheet_name}' not found in workbook '{workbook_name}'",
            style="red",
        )
        return

    # Apply filter if specified
    if filter_condition:
        df = pipeline.processor.apply_filter(
            workbook_name, sheet_name, filter_condition
        )
        if df is None:
            console.print(
                f"❌ Invalid filter condition: {filter_condition}", style="red"
            )
            return

    # Limit rows
    df_display = df.head(limit)

    console.print(f"📊 Data from {workbook_name} → {sheet_name}")
    if filter_condition:
        console.print(f"🔍 Filter: {filter_condition}")
    console.print(f"📏 Showing {len(df_display)} of {len(df)} rows\n")

    # Convert to rich table
    table = Table()

    for col in df_display.columns:
        table.add_column(str(col), style="cyan")

    for _, row in df_display.iterrows():
        table.add_row(*[str(val) for val in row])

    console.print(table)


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
