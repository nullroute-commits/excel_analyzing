"""Excel processing pipeline orchestrator."""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Generator, List, Optional

from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.database import (
    ColumnModel,
    ProcessingResultModel,
    SheetModel,
    WorkbookModel,
    db_manager,
)
from ..models.schemas import ProcessingOptions, ProcessingResult, WorkbookInfo
from .processor import ExcelDataProcessor

logger = logging.getLogger(__name__)


class ExcelPipeline:
    """Excel workbook processing pipeline."""
    
    def __init__(self, processing_options: Optional[ProcessingOptions] = None):
        """Initialize the pipeline."""
        self.options = processing_options or ProcessingOptions()
        self.processor = ExcelDataProcessor(self.options)
    
    def discover_workbooks(self, path: Path, recursive: bool = True) -> Generator[Path, None, None]:
        """Discover Excel workbooks in a directory path."""
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        if path.is_file():
            if self._is_excel_file(path):
                yield path
            return
        
        if not path.is_dir():
            raise ValueError(f"Path is neither a file nor directory: {path}")
        
        # Define search pattern
        excel_patterns = ['*.xlsx', '*.xls', '*.xlsm', '*.xlsb']
        
        if recursive:
            for pattern in excel_patterns:
                for file_path in path.rglob(pattern):
                    if self._is_valid_excel_file(file_path):
                        yield file_path
        else:
            for pattern in excel_patterns:
                for file_path in path.glob(pattern):
                    if self._is_valid_excel_file(file_path):
                        yield file_path
    
    def _is_excel_file(self, file_path: Path) -> bool:
        """Check if file is an Excel file based on extension."""
        return file_path.suffix.lower() in {'.xlsx', '.xls', '.xlsm', '.xlsb'}
    
    def _is_valid_excel_file(self, file_path: Path) -> bool:
        """Check if file is a valid Excel file to process."""
        if not self._is_excel_file(file_path):
            return False
        
        # Skip temporary files
        if file_path.name.startswith('~$'):
            return False
        
        # Check file size
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > settings.max_file_size_mb:
                logger.warning(f"Skipping large file ({file_size_mb:.1f}MB): {file_path}")
                return False
        except OSError:
            logger.warning(f"Cannot access file: {file_path}")
            return False
        
        return True
    
    def process_workbook(self, file_path: Path) -> ProcessingResult:
        """Process a single Excel workbook."""
        start_time = time.time()
        
        try:
            logger.info(f"Processing workbook: {file_path}")
            
            # Process the workbook
            workbook_info = self.processor.load_workbook(file_path)
            
            # Calculate statistics
            total_rows = sum(sheet.row_count for sheet in workbook_info.sheets)
            total_columns = sum(sheet.column_count for sheet in workbook_info.sheets)
            
            # Save to database
            self._save_workbook_to_database(workbook_info)
            
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                workbook=workbook_info,
                success=True,
                rows_processed=total_rows,
                columns_processed=total_columns,
                processing_time_seconds=processing_time,
            )
            
            # Save processing result to database
            self._save_processing_result_to_database(result)
            
            logger.info(f"Successfully processed {file_path} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = str(e)
            
            logger.error(f"Failed to process {file_path}: {error_message}")
            
            # Create a minimal workbook info for failed processing
            workbook_info = WorkbookInfo(
                file_path=file_path,
                file_name=file_path.name,
                file_size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                sheet_count=0,
            )
            
            result = ProcessingResult(
                workbook=workbook_info,
                success=False,
                error_message=error_message,
                processing_time_seconds=processing_time,
            )
            
            # Save failed result to database
            try:
                self._save_processing_result_to_database(result)
            except Exception as db_error:
                logger.error(f"Failed to save error result to database: {db_error}")
            
            return result
    
    def process_directory(self, directory_path: Path, recursive: bool = True) -> List[ProcessingResult]:
        """Process all Excel workbooks in a directory."""
        results = []
        
        logger.info(f"Processing directory: {directory_path} (recursive={recursive})")
        
        for file_path in self.discover_workbooks(directory_path, recursive):
            result = self.process_workbook(file_path)
            results.append(result)
        
        successful_count = sum(1 for r in results if r.success)
        failed_count = len(results) - successful_count
        
        logger.info(f"Directory processing complete: {successful_count} successful, {failed_count} failed")
        
        return results
    
    def _save_workbook_to_database(self, workbook_info: WorkbookInfo) -> None:
        """Save workbook information to database."""
        session: Session = next(db_manager.get_session())
        
        try:
            # Check if workbook already exists
            existing_workbook = session.query(WorkbookModel).filter_by(
                file_path=str(workbook_info.file_path)
            ).first()
            
            if existing_workbook:
                # Update existing workbook
                workbook_model = existing_workbook
                workbook_model.file_name = workbook_info.file_name
                workbook_model.file_size_bytes = workbook_info.file_size_bytes
                workbook_model.sheet_count = workbook_info.sheet_count
                workbook_model.processed_at = workbook_info.processed_at
                
                # Delete existing sheets (cascade will handle columns)
                session.query(SheetModel).filter_by(workbook_id=workbook_model.id).delete()
            else:
                # Create new workbook
                workbook_model = WorkbookModel(
                    file_path=str(workbook_info.file_path),
                    file_name=workbook_info.file_name,
                    file_size_bytes=workbook_info.file_size_bytes,
                    sheet_count=workbook_info.sheet_count,
                    processed_at=workbook_info.processed_at,
                )
                session.add(workbook_model)
                session.flush()  # Get the ID
            
            # Save sheets
            for sheet_info in workbook_info.sheets:
                sheet_model = SheetModel(
                    workbook_id=workbook_model.id,
                    name=sheet_info.name,
                    original_name=sheet_info.original_name,
                    row_count=sheet_info.row_count,
                    column_count=sheet_info.column_count,
                    has_header=sheet_info.has_header,
                    header_row=sheet_info.header_row,
                    data_start_row=sheet_info.data_start_row,
                )
                session.add(sheet_model)
                session.flush()  # Get the ID
                
                # Save columns
                for column_info in sheet_info.columns:
                    column_model = ColumnModel(
                        sheet_id=sheet_model.id,
                        name=column_info.name,
                        original_name=column_info.original_name,
                        position=column_info.position,
                        data_type=column_info.data_type.value,
                        is_nullable=column_info.is_nullable,
                        unique_count=column_info.unique_count,
                        null_count=column_info.null_count,
                        sample_values=json.dumps(column_info.sample_values),
                    )
                    session.add(column_model)
            
            session.commit()
            logger.debug(f"Saved workbook to database: {workbook_info.file_name}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save workbook to database: {e}")
            raise
        finally:
            session.close()
    
    def _save_processing_result_to_database(self, result: ProcessingResult) -> None:
        """Save processing result to database."""
        session: Session = next(db_manager.get_session())
        
        try:
            # Get or create workbook
            workbook_model = session.query(WorkbookModel).filter_by(
                file_path=str(result.workbook.file_path)
            ).first()
            
            if not workbook_model:
                # Create minimal workbook entry for failed processing
                workbook_model = WorkbookModel(
                    file_path=str(result.workbook.file_path),
                    file_name=result.workbook.file_name,
                    file_size_bytes=result.workbook.file_size_bytes,
                    sheet_count=result.workbook.sheet_count,
                )
                session.add(workbook_model)
                session.flush()
            
            # Create processing result
            result_model = ProcessingResultModel(
                workbook_id=workbook_model.id,
                success=result.success,
                error_message=result.error_message,
                rows_processed=result.rows_processed,
                columns_processed=result.columns_processed,
                processing_time_seconds=result.processing_time_seconds,
            )
            session.add(result_model)
            session.commit()
            
            logger.debug(f"Saved processing result to database: {result.workbook.file_name}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save processing result to database: {e}")
            raise
        finally:
            session.close()
    
    def get_workbook_summary(self, file_path: Path) -> Optional[Dict]:
        """Get summary information for a processed workbook."""
        session: Session = next(db_manager.get_session())
        
        try:
            workbook_model = session.query(WorkbookModel).filter_by(
                file_path=str(file_path)
            ).first()
            
            if not workbook_model:
                return None
            
            sheets_info = []
            for sheet in workbook_model.sheets:
                columns_info = []
                for column in sheet.columns:
                    columns_info.append({
                        'name': column.name,
                        'original_name': column.original_name,
                        'data_type': column.data_type,
                        'null_count': column.null_count,
                        'unique_count': column.unique_count,
                    })
                
                sheets_info.append({
                    'name': sheet.name,
                    'original_name': sheet.original_name,
                    'row_count': sheet.row_count,
                    'column_count': sheet.column_count,
                    'columns': columns_info,
                })
            
            return {
                'file_name': workbook_model.file_name,
                'file_size_bytes': workbook_model.file_size_bytes,
                'sheet_count': workbook_model.sheet_count,
                'processed_at': workbook_model.processed_at.isoformat() if workbook_model.processed_at else None,
                'sheets': sheets_info,
            }
            
        except Exception as e:
            logger.error(f"Failed to get workbook summary: {e}")
            return None
        finally:
            session.close()