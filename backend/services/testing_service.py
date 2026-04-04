"""Service for managing testing data and test runs."""

from uuid import uuid4

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.testing import Bug, CodeCoverage, TestCase, TestRun

logger = structlog.get_logger(__name__)


class TestingService:
    """Service for testing operations."""

    async def get_test_statistics(self, project_id: str = None, db: AsyncSession = None) -> dict:
        """Get overall test statistics."""
        try:
            query = select(TestRun)
            if project_id:
                query = query.where(TestRun.project_id == project_id)

            result = await db.execute(query)
            test_runs = result.scalars().all()

            total_tests = sum(run.total_tests for run in test_runs)
            passed_tests = sum(run.passed_tests for run in test_runs)
            failed_tests = sum(run.failed_tests for run in test_runs)

            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_runs": len(test_runs),
            }
        except Exception as e:
            logger.error("Failed to get test statistics", error=str(e))
            return {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "pass_rate": 0,
                "total_runs": 0,
            }

    async def list_test_runs(self, project_id: str = None, limit: int = 50, db: AsyncSession = None) -> list[TestRun]:
        """List test runs."""
        try:
            query = select(TestRun).order_by(TestRun.started_at.desc()).limit(limit)
            if project_id:
                query = query.where(TestRun.project_id == project_id)

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to list test runs", error=str(e))
            return []

    async def get_test_run(self, test_run_id: str, db: AsyncSession = None) -> TestRun | None:
        """Get a specific test run."""
        try:
            result = await db.execute(select(TestRun).where(TestRun.id == test_run_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Failed to get test run", test_run_id=test_run_id, error=str(e))
            return None

    async def list_bugs(
        self, project_id: str = None, status: str = None, severity: str = None, db: AsyncSession = None
    ) -> list[Bug]:
        """List bugs with optional filters."""
        try:
            query = select(Bug).order_by(Bug.found_at.desc())

            if project_id:
                query = query.where(Bug.project_id == project_id)
            if status:
                query = query.where(Bug.status == status)
            if severity:
                query = query.where(Bug.severity == severity)

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to list bugs", error=str(e))
            return []

    async def get_bug(self, bug_id: str, db: AsyncSession = None) -> Bug | None:
        """Get a specific bug."""
        try:
            result = await db.execute(select(Bug).where(Bug.id == bug_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Failed to get bug", bug_id=bug_id, error=str(e))
            return None

    async def create_bug(
        self,
        project_id: str,
        title: str,
        description: str,
        severity: str,
        file_path: str = None,
        line_number: int = None,
        test_run_id: str = None,
        db: AsyncSession = None,
    ) -> Bug:
        """Create a new bug."""
        bug = Bug(
            id=f"bug-{uuid4().hex[:12]}",
            project_id=project_id,
            test_run_id=test_run_id,
            title=title,
            description=description,
            severity=severity,
            status="open",
            file_path=file_path,
            line_number=line_number,
        )

        db.add(bug)
        await db.commit()
        await db.refresh(bug)

        logger.info("Bug created", bug_id=bug.id, severity=severity)
        return bug

    async def get_coverage_data(self, project_id: str, db: AsyncSession = None) -> list[CodeCoverage]:
        """Get code coverage data for a project."""
        try:
            result = await db.execute(
                select(CodeCoverage)
                .where(CodeCoverage.project_id == project_id)
                .order_by(CodeCoverage.measured_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to get coverage data", project_id=project_id, error=str(e))
            return []

    async def get_test_files(self, project_id: str, db: AsyncSession = None) -> list[dict]:
        """Get list of test files with their status."""
        try:
            # Get latest test run for project
            result = await db.execute(
                select(TestRun).where(TestRun.project_id == project_id).order_by(TestRun.started_at.desc()).limit(1)
            )
            test_run = result.scalar_one_or_none()

            if not test_run:
                return []

            # Get test cases grouped by file
            result = await db.execute(
                select(
                    TestCase.file_path,
                    func.count(TestCase.id).label("total"),
                    func.sum(func.case((TestCase.status == "passed", 1), else_=0)).label("passed"),
                    func.sum(func.case((TestCase.status == "failed", 1), else_=0)).label("failed"),
                )
                .where(TestCase.test_run_id == test_run.id)
                .group_by(TestCase.file_path)
            )

            files = []
            for row in result:
                files.append(
                    {
                        "file_path": row.file_path,
                        "total": row.total,
                        "passed": row.passed,
                        "failed": row.failed,
                        "status": "passed" if row.failed == 0 else "failed",
                    }
                )

            return files
        except Exception as e:
            logger.error("Failed to get test files", project_id=project_id, error=str(e))
            return []


# Singleton instance
testing_service = TestingService()
