"""SQLAlchemy database models."""

from typing import Optional

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Text, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

from ..core.config import settings

Base = declarative_base()


class WorkbookModel(Base):
    """Database model for Excel workbooks."""

    __tablename__ = "workbooks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String(1000), nullable=False, unique=True)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    sheet_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    sheets = relationship(
        "SheetModel", back_populates="workbook", cascade="all, delete-orphan"
    )
    processing_results = relationship(
        "ProcessingResultModel", back_populates="workbook", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of workbook."""
        return f"<WorkbookModel(id={self.id}, file_name='{self.file_name}')>"


class SheetModel(Base):
    """Database model for Excel sheets."""

    __tablename__ = "sheets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workbook_id = Column(
        Integer, ForeignKey("workbooks.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    row_count = Column(Integer, nullable=False, default=0)
    column_count = Column(Integer, nullable=False, default=0)
    has_header = Column(Boolean, nullable=False, default=True)
    header_row = Column(Integer, nullable=False, default=0)
    data_start_row = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    workbook = relationship("WorkbookModel", back_populates="sheets")
    columns = relationship(
        "ColumnModel", back_populates="sheet", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of sheet."""
        return (
            f"<SheetModel(id={self.id}, name='{self.name}', "
            f"workbook_id={self.workbook_id})>"
        )


class ColumnModel(Base):
    """Database model for Excel columns."""

    __tablename__ = "columns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sheet_id = Column(
        Integer, ForeignKey("sheets.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    position = Column(Integer, nullable=False)
    data_type = Column(String(50), nullable=False)
    is_nullable = Column(Boolean, nullable=False, default=True)
    unique_count = Column(Integer, nullable=True)
    null_count = Column(Integer, nullable=False, default=0)
    sample_values = Column(Text, nullable=True)  # JSON string of sample values
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    sheet = relationship("SheetModel", back_populates="columns")

    def __repr__(self) -> str:
        """String representation of column."""
        return (
            f"<ColumnModel(id={self.id}, name='{self.name}', sheet_id={self.sheet_id})>"
        )


class ProcessingResultModel(Base):
    """Database model for processing results."""

    __tablename__ = "processing_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workbook_id = Column(
        Integer, ForeignKey("workbooks.id", ondelete="CASCADE"), nullable=False
    )
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    rows_processed = Column(Integer, nullable=False, default=0)
    columns_processed = Column(Integer, nullable=False, default=0)
    processing_time_seconds = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    workbook = relationship("WorkbookModel", back_populates="processing_results")

    def __repr__(self) -> str:
        """String representation of processing result."""
        return (
            f"<ProcessingResultModel(id={self.id}, "
            f"workbook_id={self.workbook_id}, success={self.success})>"
        )


class DatabaseManager:
    """Database connection and session management."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager."""
        self.database_url = database_url or settings.database_url
        self.engine = create_engine(
            self.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            echo=settings.debug,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self) -> None:
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self):
        """Get database session."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()
