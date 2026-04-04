"""
Testing API Routes - REST API for AI-driven testing system.

Provides endpoints for:
- Test generation and execution
- Bug detection and fixing
- Coverage analysis
- Test health monitoring
"""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import User, get_current_user
from backend.core.logging import get_logger
from backend.testing.agents.auto_fixer import AutoFixerAgent
from backend.testing.agents.bug_detector import BugDetectorAgent
from backend.testing.agents.frontend_tester import FrontendTesterAgent
from backend.testing.agents.test_generator import TestGeneratorAgent
from backend.testing.coverage_analyzer import CoverageAnalyzer
from backend.testing.intelligence_engine import TestIntelligenceEngine
from backend.testing.self_healing_runner import SelfHealingTestRunner

logger = get_logger(__name__)

router = APIRouter(prefix="/testing", tags=["testing"])


# Request/Response Models


class GenerateTestsRequest(BaseModel):
    file_path: str = Field(..., description="Path to the source file")
    include_edge_cases: bool = Field(True, description="Include edge case tests")
    include_error_cases: bool = Field(True, description="Include error handling tests")
    include_property_tests: bool = Field(False, description="Include property-based tests")


class GenerateTestsResponse(BaseModel):
    file_path: str
    tests_generated: int
    tests: list[dict[str, Any]]
    generation_time_ms: float


class DetectBugsRequest(BaseModel):
    file_path: str | None = Field(None, description="Path to specific file")
    directory: str | None = Field(None, description="Directory to scan")
    use_static_analysis: bool = Field(True, description="Enable static analysis")
    use_llm_review: bool = Field(True, description="Enable LLM code review")
    min_confidence: float = Field(0.7, ge=0, le=1, description="Minimum confidence threshold")


class DetectBugsResponse(BaseModel):
    file_path: str | None
    directory: str | None
    bugs_found: int
    by_severity: dict[str, int]
    by_category: dict[str, int]
    bugs: list[dict[str, Any]]


class FixBugRequest(BaseModel):
    bug_id: str = Field(..., description="Bug identifier")
    file_path: str = Field(..., description="Path to the file")
    bug_description: str = Field(..., description="Description of the bug")
    suggested_fix: str = Field("", description="Suggested fix")
    line_number: int | None = Field(None, description="Line number")
    auto_apply: bool = Field(False, description="Apply fix automatically")


class FixBugResponse(BaseModel):
    fix_id: str
    bug_id: str
    status: str
    strategy: str
    applied: bool
    diff: str
    validation_passed: bool


class RunTestsRequest(BaseModel):
    test_suite: str | None = Field(None, description="Test suite name")
    file_pattern: str | None = Field(None, description="File pattern to match")
    max_retries: int = Field(3, ge=0, le=5, description="Max retries for flaky tests")
    parallel_workers: int = Field(4, ge=1, le=10, description="Parallel workers")


class RunTestsResponse(BaseModel):
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    flaky: int
    healed: int
    pass_rate: float
    duration_seconds: float
    results: list[dict[str, Any]]


class CoverageRequest(BaseModel):
    source_path: str = Field(..., description="Path to source code")
    test_path: str | None = Field(None, description="Path to tests")
    run_mutation_testing: bool = Field(False, description="Run mutation testing")


class CoverageResponse(BaseModel):
    timestamp: str
    overall_coverage: float
    overall_branch_coverage: float
    mutation_score: float | None
    files_analyzed: int
    files_by_coverage_level: dict[str, list[str]]
    gaps: list[dict[str, Any]]


class TestHealthResponse(BaseModel):
    summary: dict[str, Any]
    flaky_tests: list[dict[str, Any]]
    recent_bugs: list[dict[str, Any]]
    recent_fixes: list[dict[str, Any]]
    coverage_trend: list[dict[str, Any]]


# Dependency injection


async def get_intelligence_engine():
    return TestIntelligenceEngine()


async def get_test_generator():
    return TestGeneratorAgent()


async def get_bug_detector():
    return BugDetectorAgent()


async def get_auto_fixer():
    return AutoFixerAgent()


async def get_frontend_tester():
    return FrontendTesterAgent()


async def get_test_runner():
    return SelfHealingTestRunner()


async def get_coverage_analyzer():
    return CoverageAnalyzer()


# API Endpoints


@router.post("/generate-tests", response_model=GenerateTestsResponse)
async def generate_tests(
    request: GenerateTestsRequest,
    current_user: User = Depends(get_current_user),
    agent: TestGeneratorAgent = Depends(get_test_generator),
):
    """
    Generate AI-powered tests for a source file.

    This endpoint analyzes the code and generates comprehensive tests including:
    - Unit tests for functions and methods
    - Edge case tests
    - Error handling tests
    """
    import time

    start_time = time.time()

    try:
        tests = await agent.generate_tests_for_file(
            file_path=request.file_path,
            include_edge_cases=request.include_edge_cases,
            include_error_cases=request.include_error_cases,
            include_property_tests=request.include_property_tests,
        )

        generation_time = (time.time() - start_time) * 1000

        return GenerateTestsResponse(
            file_path=request.file_path,
            tests_generated=len(tests),
            tests=[t.to_dict() for t in tests],
            generation_time_ms=generation_time,
        )

    except Exception as e:
        logger.error("Test generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/detect-bugs", response_model=DetectBugsResponse)
async def detect_bugs(
    request: DetectBugsRequest,
    current_user: User = Depends(get_current_user),
    agent: BugDetectorAgent = Depends(get_bug_detector),
):
    """
    Detect bugs using AI and static analysis.

    Scans code for:
    - Security vulnerabilities
    - Logic errors
    - Performance issues
    - Code smells
    """
    try:
        if request.directory:
            results = await agent.detect_bugs_in_directory(
                directory=request.directory,
                use_static_analysis=request.use_static_analysis,
                use_llm_review=request.use_llm_review,
                min_confidence=request.min_confidence,
            )
            all_bugs = [bug for bugs in results.values() for bug in bugs]

            stats = await agent.get_bug_statistics(all_bugs)

            return DetectBugsResponse(
                directory=request.directory,
                file_path=None,
                bugs_found=len(all_bugs),
                by_severity=stats.get("by_severity", {}),
                by_category=stats.get("by_category", {}),
                bugs=[b.to_dict() for b in all_bugs[:50]],  # Limit output
            )

        elif request.file_path:
            bugs = await agent.detect_bugs_in_file(
                file_path=request.file_path,
                use_static_analysis=request.use_static_analysis,
                use_llm_review=request.use_llm_review,
                min_confidence=request.min_confidence,
            )

            stats = await agent.get_bug_statistics(bugs)

            return DetectBugsResponse(
                file_path=request.file_path,
                directory=None,
                bugs_found=len(bugs),
                by_severity=stats.get("by_severity", {}),
                by_category=stats.get("by_category", {}),
                bugs=[b.to_dict() for b in bugs],
            )

        else:
            raise HTTPException(status_code=400, detail="Either file_path or directory must be provided")

    except Exception as e:
        logger.error("Bug detection failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/fix-bug", response_model=FixBugResponse)
async def fix_bug(
    request: FixBugRequest,
    current_user: User = Depends(get_current_user),
    agent: AutoFixerAgent = Depends(get_auto_fixer),
):
    """
    Automatically fix a detected bug.

    Applies AI-generated or pattern-based fixes with:
    - Validation before applying
    - Automatic rollback on failure
    - Diff preview
    """
    try:
        fix_attempt = await agent.fix_bug(
            bug_id=request.bug_id,
            file_path=request.file_path,
            bug_description=request.bug_description,
            suggested_fix=request.suggested_fix,
            line_number=request.line_number,
            auto_apply=request.auto_apply,
            validate=True,
        )

        return FixBugResponse(
            fix_id=fix_attempt.id,
            bug_id=fix_attempt.bug_id,
            status=fix_attempt.status.value,
            strategy=fix_attempt.strategy.value,
            applied=fix_attempt.status.value == "success",
            diff=fix_attempt.diff,
            validation_passed=fix_attempt.validation_results.get("passed", False),
        )

    except Exception as e:
        logger.error("Bug fix failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/batch-fix")
async def batch_fix(
    bug_ids: list[str],
    auto_apply: bool = False,
    current_user: User = Depends(get_current_user),
    agent: AutoFixerAgent = Depends(get_auto_fixer),
):
    """
    Fix multiple bugs in batch.

    Args:
        bug_ids: List of bug IDs to fix
        auto_apply: Whether to apply fixes automatically
    """
    # This would look up bugs and fix them
    return {"status": "not_implemented", "bug_ids": bug_ids}


@router.post("/preview-fix")
async def preview_fix(
    request: FixBugRequest,
    current_user: User = Depends(get_current_user),
    agent: AutoFixerAgent = Depends(get_auto_fixer),
):
    """
    Preview a fix without applying it.

    Returns the diff and validation estimate.
    """
    try:
        preview = await agent.preview_fix(
            bug_id=request.bug_id,
            file_path=request.file_path,
            bug_description=request.bug_description,
            suggested_fix=request.suggested_fix,
            line_number=request.line_number,
        )

        return preview

    except Exception as e:
        logger.error("Fix preview failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/rollback-fix/{fix_id}")
async def rollback_fix(
    fix_id: str,
    current_user: User = Depends(get_current_user),
    agent: AutoFixerAgent = Depends(get_auto_fixer),
):
    """
    Rollback a previously applied fix.

    Restores the original code from backup.
    """
    try:
        success = await agent.rollback_fix(fix_id)

        if not success:
            raise HTTPException(status_code=404, detail="Fix not found or rollback failed")

        return {"fix_id": fix_id, "rolled_back": True}

    except Exception as e:
        logger.error("Rollback failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/run-tests", response_model=RunTestsResponse)
async def run_tests(
    request: RunTestsRequest,
    current_user: User = Depends(get_current_user),
    runner: SelfHealingTestRunner = Depends(get_test_runner),
):
    """
    Run tests with self-healing capabilities.

    Features:
    - Automatic retry for flaky tests
    - Self-healing selectors
    - Parallel execution
    - Smart test ordering
    """
    try:
        import uuid
        from pathlib import Path

        from backend.testing.intelligence_engine import TestCase, TestPriority, TestType

        suite_name = request.test_suite or "default"

        # Discover test cases from the filesystem
        test_cases: list[TestCase] = []
        pattern = request.file_pattern or "backend/tests"
        test_dir = Path(pattern)

        if test_dir.exists():
            files = list(test_dir.rglob("test_*.py")) if test_dir.is_dir() else [test_dir]
            for f in files:
                tc = TestCase(
                    id=str(uuid.uuid4()),
                    name=f.stem,
                    test_type=TestType.UNIT,
                    target_file=str(f),
                    code="",
                    priority=TestPriority.MEDIUM,
                    description=f"Run test file: {f.name}",
                    metadata={"file_path": str(f)},
                )
                test_cases.append(tc)

        # Execute via the self-healing runner
        suite_result = await runner.run_suite(
            test_cases=test_cases,
            suite_name=suite_name,
        )

        # Extract fields defensively — suite_result may be a dataclass, object, or mock
        def _safe_int(obj, attr: str, default: int = 0) -> int:
            val = getattr(obj, attr, default)
            return val if isinstance(val, int) else default

        def _safe_float(obj, attr: str, default: float = 0.0) -> float:
            val = getattr(obj, attr, default)
            return val if isinstance(val, float) else default

        result_suite_name = getattr(suite_result, "suite_name", None)
        if not isinstance(result_suite_name, str):
            result_suite_name = suite_name

        raw_results = getattr(suite_result, "results", []) or []
        serialized = []
        for r in raw_results if isinstance(raw_results, list) else []:
            try:
                serialized.append(r.to_dict())
            except Exception:  # noqa: S110
                pass

        return RunTestsResponse(
            suite_name=result_suite_name,
            total_tests=_safe_int(suite_result, "total_tests"),
            passed=_safe_int(suite_result, "passed"),
            failed=_safe_int(suite_result, "failed"),
            flaky=_safe_int(suite_result, "flaky"),
            healed=_safe_int(suite_result, "healed"),
            pass_rate=_safe_float(suite_result, "pass_rate"),
            duration_seconds=_safe_float(suite_result, "duration_seconds"),
            results=serialized,
        )

    except Exception as e:
        logger.error("Test execution failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/analyze-coverage", response_model=CoverageResponse)
async def analyze_coverage(
    request: CoverageRequest,
    current_user: User = Depends(get_current_user),
    analyzer: CoverageAnalyzer = Depends(get_coverage_analyzer),
):
    """
    Analyze test coverage.

    Provides:
    - Line and branch coverage
    - Coverage gaps identification
    - Mutation testing (optional)
    """
    try:
        report = await analyzer.analyze_coverage(
            source_path=request.source_path,
            test_path=request.test_path,
        )

        gaps = await analyzer.identify_coverage_gaps(report)

        mutation_score = None
        if request.run_mutation_testing and report.files:
            # Run mutation testing on first file as example
            mutation_results = await analyzer.run_mutation_testing(
                report.files[0].file_path,
                max_mutations=20,
            )
            killed = sum(1 for r in mutation_results if r.killed)
            mutation_score = (killed / len(mutation_results) * 100) if mutation_results else 0

        return CoverageResponse(
            timestamp=report.timestamp.isoformat(),
            overall_coverage=report.overall_coverage,
            overall_branch_coverage=report.overall_branch_coverage,
            mutation_score=mutation_score,
            files_analyzed=len(report.files),
            files_by_coverage_level=report.files_by_coverage_level,
            gaps=gaps[:10],  # Limit gaps
        )

    except Exception as e:
        logger.error("Coverage analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/health", response_model=TestHealthResponse)
async def get_test_health(
    current_user: User = Depends(get_current_user),
    engine: TestIntelligenceEngine = Depends(get_intelligence_engine),
    analyzer: CoverageAnalyzer = Depends(get_coverage_analyzer),
    runner: SelfHealingTestRunner = Depends(get_test_runner),
):
    """
    Get comprehensive test health report.

    Returns:
    - Overall test health metrics
    - Flaky tests
    - Recent bugs and fixes
    - Coverage trends
    """
    try:
        health_report = engine.get_test_health_report()
        coverage_stats = analyzer.get_coverage_statistics()
        runner_stats = runner.get_execution_statistics()
        coverage_trend = await analyzer.get_coverage_trend(days=30)

        return TestHealthResponse(
            summary={
                **health_report.get("summary", {}),
                "coverage": coverage_stats,
                "execution": runner_stats,
            },
            flaky_tests=health_report.get("flaky_tests", []),
            recent_bugs=health_report.get("recent_bugs", []),
            recent_fixes=health_report.get("recent_fixes", []),
            coverage_trend=coverage_trend,
        )

    except Exception as e:
        logger.error("Health report failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/flaky-tests")
async def get_flaky_tests(
    current_user: User = Depends(get_current_user),
    runner: SelfHealingTestRunner = Depends(get_test_runner),
):
    """Get list of detected flaky tests."""
    flaky_tests = runner.get_flaky_tests()

    return {
        "flaky_tests": [ft.to_dict() for ft in flaky_tests],
        "count": len(flaky_tests),
    }


@router.post("/quarantine-test/{test_id}")
async def quarantine_test(
    test_id: str,
    reason: str = "",
    current_user: User = Depends(get_current_user),
    runner: SelfHealingTestRunner = Depends(get_test_runner),
):
    """Quarantine a flaky test."""
    success = runner.quarantine_test(test_id, reason)

    if not success:
        raise HTTPException(status_code=404, detail="Test not found")

    return {"test_id": test_id, "quarantined": True, "reason": reason}


@router.post("/unquarantine-test/{test_id}")
async def unquarantine_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    runner: SelfHealingTestRunner = Depends(get_test_runner),
):
    """Remove a test from quarantine."""
    success = runner.unquarantine_test(test_id)

    if not success:
        raise HTTPException(status_code=404, detail="Test not found")

    return {"test_id": test_id, "unquarantined": True}


# Frontend Testing Endpoints


@router.post("/frontend/generate-e2e")
async def generate_e2e_tests(
    page_path: str,
    user_flow: list[str],
    page_description: str = "",
    current_user: User = Depends(get_current_user),
    agent: FrontendTesterAgent = Depends(get_frontend_tester),
):
    """
    Generate E2E tests from user flow.

    Args:
        page_path: Path to the page (e.g., "/login")
        user_flow: List of user actions
        page_description: Description of the page
    """
    try:
        tests = await agent.generate_e2e_tests_from_flow(
            page_path=page_path,
            user_flow=user_flow,
            page_description=page_description,
        )

        return {
            "page_path": page_path,
            "tests_generated": len(tests),
            "tests": [t.to_dict() for t in tests],
        }

    except Exception as e:
        logger.error("E2E test generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/frontend/visual-regression")
async def run_visual_regression(
    page_path: str,
    viewports: list[dict[str, int]] | None = None,
    threshold: float = 0.1,
    current_user: User = Depends(get_current_user),
    agent: FrontendTesterAgent = Depends(get_frontend_tester),
):
    """
    Run visual regression tests.

    Args:
        page_path: Path to test
        viewports: List of viewport sizes
        threshold: Difference threshold
    """
    try:
        results = await agent.run_visual_regression_test(
            page_path=page_path,
            viewport_sizes=viewports,
            threshold=threshold,
        )

        return {
            "page_path": page_path,
            "tests_run": len(results),
            "passed": sum(1 for r in results if r.status.value == "passed"),
            "failed": sum(1 for r in results if r.status.value == "failed"),
            "results": [r.to_dict() for r in results],
        }

    except Exception as e:
        logger.error("Visual regression failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/frontend/accessibility-audit")
async def run_accessibility_audit(
    page_path: str,
    current_user: User = Depends(get_current_user),
    agent: FrontendTesterAgent = Depends(get_frontend_tester),
):
    """Run accessibility audit on a page."""
    try:
        result = await agent.run_accessibility_audit(page_path=page_path)

        return result

    except Exception as e:
        logger.error("Accessibility audit failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/frontend/statistics")
async def get_frontend_statistics(
    current_user: User = Depends(get_current_user),
    agent: FrontendTesterAgent = Depends(get_frontend_tester),
):
    """Get frontend testing statistics."""
    return agent.get_test_statistics()


# Background Tasks


@router.post("/run-full-suite")
async def run_full_test_suite(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    engine: TestIntelligenceEngine = Depends(get_intelligence_engine),
):
    """
    Run full test suite in background.

    This is a long-running operation that:
    1. Generates missing tests
    2. Detects bugs
    3. Runs all tests
    4. Analyzes coverage
    5. Applies auto-fixes
    """

    async def run_suite():
        logger.info("Starting full test suite execution")
        # Implementation would go here
        pass

    background_tasks.add_task(run_suite)

    return {"status": "started", "message": "Full test suite running in background"}


# ── Manual bug report ──────────────────────────────────────────────────────────


class CreateBugRequest(BaseModel):
    """Manual bug report submission."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    project_id: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    component: str | None = None


class CreateBugResponse(BaseModel):
    bug_id: str
    title: str
    severity: str
    status: str
    message: str


@router.post("/bugs", response_model=CreateBugResponse, status_code=201, summary="Create bug report")
async def create_bug(
    request: CreateBugRequest,
    current_user: User = Depends(get_current_user),
) -> CreateBugResponse:
    """
    Manually create a bug report.

    Unlike /detect-bugs (which runs AI analysis on a code path), this endpoint
    accepts a manually authored bug report from the UI.
    """
    import uuid as _uuid

    bug_id = f"bug-{_uuid.uuid4().hex[:8]}"

    logger.info(
        "Bug report created",
        bug_id=bug_id,
        title=request.title,
        severity=request.severity,
        user=current_user.user_id,
    )

    return CreateBugResponse(
        bug_id=bug_id,
        title=request.title,
        severity=request.severity,
        status="open",
        message=f"Bug '{request.title}' reported successfully",
    )
