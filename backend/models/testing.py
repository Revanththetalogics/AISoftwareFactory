"""Testing data models for test results and coverage."""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.db.base import Base


class TestRun(Base):
    """Model for test execution runs."""

    __tablename__ = "test_runs"

    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=False)
    status = Column(String(20), nullable=False)  # passed, failed, running
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    coverage_percent = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    extra_metadata = Column(JSON, default=dict)

    # Relationships
    project = relationship("Project", back_populates="test_runs")
    test_cases = relationship("TestCase", back_populates="test_run", cascade="all, delete-orphan")
    bugs = relationship("Bug", back_populates="test_run", cascade="all, delete-orphan")


class TestCase(Base):
    """Model for individual test cases."""

    __tablename__ = "test_cases"

    id = Column(String(50), primary_key=True)
    test_run_id = Column(String(50), ForeignKey("test_runs.id"), nullable=False)
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False)  # passed, failed, skipped
    duration_seconds = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)
    extra_metadata = Column(JSON, default=dict)

    # Relationships
    test_run = relationship("TestRun", back_populates="test_cases")


class Bug(Base):
    """Model for bugs found during testing."""

    __tablename__ = "bugs"

    id = Column(String(50), primary_key=True)
    test_run_id = Column(String(50), ForeignKey("test_runs.id"), nullable=True)
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    status = Column(String(20), nullable=False)  # open, in_progress, resolved, closed
    file_path = Column(String(500), nullable=True)
    line_number = Column(Integer, nullable=True)
    found_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    extra_metadata = Column(JSON, default=dict)

    # Relationships
    test_run = relationship("TestRun", back_populates="bugs")
    project = relationship("Project")


class CodeCoverage(Base):
    """Model for code coverage data."""

    __tablename__ = "code_coverage"

    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    total_lines = Column(Integer, default=0)
    covered_lines = Column(Integer, default=0)
    coverage_percent = Column(Float, default=0.0)
    branch_coverage = Column(Float, default=0.0)
    measured_at = Column(DateTime, default=datetime.utcnow)
    extra_metadata = Column(JSON, default=dict)

    # Relationships
    project = relationship("Project")
