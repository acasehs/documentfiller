"""Content generation service - OpenWebUI integration"""
import time
from typing import List, Dict, Optional, Callable
import httpx

from app.models.content import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    ModelComparisonRequest,
    ModelComparisonResponse,
    ModelComparisonResult,
    OperationMode,
)
from app.services.document_service import DocumentService
from app.utils.config import settings


class ContentService:
    """Service for AI-powered content generation"""

    def __init__(self):
        self.document_service = DocumentService()
        self.timeout = httpx.Timeout(300.0, connect=10.0)

    async def generate_content(
        self,
        request: ContentGenerationRequest,
        status_callback: Optional[Callable] = None
    ) -> ContentGenerationResponse:
        """
        Generate content using OpenWebUI (ported from query_openwebui)

        Args:
            request: Content generation parameters
            status_callback: Optional callback for real-time status updates

        Returns:
            Generated content and metadata
        """
        start_time = time.time()

        try:
            # Get document structure
            if status_callback:
                await status_callback("loading", 10, "Loading document structure...")

            structure = await self.document_service.get_structure(request.document_id)
            if not structure:
                raise FileNotFoundError("Document not found")

            # Find target section
            if status_callback:
                await status_callback("preparing", 20, "Finding target section...")

            target_section = self._find_section_by_id(structure.sections, request.section_id)
            if not target_section:
                raise ValueError("Section not found")

            # Build prompt
            if status_callback:
                await status_callback("preparing", 30, "Building prompt...")

            prompt = await self._build_prompt(
                request=request,
                section=target_section,
                structure=structure
            )

            # Query OpenWebUI
            if status_callback:
                await status_callback("generating", 50, f"Generating content with {request.model}...")

            generated_content = await self._query_openwebui(
                prompt=prompt,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                knowledge_collections=request.knowledge_collections
            )

            if status_callback:
                await status_callback("complete", 100, "Content generated successfully!")

            processing_time = time.time() - start_time

            return ContentGenerationResponse(
                section_id=request.section_id,
                generated_content=generated_content,
                prompt_used=prompt,
                model=request.model,
                processing_time=processing_time,
                success=True
            )

        except Exception as e:
            processing_time = time.time() - start_time
            return ContentGenerationResponse(
                section_id=request.section_id,
                generated_content="",
                prompt_used="",
                model=request.model,
                processing_time=processing_time,
                success=False,
                error=str(e)
            )

    async def _build_prompt(
        self,
        request: ContentGenerationRequest,
        section,
        structure
    ) -> str:
        """
        Build generation prompt based on mode and context
        (ported from build_prompt logic in documentFiller5.py)
        """
        if request.custom_prompt:
            return request.custom_prompt

        # Base context
        prompt_parts = []

        if request.use_master_prompt:
            # TODO: Load master prompt from config
            master_prompt = "You are a technical writing assistant. Generate clear, accurate, and well-structured content."
            prompt_parts.append(master_prompt)

        # Document context
        if request.include_document_context:
            prompt_parts.append(f"Document: {structure.filename}")
            prompt_parts.append(f"Section: {section.full_path}")

        # Comments as guidance
        if request.include_comments and section.comments:
            prompt_parts.append("\nGuidance from comments:")
            for comment in section.comments:
                prompt_parts.append(f"- {comment.text}")

        # Mode-specific instructions
        if request.mode == OperationMode.REPLACE:
            prompt_parts.append(f"\nGenerate content for the section '{section.text}'.")
            prompt_parts.append("Write from scratch with no existing content as reference.")

        elif request.mode == OperationMode.REWORK:
            prompt_parts.append(f"\nRework and enhance the following content for '{section.text}':")
            if section.existing_content:
                prompt_parts.append(f"\nExisting content:\n{section.existing_content}")
            prompt_parts.append("\nImprove clarity, coherence, and completeness while maintaining the core message.")

        elif request.mode == OperationMode.APPEND:
            prompt_parts.append(f"\nAppend additional content to the section '{section.text}'.")
            if section.existing_content:
                prompt_parts.append(f"\nExisting content:\n{section.existing_content}")
            prompt_parts.append("\nAdd complementary information that builds upon the existing content.")

        return "\n".join(prompt_parts)

    async def _query_openwebui(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        knowledge_collections: List[str]
    ) -> str:
        """
        Query OpenWebUI API (ported from query_openwebui)

        Non-streaming implementation with comprehensive error handling
        """
        url = f"{settings.OPENWEBUI_BASE_URL}/api/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.OPENWEBUI_API_KEY}",
            "Content-Type": "application/json"
        }

        # Build files array for RAG
        files = []
        if knowledge_collections:
            for collection in knowledge_collections:
                files.append({
                    "type": "collection",
                    "id": collection
                })

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        if files:
            payload["files"] = files

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Extract content from response
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError("Unexpected response format from OpenWebUI")

    def _find_section_by_id(self, sections: List, section_id: str):
        """Recursively find section by ID"""
        for section in sections:
            if section.id == section_id:
                return section
            if section.children:
                found = self._find_section_by_id(section.children, section_id)
                if found:
                    return found
        return None

    async def compare_models(
        self,
        request: ModelComparisonRequest
    ) -> ModelComparisonResponse:
        """
        Compare content generation across multiple models
        (ported from model_comparison dialog logic)
        """
        # Get document and section
        structure = await self.document_service.get_structure(request.document_id)
        if not structure:
            raise FileNotFoundError("Document not found")

        target_section = self._find_section_by_id(structure.sections, request.section_id)
        if not target_section:
            raise ValueError("Section not found")

        # Build base prompt
        gen_request = ContentGenerationRequest(
            document_id=request.document_id,
            section_id=request.section_id,
            mode=request.mode,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        prompt = await self._build_prompt(gen_request, target_section, structure)

        # Query each model
        results = []
        for model in request.models:
            start_time = time.time()
            try:
                content = await self._query_openwebui(
                    prompt=prompt,
                    model=model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    knowledge_collections=[]
                )
                processing_time = time.time() - start_time

                results.append(ModelComparisonResult(
                    model=model,
                    content=content,
                    processing_time=processing_time
                ))
            except Exception as e:
                processing_time = time.time() - start_time
                results.append(ModelComparisonResult(
                    model=model,
                    content="",
                    processing_time=processing_time,
                    error=str(e)
                ))

        return ModelComparisonResponse(
            section_id=request.section_id,
            results=results,
            prompt_used=prompt
        )

    async def get_available_models(self) -> List[Dict]:
        """Fetch available models from OpenWebUI"""
        url = f"{settings.OPENWEBUI_BASE_URL}/api/models"

        headers = {
            "Authorization": f"Bearer {settings.OPENWEBUI_API_KEY}"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract model list
            if "data" in data:
                return data["data"]
            return []

    async def get_knowledge_collections(self) -> List[Dict]:
        """Fetch available knowledge collections from OpenWebUI"""
        url = f"{settings.OPENWEBUI_BASE_URL}/api/v1/knowledge/"

        headers = {
            "Authorization": f"Bearer {settings.OPENWEBUI_API_KEY}"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                return data
            elif "data" in data:
                return data["data"]
            return []
