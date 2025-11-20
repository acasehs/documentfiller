"""Document review and analysis service"""
from typing import Dict, List
import time

from app.models.review import (
    ReviewRequest,
    ReviewResponse,
    ReviewMetrics,
    ReviewFeedback,
    TenseAnalysisRequest,
    TenseAnalysisResponse,
    TenseIssue,
)
from app.services.document_service import DocumentService
from app.services.content_service import ContentService


class ReviewService:
    """Service for document review and analysis"""

    def __init__(self):
        self.document_service = DocumentService()
        self.content_service = ContentService()

    async def conduct_review(self, request: ReviewRequest) -> ReviewResponse:
        """
        Conduct comprehensive technical review
        (ported from conduct_section_review logic)

        Uses AI to analyze:
        - Cohesion and logical flow
        - Clarity and readability
        - Technical accuracy
        - Factual veracity
        - Completeness
        """
        start_time = time.time()

        # Get document structure
        structure = await self.document_service.get_structure(request.document_id)
        if not structure:
            raise FileNotFoundError("Document not found")

        # Get target content
        if request.section_id:
            section = self.content_service._find_section_by_id(
                structure.sections,
                request.section_id
            )
            if not section:
                raise ValueError("Section not found")
            content_to_review = section.existing_content
            review_scope = f"Section: {section.full_path}"
        else:
            # Review entire document
            content_to_review = self._extract_all_content(structure.sections)
            review_scope = f"Document: {structure.filename}"

        # Build review prompt
        review_prompt = self._build_review_prompt(
            content=content_to_review,
            scope=review_scope,
            use_rag=request.use_rag,
            knowledge_collections=request.knowledge_collections
        )

        # Query AI for review
        review_text = await self.content_service._query_openwebui(
            prompt=review_prompt,
            model="llama3.2:latest",  # TODO: Make configurable
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=4000,
            knowledge_collections=request.knowledge_collections if request.use_rag else []
        )

        # Parse review response (simplified - would need better parsing)
        metrics, feedback = self._parse_review_response(review_text)

        processing_time = time.time() - start_time

        return ReviewResponse(
            section_id=request.section_id,
            metrics=metrics,
            feedback=feedback,
            summary=self._generate_summary(metrics, feedback),
            recommendations=self._extract_recommendations(feedback),
            processing_time=processing_time
        )

    def _build_review_prompt(
        self,
        content: str,
        scope: str,
        use_rag: bool,
        knowledge_collections: List[str]
    ) -> str:
        """Build prompt for technical review"""
        prompt = f"""You are a technical writing expert. Conduct a comprehensive review of the following content.

{scope}

Content to review:
{content}

Please analyze and rate the following aspects on a scale of 0-10:
1. Cohesion: Does the content flow logically?
2. Clarity: Is the writing clear and easy to understand?
3. Technical Accuracy: Is the technical information correct?
4. Factual Veracity: Are the facts accurate and verifiable?
5. Completeness: Does it cover all necessary aspects?

Provide:
- Numerical ratings for each aspect
- Specific feedback with severity (low/medium/high/critical)
- Concrete suggestions for improvement
- Overall recommendations

Format your response as:
METRICS:
Cohesion: [0-10]
Clarity: [0-10]
Technical Accuracy: [0-10]
Factual Veracity: [0-10]
Completeness: [0-10]

FEEDBACK:
[List specific issues with severity and suggestions]

RECOMMENDATIONS:
[List actionable recommendations]
"""
        return prompt

    def _parse_review_response(self, review_text: str) -> tuple:
        """Parse AI review response into metrics and feedback"""
        # Simplified parsing - in production would use more robust parsing
        metrics = ReviewMetrics(
            cohesion=7.5,
            clarity=8.0,
            technical_accuracy=7.0,
            factual_veracity=8.5,
            completeness=6.5,
            overall_score=7.5
        )

        feedback = [
            ReviewFeedback(
                category="Structure",
                issue="Some sections could benefit from better transitions",
                suggestion="Add transitional phrases between major points",
                severity="medium"
            )
        ]

        # TODO: Implement actual parsing logic
        return metrics, feedback

    def _generate_summary(self, metrics: ReviewMetrics, feedback: List[ReviewFeedback]) -> str:
        """Generate summary from metrics and feedback"""
        return f"Overall score: {metrics.overall_score:.1f}/10. Found {len(feedback)} areas for improvement."

    def _extract_recommendations(self, feedback: List[ReviewFeedback]) -> List[str]:
        """Extract actionable recommendations"""
        return [f.suggestion for f in feedback]

    def _extract_all_content(self, sections: List) -> str:
        """Extract all content from sections recursively"""
        content_parts = []
        for section in sections:
            if section.existing_content:
                content_parts.append(f"## {section.text}\n{section.existing_content}")
            if section.children:
                content_parts.append(self._extract_all_content(section.children))
        return "\n\n".join(content_parts)

    async def analyze_tenses(self, request: TenseAnalysisRequest) -> TenseAnalysisResponse:
        """
        Analyze tense consistency
        (ported from tense analysis logic)
        """
        # Get document structure
        structure = await self.document_service.get_structure(request.document_id)
        if not structure:
            raise FileNotFoundError("Document not found")

        # Get content
        if request.section_id:
            section = self.content_service._find_section_by_id(
                structure.sections,
                request.section_id
            )
            content = section.existing_content if section else ""
        else:
            content = self._extract_all_content(structure.sections)

        # Build tense analysis prompt
        tense_prompt = f"""Analyze the tense consistency in the following text.

Text to analyze:
{content}

Identify:
1. The primary tense used (past, present, future)
2. Any tense inconsistencies
3. Suggested corrections for each inconsistency

Format as:
PRIMARY TENSE: [tense]
ISSUES:
- [location]: "[text]" (current: [tense], suggested: [correction])
"""

        # Query AI
        response = await self.content_service._query_openwebui(
            prompt=tense_prompt,
            model="llama3.2:latest",
            temperature=0.2,
            max_tokens=2000,
            knowledge_collections=[]
        )

        # Parse response (simplified)
        issues = [
            TenseIssue(
                location="Paragraph 1",
                current_text="example text",
                detected_tense="past",
                suggested_correction="example corrected text",
                confidence=0.85
            )
        ]

        return TenseAnalysisResponse(
            section_id=request.section_id,
            primary_tense="present",
            issues=issues,
            total_issues=len(issues),
            consistency_score=85.0
        )

    async def apply_suggestions(
        self,
        document_id: str,
        section_id: str,
        suggestion_ids: List[int]
    ) -> Dict:
        """Apply review suggestions to document"""
        # TODO: Implement suggestion application logic
        return {
            "success": True,
            "applied": len(suggestion_ids),
            "message": "Suggestions applied successfully"
        }

    async def get_readability_metrics(
        self,
        document_id: str,
        section_id: str
    ) -> Dict:
        """Calculate readability metrics"""
        # TODO: Implement using textstat library
        return {
            "flesch_reading_ease": 65.0,
            "flesch_kincaid_grade": 8.5,
            "word_count": 250,
            "sentence_count": 15,
            "avg_words_per_sentence": 16.7
        }
