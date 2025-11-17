# Document Filler Codebase Overview

## Project Summary

**Document Filler** is a sophisticated Python GUI application for automatically generating and managing content in Word documents (DOCX format) using OpenWebUI/Ollama with RAG (Retrieval-Augmented Generation) support. It's designed specifically for DoD (Department of Defense) cybersecurity documentation compliance with NIST, RMF, and FedRAMP standards.

---

## 1. Project Structure

```
documentfiller/
├── documentFiller.py              (615 lines)   - Original baseline implementation
├── documentFiller2.py             (2,727 lines) - V2 with enhanced features
├── documentFiller3.py             (3,957 lines) - V3 with advanced review system
├── documentFiller4.py             (5,625 lines) - V4 with model comparison
├── documentFiller5.py             (6,704 lines) - CURRENT: Latest with all features
├── content_processor.py           (615 lines)   - Intelligent RAG processing
├── credential_manager.py          (336 lines)   - Encrypted credentials handling
├── document_reviewer.py           (641 lines)   - Technical document analysis
├── openwebui_config.json          - Configuration for OpenWebUI
├── GCSSMC_Master_prompt.txt       - Master prompt template
└── ollama_config.json             - Ollama configuration
```

**Total Codebase: 21,851 lines of Python**

---

## 2. Core Architecture

### 2.1 Main Application Class: `DocxDocumentFiller`
- **File**: `documentFiller5.py` (lines 200-6700+)
- **Framework**: Tkinter (Python's standard GUI library)
- **Theme**: Dark mode with custom styling

### 2.2 Document Structure Representation

#### DocumentSection Class (lines 65-102)
Represents hierarchical document sections:
```python
class DocumentSection:
    - level: Heading level (1-4)
    - text: Section title
    - paragraph: Reference to docx paragraph
    - children: Child sections
    - parent: Parent section
    - content_paragraphs: Content under this section
```

**Key Methods**:
- `get_full_path()`: Get hierarchical path (e.g., "Chapter > Section > Subsection")
- `get_existing_content()`: Retrieve text content from section
- `has_content()`: Check if section has existing text
- `get_section_hash()`: Unique hash for tracking

#### DocumentReview Class (lines 103-199)
Tracks technical writing reviews:
```python
class DocumentReview:
    - section_path: Section being reviewed
    - timestamp: When review was conducted
    - cohesion_score: 1-10
    - clarity_score: 1-10
    - technical_accuracy_score: 1-10
    - factual_veracity_score: 1-10
    - completeness_score: 1-10
    - overall_score: Calculated average
    - feedback: Dict with feedback categories
    - recommendations: List of improvements
```

---

## 3. RAG/Content Generation Implementation

### 3.1 Intelligent Content Processor Module
**File**: `content_processor.py`

#### Core Components:

**DocumentChunk Dataclass** (lines 24-37):
Represents chunked content for RAG:
```python
@dataclass
class DocumentChunk:
    id: str                           # Unique identifier
    content: str                      # Text content
    section_path: str                 # Where it comes from
    char_count: int                   # Character length
    token_count: int                  # Token count
    embedding: Optional[List[float]]  # Vector embedding (optional)
    metadata: Dict                    # Additional data
```

**ProcessingStrategy Dataclass** (lines 40-46):
Determines optimal content processing approach:
```python
@dataclass
class ProcessingStrategy:
    method: str                       # "full_prompt", "rag", or "hybrid"
    reason: str                       # Why this strategy
    token_estimate: int              # Expected token usage
    chunk_count: int                 # Number of chunks
    confidence: float                # Confidence score 0-1
```

#### Key Functions:

1. **`analyze_content_metrics(content, sections)`** (lines 137-188)
   - Calculates character count and token count using `tiktoken`
   - Computes complexity score based on:
     - Sentence length
     - Technical term density
     - Code/syntax indicators
   - Returns ContentMetrics dataclass

2. **`determine_processing_strategy(content, sections, query_context)`** (lines 190-243)
   - Decision logic:
     - Content < 60% of max tokens → `full_prompt` (9/10 confidence)
     - Large multi-section (>10K chars, >5 sections) → `rag` (8/10 confidence)
     - High complexity (>0.7 score, >3 sections) → `hybrid` (7/10 confidence)
     - Default → `full_prompt` with truncation (6/10 confidence)

3. **`chunk_content(content, document_path, sections)`** (lines 245-279)
   - Section-based chunking (chunks by document sections first)
   - Size-based chunking (for large sections)
   - Maintains overlap for context preservation

4. **`build_rag_context(query, document_path, sections)`**
   - Retrieves relevant chunks using TF-IDF similarity
   - Ranks results by relevance score
   - Formats context for LLM prompt

#### Database: SQLite Document Store
```sql
CREATE TABLE document_chunks (
    id TEXT PRIMARY KEY,
    document_path TEXT,
    section_path TEXT,
    content TEXT,
    char_count INTEGER,
    token_count INTEGER,
    embedding BLOB,
    metadata TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

CREATE TABLE document_metadata (
    document_path TEXT PRIMARY KEY,
    total_chunks INTEGER,
    processing_strategy TEXT,
    last_processed TIMESTAMP,
    content_hash TEXT
)
```

#### ML Components:
- **Tokenizer**: OpenAI's `tiktoken` (cl100k_base encoding)
- **Similarity Search**: TF-IDF vectorizer from scikit-learn
- **Cache**: In-memory with 1-hour TTL for processed documents

---

## 4. Content Generation Pipeline

### 4.1 Generation Flow

```
1. User selects section → generate_content()
2. Spawns background thread → generate_content_thread()
3. Build prompt with:
   - Master prompt template
   - Section name and path
   - Parent context
   - Operation mode (replace/rework/append)
   - Existing content (if mode = rework/append)
   - RAG context (if applicable)
4. Query OpenWebUI API → query_openwebui()
5. Process strategy: Applies intelligent processing
6. Display in preview → show_generated_content()
7. User edits (optional) in editable text widget
8. Commit to document → commit_content()
```

### 4.2 Generate Content Function
**Location**: Lines 2915-2995

```python
def generate_content():
    # Validates selection and model config
    # Switches to console tab
    # Spawns background thread
    
def generate_content_thread():
    # Gets section and existing content
    # Builds hierarchical parent context
    # Substitutes variables in master prompt:
    #   {section_name}
    #   {parent_context}
    #   {operation_mode}
    # Adds mode-specific instructions
    # Applies intelligent processing (if available)
    # Queries OpenWebUI with retry logic
    # Updates UI with results
```

### 4.3 Operation Modes

1. **Replace**: Generate content from scratch
   - Instruction: "Write comprehensive content for this section from scratch"
   
2. **Rework**: Enhance existing content
   - Instruction: "Rewrite and enhance the existing content"
   - Includes existing content in prompt
   
3. **Append**: Add to existing content
   - Instruction: "Add additional relevant content"
   - Includes existing content for context

### 4.4 OpenWebUI API Integration
**Location**: Lines 2996-3070

```python
def query_openwebui(prompt):
    # Builds request headers with API key
    payload = {
        "model": selected_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": temperature (default 0.1),
        "max_tokens": max_tokens (default 8000),
        "files": []  # RAG collections if selected
    }
    
    # POST to http://base_url/api/chat/completions
    # Timeout: 300 seconds
    # Returns: response['choices'][0]['message']['content']
```

**Configuration**:
- Base URL: `http://172.16.27.122:3000` (configurable)
- API Key: From openwebui_config.json (secured with encryption)
- Models: Dynamically loaded from OpenWebUI API
- Knowledge Collections: Multiple RAG sources selectable

### 4.5 Prompt Template System
**Master Prompt** includes:

1. **System Context**:
   - DoD cybersecurity expertise
   - Zero Trust Architecture focus
   - NIST SP 800-53, RMF, FedRAMP compliance

2. **Requirements**:
   - Formal business language
   - Technical accuracy
   - Markdown formatting support
   - Implementation-focused (not policy)

3. **Tools & Team Composition**:
   - Security tools (CyberArk, OKTA, Palo Alto, Tenable, etc.)
   - Team roles (ISSOs, ISSEs, SecOps, ICAM, AppSec)

4. **Variable Substitution**:
   - `{section_name}`: Section being filled
   - `{parent_context}`: Hierarchical parent sections
   - `{operation_mode}`: REPLACE, REWORK, or APPEND

---

## 5. Document Editing & Commits

### 5.1 Document Manipulation
Uses `python-docx` library for DOCX handling.

#### Document Loading (lines 393-415)
```python
def load_document(filepath):
    # Load DOCX file
    # Parse document structure (hierarchical sections)
    # Populate UI tree view
    # Save as "last document" for auto-reload
```

#### Structure Parsing (lines 416-450)
- Iterates through paragraphs
- Identifies headings (Heading 1-4)
- Builds hierarchical section tree
- Associates content paragraphs with sections

### 5.2 Content Commitment Process
**Location**: Lines 3996-4062

```python
def commit_content():
    1. Get content from editable preview widget
    2. Confirm with user (dialog box)
    3. Check backup settings (optional prompt)
    4. Create backup copy (timestamp: YYYYMMDD_HHMMSS)
    5. Apply changes based on operation mode:
       - REPLACE: remove_section_content() + add_markdown_content_to_section()
       - REWORK: same as replace
       - APPEND: append_section_content()
    6. Mark section as edited (in tracking dict)
    7. Refresh UI tree
    8. Auto-save document (if enabled)
    9. Auto-reload document (if enabled)
    10. Clear preview and show updated content
```

### 5.3 Content Formatting

#### Markdown Processing (lines 4986-5250+)
Converts markdown to DOCX formatting:

**Supported Markdown**:
- Headers: `# Header 1`, `## Header 2`, etc.
- Bold: `**text**`
- Italic: `*text*`
- Code: `` `code` `` or ` ```code block``` `
- Lists: `- item` (unordered), `1. item` (numbered)
- Tables: Pipe-delimited format
- Blockquotes: `> quote`
- Horizontal rules: `---`, `***`
- Definition lists: `term: definition`

**Implementation**: `render_markdown_preview()` and `apply_markdown_to_paragraph()`
- Parses markdown syntax with regex
- Applies DOCX formatting (bold, italic, color, etc.)
- Handles tables with cell styling
- Inserts at correct paragraph position

### 5.4 Backup System
**Location**: Lines 4110-4126

```python
def create_backup():
    # Triggered before commit
    # Creates copy: filename_backup_YYYYMMDD_HHMMSS.docx
    # Same directory as original
    # Timestamp-based, no overwrites
    # Optional prompt with "don't ask again" option
```

### 5.5 Auto-Save & Auto-Reload
**Configuration** (in `auto_config` dict):
- `auto_backup`: Enable automatic backups (default: True)
- `backup_interval`: Minutes between auto-backups (default: 5)
- `auto_save`: Auto-save after commit (default: False)
- `auto_reload`: Reload document after commit (default: True)
- `ask_backup`: Prompt before backup (default: True)

---

## 6. Advanced Features in DocumentFiller5

### 6.1 Technical Document Review System
**Location**: Lines 432-770

#### Review Workflow:
1. User selects section → `conduct_section_review()`
2. Builds review prompt using `set_review_prompt()`
3. Sends to OpenWebUI for expert review
4. Parses JSON response → `_parse_review_response()`
5. Displays results with scores: `_display_review_results()`

#### Review Criteria (Scored 1-10):
- **Cohesion**: Flow, transitions, narrative consistency
- **Clarity**: Readability, terminology, conciseness
- **Technical Accuracy**: Correctness of technical details
- **Factual Veracity**: Accuracy of facts and claims
- **Completeness**: Addresses purpose, answers questions

#### Review Actions:
- **Apply Suggestions**: Auto-improve content using review feedback
- **Regenerate from Review**: Full rewrite based on feedback
- **Accept/Reject**: User decision on suggestions

### 6.2 Tense Consistency Analysis
**Location**: Lines 6600-6643

Uses `TechnicalDocumentReviewer.analyze_tense_consistency()`:
- Detects dominant tense (past/present/future)
- Calculates consistency score (0-10)
- Identifies inconsistent sentences
- Reports tense distribution

### 6.3 Model Comparison Feature
**Location**: Lines 3642-3941

Compare responses from up to 3 models simultaneously:
1. Select 3 different models
2. Same prompt sent to all
3. Results displayed side-by-side
4. User selects best version
5. Option to update master prompt with preferred style

### 6.4 Auto-Complete Document
**Location**: Lines 3184-3336

Batch generate content for multiple sections:
- Options:
  - Complete ALL sections (overwrites existing)
  - Complete only EMPTY sections
  - Custom selection from tree
- Progress tracking with live log
- Pause/Resume functionality
- Error recovery

### 6.5 Prompt History & Learning
**Location**: Lines 1522-1650+ (create_prompt_history_tab)

Tracks all prompts and responses:
- Timestamp for each interaction
- Full prompt text (editable)
- Response content
- Model used
- Can review past generations
- Learn from successful patterns

### 6.6 Markdown Export/Import
**Location**: Lines 4136-4215

- Export generated content to `.md` file
- Import content from markdown for editing
- Useful for external processing

### 6.7 Section Tracking & Editing History
**Location**: Lines 993-1031

Maintains metadata for each section:
```json
{
    "section_hash": {
        "edited": true/false,
        "last_edited": timestamp,
        "edit_count": number,
        "model_used": "model_name"
    }
}
```

### 6.8 Encrypted Credentials Manager
**Location**: `credential_manager.py`

Features:
- PBKDF2-HMAC SHA256 key derivation
- Fernet (AES) encryption for data
- Salt generation for security
- Password-protected configuration storage
- Master password for sensitive data

---

## 7. Technology Stack

### Core Dependencies
```
Python 3.x
├── tkinter              - GUI framework (built-in)
├── python-docx         - DOCX manipulation & editing
├── requests            - HTTP API calls to OpenWebUI
├── cryptography        - Encrypted credentials (Fernet)
├── tiktoken            - Token counting (OpenAI's tokenizer)
├── scikit-learn        - TF-IDF vectorization for similarity
├── numpy               - Numerical operations
├── nltk                - Natural language processing
├── textstat            - Readability metrics
└── sqlite3             - Document chunk storage (built-in)
```

### External Services
- **OpenWebUI**: LLM interface (HTTP REST API)
- **Ollama**: Local LLM runtime
- **Knowledge Collections**: RAG data sources

### Installation
```bash
python -m pip install --break-system-packages \
    cryptography textstat nltk tiktoken scikit-learn \
    numpy requests python-docx
```

---

## 8. Configuration System

### 8.1 Configuration Files

**openwebui_config.json**:
```json
{
    "base_url": "http://172.16.27.122:3000",
    "api_key": "sk-...",
    "model": "llama4:latest",
    "temperature": 0.07,
    "max_tokens": 80000,
    "knowledge_collections": [
        {"id": "uuid", "name": "USMC"},
        {"id": "uuid", "name": "NIST"},
        {"id": "uuid", "name": "DoD"},
        {"id": "uuid", "name": "CCI"}
    ],
    "master_prompt": "...",
    "format_config": {
        "highlight_enabled": false,
        "bold_enabled": false,
        "font_size": 12
    },
    "auto_config": {
        "auto_backup": false,
        "auto_save": false,
        "auto_reload": true
    }
}
```

**last_document.txt**:
- Stores path to last opened document for quick reload

### 8.2 Settings Persistence
- Auto-loads on startup
- Saves after any configuration change
- Last document auto-loaded if available
- User preferences (temp, tokens, models) preserved

---

## 9. GUI Layout & Components

### 9.1 Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│  DoD Document Filler - OpenWebUI Integration                │
├─────────────────────────────────────────────────────────────┤
│ [Load Document] Document Name                               │
│ [Configure] OpenWebUI Configuration Status                  │
├──────────────────────────┬──────────────────────────────────┤
│  LEFT PANEL              │       RIGHT PANEL                 │
│  (Narrow)                │       (Wide)                      │
│                          │                                   │
│ ┌─ Document Sections ──┐ │  ┌─ TABS ─────────────────────┐ │
│ │ [+] Chapter          │ │  │ Content | Prompt | Console │ │
│ │   [+] Section 1      │ │  ├─────────────────────────────┤ │
│ │   [+] Section 2      │ │  │  LEFT: Existing | RIGHT:   │ │
│ │   [+] Section 3      │ │  │        Generated (editable) │ │
│ │                      │ │  │                             │ │
│ │ [Select] Selected    │ │  │ [Commit] [Clear] [Export] │ │
│ └──────────────────────┘ │  │                             │ │
│                          │  │ PROMPT TAB:                 │ │
│ ┌─ Operation Mode ─────┐ │  │ [Last sent prompt]          │ │
│ │ ⦿ Replace (scratch)  │ │  │                             │ │
│ │ ○ Rework (enhance)   │ │  │ CONSOLE TAB:                │ │
│ │ ○ Append (add)       │ │  │ [Logs & status messages]    │ │
│ └──────────────────────┘ │  └─────────────────────────────┘ │
│                          │                                   │
│ [Generate Content]       │                                   │
│ [Edit Master Prompt]     │                                   │
│ [Review Section]         │                                   │
│ [Compare Models]         │                                   │
│ [Analyze Tenses]         │                                   │
│ [Auto-Complete]          │                                   │
│                          │                                   │
└──────────────────────────┴──────────────────────────────────┘
```

### 9.2 Major Dialogs

1. **Configuration Dialog**: Connection, model selection, knowledge collections, parameters
2. **Review Results Dialog**: Scores, feedback, recommendations, action buttons
3. **Model Comparison Window**: Side-by-side model outputs
4. **Auto-Complete Progress**: Section list with progress bar and live log
5. **Credentials Manager**: Encrypted password setup and management

---

## 10. Current Capabilities Summary

### Content Generation
- AI-powered content generation for document sections
- Multiple operation modes (replace/rework/append)
- RAG integration for contextual generation
- Model selection and configuration
- Temperature and token controls
- Knowledge collection integration
- Prompt customization with variables

### Document Handling
- Load/save DOCX documents
- Hierarchical section tree navigation
- Parse multi-level document structure
- Support for up to Heading 4
- Backup before commits
- Auto-save and auto-reload
- Document outline viewing

### Content Processing
- Intelligent strategy selection (full_prompt/RAG/hybrid)
- Chunking with overlap
- TF-IDF similarity ranking
- Token counting and estimation
- Content complexity analysis
- SQLite document store

### Advanced Features
- Technical writing review (cohesion, clarity, accuracy, completeness)
- Tense consistency analysis
- Model comparison (3-way simultaneous)
- Markdown to DOCX conversion
- Table creation and styling
- Auto-complete for multiple sections
- Prompt history tracking
- Encrypted credential storage
- Formatting options (bold, italic, color, size)

### User Experience
- Dark theme GUI
- Editable content preview
- Live console logs
- Real-time model status
- Progress tracking
- Error handling and recovery
- Configuration persistence
- Auto-backup system

---

## 11. Evolution Across Versions

| Version | Lines | Key Additions |
|---------|-------|---|
| V1      | 1,246 | Baseline: document loading, basic generation, model config |
| V2      | 2,727 | +Enhanced prompting, +operation modes, +knowledge collections |
| V3      | 3,957 | +Technical review system, +tense analysis, +markdown support |
| V4      | 5,625 | +Model comparison, +auto-complete, +prompt history, +tables |
| V5      | 6,704 | +Encrypted credentials, +RAG optimization, +formatting controls |

---

## 12. Workflow Examples

### Example 1: Generate Section Content
```
1. Load Document (File → Open)
2. Select section from tree
3. View existing content (left panel)
4. Click "Generate Content"
5. System analyzes content → chooses strategy (full_prompt/RAG/hybrid)
6. Sends prompt to OpenWebUI with knowledge collections
7. Display result in right panel (green text, editable)
8. User reviews and edits if needed
9. Click "Commit to Document"
10. Backup created → content replaced → document saved
11. Document reloaded with new content
```

### Example 2: Review & Improve Content
```
1. Select section with existing content
2. Click "Review Section"
3. Sends to technical reviewer
4. Displays scores and feedback:
   - Cohesion: 7/10 - needs better transitions
   - Clarity: 8/10 - good
   - Accuracy: 9/10 - accurate
   - etc.
5. Click "Apply Suggestions" → LLM improves content
6. Review improved version
7. Commit or regenerate with different feedback
```

### Example 3: Auto-Complete Document
```
1. Load document with partial content
2. Tools → Auto-Complete Document
3. Choose: ALL sections or EMPTY only
4. System generates for each section in order
5. Shows progress with section names
6. Live log shows which sections completed
7. Can pause/resume or skip problem areas
8. Save document when complete
```

---

## Summary

The **Document Filler** is a sophisticated, feature-rich application that demonstrates:

- **Advanced GUI Design** with Tkinter and dark theme
- **RAG Implementation** with intelligent strategy selection
- **API Integration** with OpenWebUI/Ollama
- **Document Processing** using python-docx
- **NLP Capabilities** for review and analysis
- **Encryption** for secure credential storage
- **Batch Processing** for efficiency
- **Version Evolution** showing gradual feature addition

It's specifically tailored for DoD documentation where compliance, accuracy, and professional quality are paramount. The multi-version history shows thoughtful development progression from core functionality through advanced features.
