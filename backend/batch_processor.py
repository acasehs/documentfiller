"""
Batch Processing Module
Handles batch content generation with WebSocket progress updates
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid

class BatchStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BatchTask:
    """Represents a batch processing task"""

    def __init__(
        self,
        task_id: str,
        document_id: str,
        sections: List[Dict[str, Any]],
        operation_mode: str,
        model: str,
        temperature: float,
        max_tokens: int,
        process_empty_only: bool = False,
        client_id: Optional[str] = None
    ):
        self.task_id = task_id
        self.document_id = document_id
        self.sections = sections
        self.operation_mode = operation_mode
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.process_empty_only = process_empty_only
        self.client_id = client_id

        self.status = BatchStatus.PENDING
        self.current_section = 0
        self.total_sections = len(sections)
        self.completed_sections = 0
        self.failed_sections = 0
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.results: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "task_id": self.task_id,
            "document_id": self.document_id,
            "status": self.status.value,
            "current_section": self.current_section,
            "total_sections": self.total_sections,
            "completed_sections": self.completed_sections,
            "failed_sections": self.failed_sections,
            "progress_percentage": (self.completed_sections / self.total_sections * 100) if self.total_sections > 0 else 0,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
        }

class BatchProcessor:
    """Manages batch processing tasks"""

    def __init__(self):
        self.tasks: Dict[str, BatchTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}

    async def create_task(
        self,
        document_id: str,
        sections: List[Dict[str, Any]],
        operation_mode: str,
        model: str,
        temperature: float,
        max_tokens: int,
        process_empty_only: bool = False,
        client_id: Optional[str] = None
    ) -> str:
        """Create a new batch processing task"""
        task_id = str(uuid.uuid4())

        # Filter sections if process_empty_only
        if process_empty_only:
            sections = [s for s in sections if not s.get("content", "").strip()]

        task = BatchTask(
            task_id=task_id,
            document_id=document_id,
            sections=sections,
            operation_mode=operation_mode,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            process_empty_only=process_empty_only,
            client_id=client_id
        )

        self.tasks[task_id] = task
        return task_id

    async def start_task(self, task_id: str, websocket_manager, generate_callback):
        """Start a batch processing task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]

        if task.status == BatchStatus.RUNNING:
            raise ValueError(f"Task {task_id} is already running")

        # Create async task
        async_task = asyncio.create_task(
            self._process_task(task, websocket_manager, generate_callback)
        )
        self.running_tasks[task_id] = async_task

        return task

    async def pause_task(self, task_id: str):
        """Pause a running task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]

        if task.status != BatchStatus.RUNNING:
            raise ValueError(f"Task {task_id} is not running")

        task.status = BatchStatus.PAUSED

    async def resume_task(self, task_id: str, websocket_manager, generate_callback):
        """Resume a paused task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]

        if task.status != BatchStatus.PAUSED:
            raise ValueError(f"Task {task_id} is not paused")

        task.status = BatchStatus.RUNNING

        # Continue processing
        async_task = asyncio.create_task(
            self._process_task(task, websocket_manager, generate_callback)
        )
        self.running_tasks[task_id] = async_task

    async def cancel_task(self, task_id: str):
        """Cancel a task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]
        task.status = BatchStatus.CANCELLED

        # Cancel async task if running
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        return self.tasks[task_id].to_dict()

    async def _process_task(self, task: BatchTask, websocket_manager, generate_callback):
        """Process a batch task"""
        try:
            task.status = BatchStatus.RUNNING
            task.started_at = datetime.utcnow()

            # Send initial status
            await self._send_progress(task, websocket_manager, "started")

            # Process each section
            for i in range(task.current_section, task.total_sections):
                # Check if paused or cancelled
                if task.status == BatchStatus.PAUSED:
                    task.current_section = i
                    await self._send_progress(task, websocket_manager, "paused")
                    return

                if task.status == BatchStatus.CANCELLED:
                    await self._send_progress(task, websocket_manager, "cancelled")
                    return

                section = task.sections[i]
                task.current_section = i

                # Send progress update
                await self._send_progress(
                    task,
                    websocket_manager,
                    "processing",
                    current_section=section
                )

                try:
                    # Generate content for section
                    result = await generate_callback(
                        section_id=section["id"],
                        section_title=section["title"],
                        existing_content=section.get("content", ""),
                        operation_mode=task.operation_mode,
                        model=task.model,
                        temperature=task.temperature,
                        max_tokens=task.max_tokens
                    )

                    task.results.append({
                        "section_id": section["id"],
                        "section_title": section["title"],
                        "success": True,
                        "content": result["generated_content"],
                        "tokens_used": result.get("tokens_used", 0)
                    })

                    task.completed_sections += 1

                    # Send section completed update
                    await self._send_progress(
                        task,
                        websocket_manager,
                        "section_completed",
                        current_section=section,
                        result=result
                    )

                except Exception as e:
                    task.failed_sections += 1
                    task.results.append({
                        "section_id": section["id"],
                        "section_title": section["title"],
                        "success": False,
                        "error": str(e)
                    })

                    # Send section failed update
                    await self._send_progress(
                        task,
                        websocket_manager,
                        "section_failed",
                        current_section=section,
                        error=str(e)
                    )

                # Small delay between sections
                await asyncio.sleep(0.5)

            # Task completed
            task.status = BatchStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            await self._send_progress(task, websocket_manager, "completed")

            # Clean up
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]

        except Exception as e:
            task.status = BatchStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()

            await self._send_progress(task, websocket_manager, "failed", error=str(e))

            # Clean up
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]

    async def _send_progress(
        self,
        task: BatchTask,
        websocket_manager,
        event_type: str,
        current_section: Optional[Dict] = None,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Send progress update via WebSocket"""
        if not task.client_id:
            return

        message = {
            "type": "batch_progress",
            "event": event_type,
            "task": task.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        }

        if current_section:
            message["current_section"] = {
                "id": current_section["id"],
                "title": current_section["title"]
            }

        if result:
            message["result"] = result

        if error:
            message["error"] = error

        try:
            await websocket_manager.send_message(message, task.client_id)
        except Exception as e:
            print(f"Failed to send WebSocket message: {e}")

# Global batch processor instance
batch_processor = BatchProcessor()
