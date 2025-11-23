"""
Thread-safe utilities for background operations
"""
import threading
import queue
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass
from enum import Enum

try:
    from utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class TaskStatus(Enum):
    """Status of background tasks"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """Result of a background task"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[Exception] = None
    error_message: Optional[str] = None


class ThreadSafeQueue:
    """
    Thread-safe queue for managing background tasks

    Provides safe communication between GUI thread and worker threads
    """

    def __init__(self, max_size: int = 0):
        """
        Initialize thread-safe queue

        Args:
            max_size: Maximum queue size (0 = unlimited)
        """
        self.queue = queue.Queue(maxsize=max_size)
        self.results: Dict[str, TaskResult] = {}
        self.lock = threading.Lock()
        logger.info(f"ThreadSafeQueue initialized with max_size={max_size}")

    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None):
        """
        Put an item in the queue

        Args:
            item: Item to add to queue
            block: Whether to block if queue is full
            timeout: Timeout in seconds (None = wait forever)

        Raises:
            queue.Full: If queue is full and block=False
        """
        try:
            self.queue.put(item, block=block, timeout=timeout)
            logger.debug(f"Item added to queue: {type(item).__name__}")
        except queue.Full:
            logger.error("Queue is full, cannot add item")
            raise

    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        """
        Get an item from the queue

        Args:
            block: Whether to block if queue is empty
            timeout: Timeout in seconds (None = wait forever)

        Returns:
            Item from queue

        Raises:
            queue.Empty: If queue is empty and block=False
        """
        try:
            item = self.queue.get(block=block, timeout=timeout)
            logger.debug(f"Item retrieved from queue: {type(item).__name__}")
            return item
        except queue.Empty:
            logger.debug("Queue is empty")
            raise

    def task_done(self):
        """Mark a task as done"""
        self.queue.task_done()

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty()

    def size(self) -> int:
        """Get approximate queue size"""
        return self.queue.qsize()

    def store_result(self, task_id: str, result: TaskResult):
        """
        Store task result in thread-safe manner

        Args:
            task_id: Unique task identifier
            result: Task result
        """
        with self.lock:
            self.results[task_id] = result
            logger.debug(f"Result stored for task {task_id}: {result.status.value}")

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """
        Get task result in thread-safe manner

        Args:
            task_id: Task identifier

        Returns:
            Task result or None if not found
        """
        with self.lock:
            return self.results.get(task_id)

    def clear_results(self):
        """Clear all stored results"""
        with self.lock:
            count = len(self.results)
            self.results.clear()
            logger.info(f"Cleared {count} task results")


class BackgroundTaskManager:
    """
    Manager for running background tasks safely

    Ensures proper thread management and result handling
    """

    def __init__(self):
        self.task_queue = ThreadSafeQueue()
        self.active_tasks: Dict[str, threading.Thread] = {}
        self.lock = threading.Lock()
        self._task_counter = 0
        logger.info("BackgroundTaskManager initialized")

    def submit_task(
        self,
        task_func: Callable,
        task_id: Optional[str] = None,
        callback: Optional[Callable[[TaskResult], None]] = None,
        *args,
        **kwargs
    ) -> str:
        """
        Submit a task for background execution

        Args:
            task_func: Function to execute in background
            task_id: Optional task identifier (auto-generated if not provided)
            callback: Optional callback function to call with result
            *args: Positional arguments for task_func
            **kwargs: Keyword arguments for task_func

        Returns:
            Task ID
        """
        # Generate task ID if not provided
        if task_id is None:
            with self.lock:
                self._task_counter += 1
                task_id = f"task_{self._task_counter}"

        logger.info(f"Submitting task {task_id}: {task_func.__name__}")

        def wrapped_task():
            """Wrapper that handles execution and result storage"""
            result = TaskResult(
                task_id=task_id,
                status=TaskStatus.RUNNING
            )

            try:
                logger.debug(f"Task {task_id} started")
                result.result = task_func(*args, **kwargs)
                result.status = TaskStatus.COMPLETED
                logger.info(f"Task {task_id} completed successfully")

            except Exception as e:
                result.status = TaskStatus.FAILED
                result.error = e
                result.error_message = str(e)
                logger.exception(f"Task {task_id} failed: {e}")

            finally:
                # Store result
                self.task_queue.store_result(task_id, result)

                # Call callback if provided
                if callback:
                    try:
                        callback(result)
                    except Exception as e:
                        logger.exception(f"Callback failed for task {task_id}: {e}")

                # Clean up active task reference
                with self.lock:
                    if task_id in self.active_tasks:
                        del self.active_tasks[task_id]

        # Create and start thread
        thread = threading.Thread(
            target=wrapped_task,
            name=f"BgTask-{task_id}",
            daemon=True
        )

        with self.lock:
            self.active_tasks[task_id] = thread

        thread.start()
        logger.debug(f"Task {task_id} thread started")

        return task_id

    def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """
        Get result of a task, optionally waiting for completion

        Args:
            task_id: Task identifier
            timeout: Maximum time to wait in seconds (None = don't wait)

        Returns:
            Task result or None if not available
        """
        if timeout is not None:
            # Wait for task to complete
            with self.lock:
                thread = self.active_tasks.get(task_id)

            if thread and thread.is_alive():
                logger.debug(f"Waiting up to {timeout}s for task {task_id}")
                thread.join(timeout=timeout)

        return self.task_queue.get_result(task_id)

    def is_task_running(self, task_id: str) -> bool:
        """
        Check if a task is currently running

        Args:
            task_id: Task identifier

        Returns:
            True if task is running
        """
        with self.lock:
            thread = self.active_tasks.get(task_id)
            return thread is not None and thread.is_alive()

    def get_active_task_count(self) -> int:
        """Get number of currently active tasks"""
        with self.lock:
            # Clean up dead threads
            dead_tasks = [
                tid for tid, thread in self.active_tasks.items()
                if not thread.is_alive()
            ]
            for tid in dead_tasks:
                del self.active_tasks[tid]

            return len(self.active_tasks)

    def cancel_all_tasks(self):
        """
        Request cancellation of all tasks

        Note: This doesn't forcefully stop threads, just marks them for cleanup
        """
        with self.lock:
            count = len(self.active_tasks)
            self.active_tasks.clear()
            logger.info(f"Cancelled {count} tasks")


# Global instance for convenience
_global_task_manager: Optional[BackgroundTaskManager] = None


def get_task_manager() -> BackgroundTaskManager:
    """Get or create global task manager instance"""
    global _global_task_manager
    if _global_task_manager is None:
        _global_task_manager = BackgroundTaskManager()
    return _global_task_manager
