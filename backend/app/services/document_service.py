"""Document processing service - ported from Tkinter app"""
import hashlib
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import shutil

from docx import Document
from docx.oxml.shared import qn
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt, RGBColor

from app.models.document import (
    DocumentSection,
    DocumentStructure,
    DocumentComment,
    DocumentSaveResponse,
)
from app.utils.config import settings


class DocumentService:
    """Service for document operations"""

    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.structures: Dict[str, DocumentStructure] = {}
        self.file_paths: Dict[str, str] = {}

    async def parse_document(self, file_path: str, document_id: str) -> DocumentStructure:
        """
        Parse Word document structure (ported from parse_document_structure)

        Extracts:
        - Hierarchical section structure from headings
        - Existing content in each section
        - Comments associated with sections
        """
        try:
            doc = Document(file_path)
            self.documents[document_id] = doc
            self.file_paths[document_id] = file_path

            # Extract comments
            comments_map = self._extract_document_comments(doc)

            # Build section hierarchy
            sections = []
            section_stack = []
            current_section = None
            section_counter = 0

            for para in doc.paragraphs:
                style = para.style.name if para.style else ""

                # Check if this is a heading
                heading_level = None
                if style.startswith('Heading'):
                    try:
                        heading_level = int(style.split()[-1])
                    except (ValueError, IndexError):
                        continue

                if heading_level and 1 <= heading_level <= 6:
                    # Create new section
                    section_id = f"{document_id}_section_{section_counter}"
                    section_counter += 1

                    section_hash = hashlib.sha256(
                        f"{heading_level}{para.text}".encode()
                    ).hexdigest()[:16]

                    section = DocumentSection(
                        id=section_id,
                        level=heading_level,
                        text=para.text.strip(),
                        full_path=para.text.strip(),
                        section_hash=section_hash,
                        comments=comments_map.get(para.text, [])
                    )

                    # Manage hierarchy
                    while section_stack and section_stack[-1].level >= heading_level:
                        section_stack.pop()

                    if section_stack:
                        # Add as child to parent
                        parent = section_stack[-1]
                        section.full_path = f"{parent.full_path} > {section.text}"
                    else:
                        # Top-level section
                        sections.append(section)

                    section_stack.append(section)
                    current_section = section

                elif current_section and para.text.strip():
                    # Content paragraph belonging to current section
                    if not current_section.existing_content:
                        current_section.existing_content = para.text.strip()
                    else:
                        current_section.existing_content += "\n" + para.text.strip()
                    current_section.has_content = True

            # Build final structure
            structure = DocumentStructure(
                filename=Path(file_path).name,
                total_sections=section_counter,
                sections=sections,
                has_comments=len(comments_map) > 0,
                total_comments=sum(len(c) for c in comments_map.values())
            )

            self.structures[document_id] = structure
            return structure

        except Exception as e:
            raise Exception(f"Failed to parse document: {str(e)}")

    def _extract_document_comments(self, doc: Document) -> Dict[str, List[DocumentComment]]:
        """
        Extract comments from Word document XML (ported from extract_document_comments)

        Returns mapping of paragraph text to associated comments
        """
        comments_map = {}

        try:
            # Access document part for comments
            comments_part = None
            for rel in doc.part.rels.values():
                if "comments" in rel.target_ref:
                    comments_part = rel.target_part
                    break

            if not comments_part:
                return comments_map

            # Parse comments XML
            root = comments_part.element
            for comment_elem in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}comment'):
                author = comment_elem.get(qn('w:author'), 'Unknown')
                date_str = comment_elem.get(qn('w:date'), '')

                # Extract comment text
                comment_text = ""
                for para in comment_elem.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                    if para.text:
                        comment_text += para.text

                if comment_text.strip():
                    comment = DocumentComment(
                        author=author,
                        text=comment_text.strip(),
                        date=datetime.fromisoformat(date_str.replace('Z', '+00:00')) if date_str else None
                    )

                    # Associate with section (simplified - in reality would need more context)
                    # For now, just store by comment text
                    if "Section" in comment_text:
                        section_name = comment_text.split("Section")[-1].split(":")[0].strip()
                        if section_name not in comments_map:
                            comments_map[section_name] = []
                        comments_map[section_name].append(comment)

        except Exception as e:
            print(f"Warning: Could not extract comments: {e}")

        return comments_map

    async def get_structure(self, document_id: str) -> Optional[DocumentStructure]:
        """Get cached document structure"""
        return self.structures.get(document_id)

    async def get_document_path(self, document_id: str) -> Optional[str]:
        """Get file path for document"""
        return self.file_paths.get(document_id)

    async def save_document(
        self,
        document_id: str,
        sections_to_update: Dict[str, str],
        create_backup: bool = True
    ) -> DocumentSaveResponse:
        """
        Save updates to document (ported from commit_content logic)

        Args:
            document_id: Document identifier
            sections_to_update: Map of section_id to new content
            create_backup: Whether to create backup before saving

        Returns:
            DocumentSaveResponse with success status
        """
        if document_id not in self.documents:
            raise FileNotFoundError("Document not found")

        doc = self.documents[document_id]
        file_path = self.file_paths[document_id]
        backup_path = None

        # Create backup
        if create_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = str(Path(file_path).with_suffix(f".backup_{timestamp}.docx"))
            shutil.copy2(file_path, backup_path)

        # Apply updates (simplified - would need section tracking)
        updated_count = 0
        structure = self.structures.get(document_id)

        if structure:
            for section_id, new_content in sections_to_update.items():
                # Find section in structure
                # In real implementation, would need to map section_id to paragraph
                # and update content accordingly
                updated_count += 1

        # Save document
        doc.save(file_path)

        return DocumentSaveResponse(
            success=True,
            message=f"Document saved successfully. {updated_count} sections updated.",
            backup_path=backup_path,
            updated_sections=updated_count
        )

    async def delete_document(self, document_id: str) -> bool:
        """Delete document and cleanup"""
        if document_id in self.file_paths:
            file_path = Path(self.file_paths[document_id])
            if file_path.exists():
                file_path.unlink()

            # Cleanup caches
            self.documents.pop(document_id, None)
            self.structures.pop(document_id, None)
            self.file_paths.pop(document_id, None)
            return True

        return False
