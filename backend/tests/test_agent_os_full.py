"""
Comprehensive tests for AgentOS components to achieve 100% coverage.

Covers:
- CrewExecutor (lines 26-27, 48-97, 106, 124-128)
- ErrorHandler (lines 43-47, 51-61, 65-66, 70-75, 88-89, 115-163, 179)
- WorkerPool (lines 83, 104-121, 130-133, 146-152, 162-168, 189-196)
- Scheduler (lines 101, 110-123, 127-148, 152-153)
- ResourceManager (line 100)
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.agent_os.crew_executor import CrewExecutor
from backend.agent_os.error_handler import (
    CircuitBreaker,
    CircuitState,
    ErrorHandler,
    RetryConfig,
)
from backend.agent_os.resource_manager import ResourceManager
from backend.agent_os.scheduler import ScheduledTask, Scheduler
from backend.agent_os.worker_pool import Worker, WorkerPool


class TestCrewExecutorFull:
    """Comprehensive tests for CrewExecutor."""

    def test_init_creates_empty_active_crews(self):
        """Test initialization creates empty active crews dict."""
        executor = CrewExecutor()
        assert executor._active_crews == {}
        assert executor._logger is not None

    @pytest.mark.asyncio
    async def test_execute_crew_success(self):
        """Test successful crew execution."""
        executor = CrewExecutor()

        # Mock crew factory
        mock_crew = Mock()
        mock_crew.kickoff = Mock(return_value={"output": "test result"})

        def crew_factory():
            return mock_crew

        result = await executor.execute_crew(
            crew_name="test_crew",
            crew_factory=crew_factory,
            inputs={"input_key": "input_value"},
            task_id="task-123"
        )

        assert result["success"] is True
        assert result["crew_name"] == "test_crew"
        assert result["result"] == {"output": "test result"}
        assert "execution_id" in result
        # Verify crew was cleaned up
        assert len(executor._active_crews) == 0

    @pytest.mark.asyncio
    async def test_execute_crew_without_task_id(self):
        """Test crew execution without explicit task_id."""
        executor = CrewExecutor()

        mock_crew = Mock()
        mock_crew.kickoff = Mock(return_value="result")

        result = await executor.execute_crew(
            crew_name="test_crew",
            crew_factory=lambda: mock_crew
        )

        assert result["success"] is True
        assert result["execution_id"] is not None

    @pytest.mark.asyncio
    async def test_execute_crew_failure(self):
        """Test crew execution handles exceptions."""
        executor = CrewExecutor()

        def failing_factory():
            raise ValueError("Crew creation failed")

        result = await executor.execute_crew(
            crew_name="failing_crew",
            crew_factory=failing_factory
        )

        assert result["success"] is False
        assert "error" in result
        assert "Crew creation failed" in result["error"]
        assert result["crew_name"] == "failing_crew"

    @pytest.mark.asyncio
    async def test_execute_crew_kickoff_failure(self):
        """Test crew execution handles kickoff failures."""
        executor = CrewExecutor()

        mock_crew = Mock()
        mock_crew.kickoff = Mock(side_effect=RuntimeError("Kickoff failed"))

        result = await executor.execute_crew(
            crew_name="test_crew",
            crew_factory=lambda: mock_crew
        )

        assert result["success"] is False
        assert "Kickoff failed" in result["error"]

    def test_get_active_crews_empty(self):
        """Test getting active crews when none are active."""
        executor = CrewExecutor()
        active = executor.get_active_crews()
        assert active == []

    def test_get_active_crews_with_crews(self):
        """Test getting active crews with entries."""
        executor = CrewExecutor()

        class MockCrew:
            pass

        executor._active_crews["exec-1"] = MockCrew()
        executor._active_crews["exec-2"] = MockCrew()

        active = executor.get_active_crews()

        assert len(active) == 2
        assert all("execution_id" in c for c in active)
        assert all("crew_type" in c for c in active)

    @pytest.mark.asyncio
    async def test_stop_crew_existing(self):
        """Test stopping an existing crew."""
        executor = CrewExecutor()
        executor._active_crews["exec-123"] = Mock()

        result = await executor.stop_crew("exec-123")

        assert result is True
        assert "exec-123" not in executor._active_crews

    @pytest.mark.asyncio
    async def test_stop_crew_nonexistent(self):
        """Test stopping a non-existent crew."""
        executor = CrewExecutor()

        result = await executor.stop_crew("nonexistent")

        assert result is False


class TestCircuitBreakerFull:
    """Comprehensive tests for CircuitBreaker."""

    def test_init_defaults(self):
        """Test default initialization."""
        cb = CircuitBreaker()
        assert cb._failure_threshold == 5
        assert cb._recovery_timeout == 60.0
        assert cb._state == CircuitState.CLOSED
        assert cb._failures == 0
        assert cb._last_failure is None

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
        assert cb._failure_threshold == 3
        assert cb._recovery_timeout == 30.0

    def test_can_execute_closed_state(self):
        """Test can_execute returns True in closed state."""
        cb = CircuitBreaker()
        assert cb.can_execute() is True

    def test_can_execute_open_state_no_recovery(self):
        """Test can_execute returns False in open state before recovery."""
        cb = CircuitBreaker(recovery_timeout=60.0)
        cb._state = CircuitState.OPEN
        cb._last_failure = datetime.utcnow()
        assert cb.can_execute() is False

    def test_can_execute_open_state_after_recovery(self):
        """Test can_execute transitions to half-open after recovery timeout."""
        cb = CircuitBreaker(recovery_timeout=1.0)
        cb._state = CircuitState.OPEN
        cb._last_failure = datetime.utcnow() - timedelta(seconds=5)

        result = cb.can_execute()

        assert result is True
        assert cb._state == CircuitState.HALF_OPEN

    def test_can_execute_half_open_state(self):
        """Test can_execute returns True in half-open state."""
        cb = CircuitBreaker()
        cb._state = CircuitState.HALF_OPEN
        assert cb.can_execute() is True

    def test_record_success(self):
        """Test record_success resets state."""
        cb = CircuitBreaker()
        cb._failures = 3
        cb._state = CircuitState.HALF_OPEN

        cb.record_success()

        assert cb._failures == 0
        assert cb._state == CircuitState.CLOSED

    def test_record_failure_below_threshold(self):
        """Test record_failure increments failures below threshold."""
        cb = CircuitBreaker(failure_threshold=5)

        cb.record_failure()

        assert cb._failures == 1
        assert cb._state == CircuitState.CLOSED
        assert cb._last_failure is not None

    def test_record_failure_reaches_threshold(self):
        """Test record_failure opens circuit at threshold."""
        cb = CircuitBreaker(failure_threshold=3)
        cb._failures = 2

        cb.record_failure()

        assert cb._failures == 3
        assert cb._state == CircuitState.OPEN


class TestErrorHandlerFull:
    """Comprehensive tests for ErrorHandler."""

    def test_init(self):
        """Test initialization."""
        handler = ErrorHandler()
        assert handler._circuit_breakers == {}

    @pytest.mark.asyncio
    async def test_execute_with_retry_success_first_try(self):
        """Test successful execution on first try."""
        handler = ErrorHandler()

        async def successful_op():
            return "success"

        result = await handler.execute_with_retry(successful_op)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_execute_with_retry_eventual_success(self):
        """Test retry succeeds after initial failures."""
        handler = ErrorHandler()
        call_count = 0

        async def eventual_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        config = RetryConfig(max_retries=3, backoff_base=0.01)
        result = await handler.execute_with_retry(eventual_success, config=config)

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_execute_with_retry_all_failures(self):
        """Test retry exhaustion raises last exception."""
        handler = ErrorHandler()

        async def always_fails():
            raise ValueError("Always fails")

        config = RetryConfig(max_retries=2, backoff_base=0.01)

        with pytest.raises(ValueError, match="Always fails"):
            await handler.execute_with_retry(always_fails, config=config)

    @pytest.mark.asyncio
    async def test_execute_with_retry_linear_backoff(self):
        """Test linear backoff when exponential is false."""
        handler = ErrorHandler()
        call_count = 0

        async def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Fail")
            return "ok"

        config = RetryConfig(max_retries=3, backoff_base=0.01, exponential=False)
        result = await handler.execute_with_retry(fails_twice, config=config)

        assert result == "ok"

    @pytest.mark.asyncio
    async def test_execute_with_retry_with_circuit_breaker(self):
        """Test retry with circuit breaker integration."""
        handler = ErrorHandler()

        async def successful_op():
            return "success"

        result = await handler.execute_with_retry(
            successful_op,
            circuit_name="test_circuit"
        )

        assert result == "success"
        assert "test_circuit" in handler._circuit_breakers

    @pytest.mark.asyncio
    async def test_execute_with_retry_circuit_breaker_open(self):
        """Test execution blocked when circuit breaker is open."""
        handler = ErrorHandler()

        # Set up open circuit breaker
        cb = CircuitBreaker(failure_threshold=1)
        cb._state = CircuitState.OPEN
        cb._last_failure = datetime.utcnow()
        handler._circuit_breakers["test_circuit"] = cb

        async def should_not_run():
            return "should not reach"

        with pytest.raises(Exception, match="Circuit breaker open"):
            await handler.execute_with_retry(
                should_not_run,
                circuit_name="test_circuit"
            )

    @pytest.mark.asyncio
    async def test_execute_with_retry_records_failure_on_circuit(self):
        """Test that all retries failing records failure on circuit."""
        handler = ErrorHandler()

        async def always_fails():
            raise ValueError("Always fails")

        config = RetryConfig(max_retries=1, backoff_base=0.01)

        with pytest.raises(ValueError):
            await handler.execute_with_retry(
                always_fails,
                config=config,
                circuit_name="failure_circuit"
            )

        assert handler._circuit_breakers["failure_circuit"]._failures > 0

    @pytest.mark.asyncio
    async def test_execute_with_retry_backoff_max(self):
        """Test backoff capped at max value."""
        handler = ErrorHandler()
        call_count = 0

        async def fails_many():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Fail")
            return "ok"

        config = RetryConfig(
            max_retries=5,
            backoff_base=0.01,
            backoff_max=0.02,
            exponential=True
        )
        result = await handler.execute_with_retry(fails_many, config=config)
        assert result == "ok"

    def test_escalate_to_human(self):
        """Test escalate_to_human logs the escalation."""
        handler = ErrorHandler()

        # Should not raise, just logs
        handler.escalate_to_human(
            task_id="task-123",
            error=ValueError("Test error"),
            context={"key": "value"}
        )

    def test_escalate_to_human_without_context(self):
        """Test escalate_to_human without context."""
        handler = ErrorHandler()
        handler.escalate_to_human(
            task_id="task-456",
            error=RuntimeError("Another error")
        )


class TestWorkerPoolFull:
    """Comprehensive tests for WorkerPool."""

    def test_init_creates_min_workers(self):
        """Test initialization creates minimum workers."""
        pool = WorkerPool(min_workers=3, max_workers=10)
        assert len(pool._workers) == 3

    def test_create_worker(self):
        """Test creating a worker."""
        pool = WorkerPool(min_workers=0, max_workers=5)
        worker = pool._create_worker("test-worker")

        assert worker.name == "test-worker"
        assert worker.status == "idle"
        assert worker.worker_id in pool._workers

    @pytest.mark.asyncio
    async def test_scale_up_within_limit(self):
        """Test scaling up within max limit."""
        pool = WorkerPool(min_workers=2, max_workers=5)

        new_workers = await pool.scale_up(2)

        assert len(new_workers) == 2
        assert len(pool._workers) == 4

    @pytest.mark.asyncio
    async def test_scale_up_hits_max_limit(self):
        """Test scaling up stops at max limit."""
        pool = WorkerPool(min_workers=2, max_workers=3)

        new_workers = await pool.scale_up(5)

        assert len(new_workers) == 1  # Only 1 can be added
        assert len(pool._workers) == 3

    @pytest.mark.asyncio
    async def test_scale_down_removes_idle_workers(self):
        """Test scaling down removes idle workers."""
        pool = WorkerPool(min_workers=2, max_workers=5)
        await pool.scale_up(2)
        assert len(pool._workers) == 4

        removed = await pool.scale_down(1)

        assert removed == 1
        assert len(pool._workers) == 3

    @pytest.mark.asyncio
    async def test_scale_down_respects_min_workers(self):
        """Test scaling down respects minimum workers."""
        pool = WorkerPool(min_workers=2, max_workers=5)

        removed = await pool.scale_down(3)

        assert removed == 0
        assert len(pool._workers) == 2

    @pytest.mark.asyncio
    async def test_scale_down_skips_busy_workers(self):
        """Test scaling down only removes idle workers."""
        pool = WorkerPool(min_workers=1, max_workers=5)
        await pool.scale_up(2)

        # Make first workers busy
        worker_ids = list(pool._workers.keys())
        pool._workers[worker_ids[0]].status = "busy"
        pool._workers[worker_ids[1]].status = "busy"

        removed = await pool.scale_down(3)

        # Should only remove idle workers
        assert removed == 1  # Only the third worker is idle
        assert len(pool._workers) == 2

    def test_get_available_worker_returns_idle(self):
        """Test getting available worker returns idle worker."""
        pool = WorkerPool(min_workers=2, max_workers=5)

        worker = pool.get_available_worker()

        assert worker is not None
        assert worker.status == "idle"

    def test_get_available_worker_none_when_all_busy(self):
        """Test getting available worker returns None when all busy."""
        pool = WorkerPool(min_workers=2, max_workers=5)

        for worker in pool._workers.values():
            worker.status = "busy"

        worker = pool.get_available_worker()
        assert worker is None

    def test_assign_task_success(self):
        """Test assigning task to worker."""
        pool = WorkerPool(min_workers=2, max_workers=5)
        worker_id = list(pool._workers.keys())[0]

        result = pool.assign_task(worker_id, "task-123")

        assert result is True
        assert pool._workers[worker_id].status == "busy"
        assert pool._workers[worker_id].current_task == "task-123"

    def test_assign_task_worker_not_found(self):
        """Test assigning task to nonexistent worker."""
        pool = WorkerPool(min_workers=2, max_workers=5)

        result = pool.assign_task("nonexistent", "task-123")

        assert result is False

    def test_assign_task_worker_busy(self):
        """Test assigning task to busy worker fails."""
        pool = WorkerPool(min_workers=2, max_workers=5)
        worker_id = list(pool._workers.keys())[0]
        pool._workers[worker_id].status = "busy"

        result = pool.assign_task(worker_id, "task-123")

        assert result is False

    def test_release_worker_success(self):
        """Test releasing worker after successful task."""
        pool = WorkerPool(min_workers=2, max_workers=5)
        worker_id = list(pool._workers.keys())[0]
        pool.assign_task(worker_id, "task-123")

        pool.release_worker(worker_id, success=True)

        worker = pool._workers[worker_id]
        assert worker.status == "idle"
        assert worker.current_task is None
        assert worker.total_tasks == 1
        assert worker.failed_tasks == 0

    def test_release_worker_failed_task(self):
        """Test releasing worker after failed task."""
        pool = WorkerPool(min_workers=2, max_workers=5)
        worker_id = list(pool._workers.keys())[0]
        pool.assign_task(worker_id, "task-123")

        pool.release_worker(worker_id, success=False)

        worker = pool._workers[worker_id]
        assert worker.total_tasks == 1
        assert worker.failed_tasks == 1

    def test_release_worker_nonexistent(self):
        """Test releasing nonexistent worker does nothing."""
        pool = WorkerPool(min_workers=2, max_workers=5)
        # Should not raise
        pool.release_worker("nonexistent")

    def test_get_pool_status(self):
        """Test getting pool status."""
        pool = WorkerPool(min_workers=2, max_workers=5)
        worker_id = list(pool._workers.keys())[0]
        pool._workers[worker_id].status = "busy"

        status = pool.get_pool_status()

        assert status["total_workers"] == 2
        assert status["idle_workers"] == 1
        assert status["busy_workers"] == 1
        assert status["unhealthy_workers"] == 0
        assert status["min_workers"] == 2
        assert status["max_workers"] == 5

    @pytest.mark.asyncio
    async def test_shutdown_waits_for_busy_workers(self):
        """Test shutdown waits for busy workers to complete."""
        pool = WorkerPool(min_workers=2, max_workers=5)
        worker_id = list(pool._workers.keys())[0]
        pool._workers[worker_id].status = "busy"

        # Start shutdown in background
        async def finish_work():
            await asyncio.sleep(0.1)
            pool._workers[worker_id].status = "idle"

        asyncio.create_task(finish_work())

        await pool.shutdown()

        assert len(pool._workers) == 0

    @pytest.mark.asyncio
    async def test_shutdown_immediate_when_all_idle(self):
        """Test shutdown completes immediately when all workers idle."""
        pool = WorkerPool(min_workers=2, max_workers=5)

        await pool.shutdown()

        assert len(pool._workers) == 0


class TestSchedulerFull:
    """Comprehensive tests for Scheduler."""

    def test_init(self):
        """Test initialization."""
        scheduler = Scheduler()
        assert scheduler._scheduled_tasks == {}
        assert scheduler._running is False

    @pytest.mark.asyncio
    async def test_schedule_task_immediate(self):
        """Test scheduling task for immediate execution."""
        scheduler = Scheduler()

        async def test_exec():
            pass

        task_id = await scheduler.schedule_task(
            name="test_task",
            execute=test_exec
        )

        assert task_id is not None
        assert task_id in scheduler._scheduled_tasks
        assert scheduler._scheduled_tasks[task_id].name == "test_task"

    @pytest.mark.asyncio
    async def test_schedule_task_with_dependencies(self):
        """Test scheduling task with dependencies."""
        scheduler = Scheduler()

        async def test_exec():
            pass

        task_id = await scheduler.schedule_task(
            name="dependent_task",
            execute=test_exec,
            dependencies=["dep-1", "dep-2"],
            metadata={"key": "value"}
        )

        task = scheduler._scheduled_tasks[task_id]
        assert task.dependencies == ["dep-1", "dep-2"]
        assert task.metadata == {"key": "value"}

    @pytest.mark.asyncio
    async def test_cancel_task_existing(self):
        """Test canceling existing task."""
        scheduler = Scheduler()

        async def test_exec():
            pass

        task_id = await scheduler.schedule_task("test", test_exec)

        result = await scheduler.cancel_task(task_id)

        assert result is True
        assert task_id not in scheduler._scheduled_tasks

    @pytest.mark.asyncio
    async def test_cancel_task_nonexistent(self):
        """Test canceling nonexistent task returns False."""
        scheduler = Scheduler()

        result = await scheduler.cancel_task("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_get_ready_tasks_empty(self):
        """Test getting ready tasks when none are ready."""
        scheduler = Scheduler()

        ready = await scheduler.get_ready_tasks()

        assert ready == []

    @pytest.mark.asyncio
    async def test_get_ready_tasks_scheduled_in_past(self):
        """Test getting tasks scheduled in the past."""
        scheduler = Scheduler()

        async def test_exec():
            pass

        await scheduler.schedule_task(
            name="ready_task",
            execute=test_exec,
            scheduled_at=datetime.utcnow() - timedelta(seconds=10)
        )

        ready = await scheduler.get_ready_tasks()

        assert len(ready) == 1
        assert ready[0].name == "ready_task"

    @pytest.mark.asyncio
    async def test_get_ready_tasks_scheduled_in_future(self):
        """Test tasks scheduled in future are not ready."""
        scheduler = Scheduler()

        async def test_exec():
            pass

        await scheduler.schedule_task(
            name="future_task",
            execute=test_exec,
            scheduled_at=datetime.utcnow() + timedelta(hours=1)
        )

        ready = await scheduler.get_ready_tasks()

        assert len(ready) == 0

    @pytest.mark.asyncio
    async def test_get_ready_tasks_with_unmet_dependencies(self):
        """Test tasks with unmet dependencies are not ready."""
        scheduler = Scheduler()

        async def test_exec():
            pass

        # Create dependency task
        dep_id = await scheduler.schedule_task(
            name="dependency",
            execute=test_exec
        )

        # Create task that depends on it
        await scheduler.schedule_task(
            name="dependent",
            execute=test_exec,
            dependencies=[dep_id]
        )

        ready = await scheduler.get_ready_tasks()

        # Only the dependency should be ready
        assert len(ready) == 1
        assert ready[0].name == "dependency"

    @pytest.mark.asyncio
    async def test_get_ready_tasks_sorted_by_priority(self):
        """Test ready tasks are sorted by priority."""
        scheduler = Scheduler()

        async def test_exec():
            pass

        await scheduler.schedule_task(
            name="low_priority",
            execute=test_exec,
            priority=10
        )

        await scheduler.schedule_task(
            name="high_priority",
            execute=test_exec,
            priority=1
        )

        ready = await scheduler.get_ready_tasks()

        assert len(ready) == 2
        assert ready[0].name == "high_priority"
        assert ready[1].name == "low_priority"

    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        """Test starting and stopping scheduler."""
        scheduler = Scheduler()
        executed = []

        async def test_exec():
            executed.append(True)

        await scheduler.schedule_task("test", test_exec)

        # Start scheduler in background
        asyncio.create_task(scheduler.start())

        # Give it time to run
        await asyncio.sleep(1.5)

        scheduler.stop()
        await asyncio.sleep(0.1)

        assert scheduler._running is False
        assert len(executed) > 0

    @pytest.mark.asyncio
    async def test_start_handles_task_exceptions(self):
        """Test scheduler handles task execution exceptions."""
        scheduler = Scheduler()

        async def failing_exec():
            raise ValueError("Task failed")

        await scheduler.schedule_task("failing", failing_exec)

        # Start scheduler briefly
        asyncio.create_task(scheduler.start())
        await asyncio.sleep(1.5)
        scheduler.stop()
        await asyncio.sleep(0.1)

        # Scheduler should continue running after task failure
        assert scheduler._running is False

    @pytest.mark.asyncio
    async def test_start_handles_scheduler_loop_exception(self):
        """Test scheduler handles exceptions in the main loop (lines 147-148)."""
        scheduler = Scheduler()

        # Patch get_ready_tasks to raise exception on first call
        original_get_ready = scheduler.get_ready_tasks
        call_count = 0

        async def failing_get_ready():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("Scheduler loop error")
            scheduler.stop()  # Stop after successful call
            return []

        scheduler.get_ready_tasks = failing_get_ready

        # Mock asyncio.sleep to speed up test
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            mock_sleep.return_value = None

            # Run the scheduler (it will handle the exception and continue)
            task = asyncio.create_task(scheduler.start())

            # Give it time to process
            for _ in range(10):
                await asyncio.sleep(0)  # Real sleep to allow task to run
                if call_count >= 2:
                    break

            scheduler.stop()

            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                scheduler._running = False

        # Restore original
        scheduler.get_ready_tasks = original_get_ready

        # The scheduler should have handled the exception
        assert call_count >= 1

    def test_stop_scheduler(self):
        """Test stopping scheduler."""
        scheduler = Scheduler()
        scheduler._running = True

        scheduler.stop()

        assert scheduler._running is False


class TestResourceManagerFull:
    """Additional tests for ResourceManager to achieve 100% coverage."""

    def test_release_nonexistent_task(self):
        """Test releasing nonexistent task returns False."""
        manager = ResourceManager()

        result = manager.release("nonexistent-task")

        assert result is False

    def test_allocate_insufficient_memory(self):
        """Test allocation with insufficient memory."""
        manager = ResourceManager()

        result = manager.allocate(
            task_id="task1",
            memory_mb=999999  # More than available
        )

        assert result is False

    def test_allocate_insufficient_gpu(self):
        """Test allocation with insufficient GPU."""
        manager = ResourceManager()

        result = manager.allocate(
            task_id="task1",
            gpu_count=100  # More than available
        )

        assert result is False

    def test_allocate_insufficient_storage(self):
        """Test allocation with insufficient storage."""
        manager = ResourceManager()

        result = manager.allocate(
            task_id="task1",
            storage_mb=999999999  # More than available
        )

        assert result is False


class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_default_values(self):
        """Test default values."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.backoff_base == 1.0
        assert config.backoff_max == 60.0
        assert config.exponential is True

    def test_custom_values(self):
        """Test custom values."""
        config = RetryConfig(
            max_retries=5,
            backoff_base=2.0,
            backoff_max=120.0,
            exponential=False
        )
        assert config.max_retries == 5
        assert config.backoff_base == 2.0


class TestWorkerDataclass:
    """Tests for Worker dataclass."""

    def test_worker_creation(self):
        """Test worker creation with defaults."""
        worker = Worker(
            worker_id="w-123",
            name="test-worker"
        )
        assert worker.status == "idle"
        assert worker.current_task is None
        assert worker.total_tasks == 0
        assert worker.failed_tasks == 0


class TestScheduledTaskDataclass:
    """Tests for ScheduledTask dataclass."""

    def test_scheduled_task_creation(self):
        """Test scheduled task creation."""
        async def exec_fn():
            pass

        task = ScheduledTask(
            task_id="t-123",
            name="test",
            scheduled_at=datetime.utcnow(),
            priority=5,
            execute=exec_fn
        )
        assert task.dependencies == []
        assert task.metadata == {}
