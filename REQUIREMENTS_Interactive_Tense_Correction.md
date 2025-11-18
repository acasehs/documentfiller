# Requirements: Interactive Tense Correction Feature

## Feature Overview

An interactive, sentence-level tense correction system that allows users to identify, review, and selectively correct tense inconsistencies with visual feedback and granular control.

## Current vs. Proposed Behavior

### Current Implementation
- Analyze Tenses → Shows dialog with all inconsistent sentences listed
- User clicks "Correct to [Tense]" → AI rewrites ENTIRE section
- User reviews complete rewrite → Commits or discards all changes

### Proposed Implementation
- Analyze Tenses → Highlights inconsistent sentences in **light red** within the text
- User clicks highlighted sentence → Popup shows tense options
- User selects desired tense → AI rewrites ONLY that sentence
- Corrected sentence turns **light blue** → User can see what changed
- User can correct sentences one-by-one or in batch
- Final review shows all changes before committing

---

## 1. UI/UX Requirements

### 1.1 Visual Highlighting System

**Inconsistent Sentence Highlighting (Pre-Correction)**
- **Color**: Light red background (`#ffcccc` or `#fdd`)
- **Text Color**: Dark text for readability (`#000000` or `#333333`)
- **Hover Effect**: Slightly darker red on hover to indicate clickability
- **Cursor**: Pointer cursor on hover to show interactivity
- **Border**: Optional subtle border (1px solid `#ff9999`) for clarity

**Corrected Sentence Highlighting (Post-Correction)**
- **Color**: Light blue background (`#cce5ff` or `#d0e8ff`)
- **Text Color**: Dark text for readability (`#000000` or `#333333`)
- **Indicator**: Small checkmark or pencil icon to show manual correction
- **Fade**: Optional fade animation from red → blue on correction

**Text Widget Requirements**
- Must support multiple overlapping tags
- Must allow click event handlers on tagged regions
- Must preserve formatting during tag changes
- Must handle sentence boundaries correctly (periods, question marks, exclamation points)

### 1.2 Interactive Popup Dialog

**Trigger**
- Click on any light red highlighted sentence
- Keyboard shortcut (e.g., Enter while sentence is selected)

**Popup Contents**
```
┌─────────────────────────────────────────────────┐
│ Correct Tense - Sentence Selection              │
├─────────────────────────────────────────────────┤
│                                                  │
│ Original Sentence:                               │
│ ┌─────────────────────────────────────────────┐ │
│ │ The system processes the data and stored   │ │
│ │ it in the database.                         │ │
│ └─────────────────────────────────────────────┘ │
│                                                  │
│ Detected Tense: Mixed (present + past)          │
│ Dominant Document Tense: Present                │
│                                                  │
│ Correct to:                                      │
│  ○ Past Tense                                   │
│  ● Present Tense (recommended)                  │
│  ○ Future Tense                                 │
│  ○ Keep As-Is (skip)                            │
│                                                  │
│ ☑ Fix grammar and punctuation                   │
│ ☑ Maintain technical terminology                │
│                                                  │
│         [Preview]  [Apply]  [Cancel]            │
└─────────────────────────────────────────────────┘
```

**Popup Requirements**
- Modal dialog (blocks interaction with main window)
- Position: Center of screen or near clicked sentence
- Minimum width: 500px
- Maximum height: Auto-adjust to content
- Escape key to cancel
- Enter key to apply (with selected option)

**Radio Button Options**
- Past Tense
- Present Tense (default to dominant tense with "recommended" label)
- Future Tense
- Keep As-Is (skip this correction)

**Optional Preview Button**
- Shows AI-generated correction before applying
- Displays in read-only text box within popup
- Allows user to review before committing

**Checkboxes for Correction Scope**
- ☑ Fix grammar and punctuation (default: checked)
- ☑ Maintain technical terminology (default: checked)
- ☑ Preserve markdown formatting (default: checked)

### 1.3 Batch Operations

**"Correct All" Button**
- Appears in tense analysis dialog
- Corrects all inconsistent sentences to dominant tense
- Shows progress bar/indicator during processing
- Allows cancellation mid-process

**"Review Changes" Button**
- Shows summary of all corrections made
- Side-by-side comparison:
  - Left: Original sentence (light red)
  - Right: Corrected sentence (light blue)
- Allows undo of individual corrections
- Shows total count of corrections

**"Undo Last Correction" Button**
- Reverts most recent sentence correction
- Changes sentence from blue back to red
- Maintains undo history (up to 10 corrections)

---

## 2. Technical Requirements

### 2.1 Sentence Detection & Tagging

**Sentence Boundary Detection**
```python
import nltk
from nltk.tokenize import sent_tokenize

# Must handle:
- Standard sentences ending in . ! ?
- Abbreviations (e.g., "Dr.", "Inc.", "etc.")
- Decimal numbers (e.g., "3.14")
- Multiple punctuation (e.g., "What?!")
- Quoted sentences
- List items
- Code blocks (should be excluded)
```

**Text Widget Tag System**
```python
# Tag structure:
{
    'inconsistent_1': {
        'start_index': '1.0',
        'end_index': '1.45',
        'sentence_text': "The system processes...",
        'detected_tense': 'mixed',
        'tag_name': 'tense_inconsistent_1',
        'status': 'uncorrected'  # or 'corrected', 'skipped'
    },
    ...
}
```

**Tag Configuration**
```python
# Inconsistent (red) tag
text_widget.tag_configure(
    'tense_inconsistent',
    background='#ffcccc',
    foreground='#000000',
    borderwidth=1,
    relief='solid'
)

# Corrected (blue) tag
text_widget.tag_configure(
    'tense_corrected',
    background='#cce5ff',
    foreground='#000000',
    borderwidth=1,
    relief='solid'
)

# Hover state
text_widget.tag_configure(
    'tense_hover',
    background='#ffaaaa'  # Darker red on hover
)
```

### 2.2 Click Event Handling

**Event Binding**
```python
# Bind click events to all inconsistent tags
for tag_name in inconsistent_tags:
    text_widget.tag_bind(tag_name, '<Button-1>',
                         lambda e, tag=tag_name: on_sentence_click(tag))
    text_widget.tag_bind(tag_name, '<Enter>',
                         lambda e, tag=tag_name: on_hover_enter(tag))
    text_widget.tag_bind(tag_name, '<Leave>',
                         lambda e, tag=tag_name: on_hover_leave(tag))
```

**Click Handler Requirements**
- Identify which sentence was clicked
- Retrieve sentence text and metadata
- Open popup dialog with pre-filled information
- Prevent multiple popups from opening simultaneously
- Handle edge cases (click on tag boundary, double-click, etc.)

### 2.3 AI Correction API

**Prompt Template for Single Sentence**
```python
prompt = f"""Rewrite the following sentence to use consistent {target_tense} tense.

IMPORTANT RULES:
1. Change ONLY the verb tenses and related time expressions
2. Fix grammar and punctuation ONLY if requested
3. Maintain ALL technical terminology exactly as written
4. Preserve markdown formatting (bold, italic, code, etc.)
5. Do NOT add, remove, or rearrange content
6. Do NOT change the meaning or intent

Original sentence:
{sentence_text}

Rewritten sentence in {target_tense} tense:"""
```

**API Call Requirements**
- Use existing `query_openwebui()` function
- Timeout: 30 seconds (shorter for single sentence)
- Model: Same as configured in settings
- Temperature: 0.1 (low for consistency)
- Max tokens: Estimate based on sentence length × 1.5

**Response Validation**
```python
def validate_correction(original, corrected, target_tense):
    """Validate AI-corrected sentence"""
    checks = {
        'not_empty': len(corrected.strip()) > 0,
        'not_too_long': len(corrected) < len(original) * 2,
        'not_too_short': len(corrected) > len(original) * 0.5,
        'starts_similar': similar_start(original, corrected),
        'ends_with_punctuation': corrected[-1] in '.!?',
        'no_extra_sentences': count_sentences(corrected) == 1
    }
    return all(checks.values()), checks
```

### 2.4 State Management

**Correction History Tracking**
```python
correction_history = {
    'corrections': [
        {
            'sentence_id': 'inconsistent_1',
            'original_text': "The system processes...",
            'corrected_text': "The system processed...",
            'target_tense': 'past',
            'timestamp': datetime.now(),
            'options_used': {
                'fix_grammar': True,
                'maintain_terminology': True,
                'preserve_formatting': True
            }
        },
        ...
    ],
    'undo_stack': [],  # For undo functionality
    'statistics': {
        'total_inconsistencies': 15,
        'corrected': 8,
        'skipped': 2,
        'remaining': 5
    }
}
```

**Persistence Requirements**
- Store corrections in memory during session
- Optional: Save to file for recovery (JSON format)
- Clear on document close or section change
- Warn user about unsaved corrections

---

## 3. Implementation Steps

### Phase 1: Text Widget Enhancement (Week 1)
1. ✅ Implement sentence boundary detection using NLTK
2. ✅ Create tag system for highlighting (red/blue)
3. ✅ Add click event handlers to tagged regions
4. ✅ Implement hover effects (color change, cursor)
5. ✅ Test tag overlapping and boundary cases

### Phase 2: Popup Dialog (Week 1-2)
1. ✅ Design popup UI with radio buttons and checkboxes
2. ✅ Implement modal dialog behavior
3. ✅ Add keyboard shortcuts (Enter, Escape)
4. ✅ Connect dialog to click events
5. ✅ Test dialog positioning and responsiveness

### Phase 3: AI Integration (Week 2)
1. ✅ Create single-sentence correction prompt template
2. ✅ Implement sentence-level `query_openwebui()` calls
3. ✅ Add response validation logic
4. ✅ Implement preview functionality (optional)
5. ✅ Add error handling and retry logic
6. ✅ Test with various sentence types

### Phase 4: Visual Feedback (Week 2-3)
1. ✅ Implement red → blue color transition
2. ✅ Add correction indicator icons (checkmark, pencil)
3. ✅ Optional: Fade animations for smooth transitions
4. ✅ Update sentence tags after correction
5. ✅ Test visual consistency across themes

### Phase 5: Batch Operations (Week 3)
1. ✅ Implement "Correct All" with progress tracking
2. ✅ Add cancellation support mid-process
3. ✅ Create "Review Changes" summary view
4. ✅ Implement undo/redo functionality
5. ✅ Test batch correction performance

### Phase 6: Integration & Polish (Week 3-4)
1. ✅ Integrate with existing "Analyze Tenses" function
2. ✅ Add to Tools menu and keyboard shortcuts
3. ✅ Create user documentation
4. ✅ Comprehensive testing (edge cases, errors, UX)
5. ✅ Performance optimization for large documents
6. ✅ Bug fixes and refinement

---

## 4. User Workflow

### Primary Workflow: Interactive Correction
```
1. User selects section → Clicks "Analyze Tenses"
2. Analysis runs → Inconsistent sentences highlighted in light red
3. User clicks red sentence → Popup appears
4. User selects tense (Past/Present/Future)
5. Optional: Click "Preview" to see correction
6. User clicks "Apply" → AI corrects sentence
7. Sentence changes from red → blue
8. Repeat for other sentences as desired
9. Click "Review Changes" to see summary
10. Click "Commit" to apply to document
```

### Alternative Workflow: Batch Correction
```
1. User selects section → Clicks "Analyze Tenses"
2. Analysis runs → Inconsistent sentences highlighted
3. User clicks "Correct All to [Dominant Tense]"
4. Progress bar shows correction status
5. All sentences corrected → Turn blue
6. User reviews changes in summary
7. User can undo individual corrections if needed
8. Click "Commit" to apply to document
```

### Edge Case Workflow: Mixed Corrections
```
1. User starts with interactive correction
2. Corrects 5 sentences individually
3. Clicks "Correct Remaining" for the rest
4. Reviews all changes together
5. Undoes 2 specific corrections
6. Re-corrects those 2 manually with different tense
7. Final review → Commit
```

---

## 5. Edge Cases & Error Handling

### 5.1 Sentence Detection Edge Cases
- **Abbreviations**: "Dr. Smith examined the data." → 1 sentence, not 2
- **Decimal Numbers**: "The value is 3.14." → 1 sentence
- **Code Blocks**: Should be excluded from analysis entirely
- **Bullet Points**: Each item treated as separate sentence
- **Quoted Sentences**: "He said, 'This works.' Then left." → 2 sentences
- **Multiple Punctuation**: "What?!" → End of sentence
- **No Ending Punctuation**: "This is incomplete" → Still treated as sentence

### 5.2 AI Correction Failures
- **Timeout**: Show error, offer retry or skip
- **Invalid Response**: Warn user, keep original
- **Response Too Different**: Warn user, show preview, require confirmation
- **Empty Response**: Error message, keep original
- **Network Error**: Queue for retry when connection restored

### 5.3 User Interaction Edge Cases
- **Rapid Clicking**: Prevent multiple popups, debounce clicks
- **Click During Correction**: Disable clicking while AI processing
- **Close Dialog Mid-Correction**: Cancel API request, revert to original
- **Document Changed**: Detect changes, warn about tag invalidation
- **Section Changed**: Ask to save corrections or discard

### 5.4 Tag Management Edge Cases
- **Overlapping Sentences**: Should not happen, but detect and warn
- **Tag Removed by User Edit**: Detect and remove from tracking
- **Sentence Modified by User**: Remove tags, re-run analysis
- **Copy-Paste Text**: Tags don't copy, explain to user

---

## 6. Performance Considerations

### 6.1 Scalability
- **Large Sections**: Max 50 sentences highlighted at once
- **Long Sentences**: Limit to 500 characters per sentence
- **Multiple Corrections**: Process sequentially, not in parallel (API limit)
- **Memory Usage**: Store only essential data per sentence

### 6.2 Optimization Strategies
- **Lazy Loading**: Only detect sentences when analysis runs
- **Tag Caching**: Cache sentence positions to avoid re-detection
- **Debouncing**: Wait 500ms after typing before re-analyzing
- **Background Processing**: Run AI corrections in threads
- **Progress Feedback**: Show progress bar for batch operations (every 10%)

### 6.3 API Rate Limiting
- **Sequential Requests**: 1 sentence at a time
- **Delay Between Requests**: 500ms minimum
- **Batch Size Limit**: Max 20 sentences per batch operation
- **Timeout Handling**: 30s per sentence, retry once on timeout
- **Fallback**: If API unavailable, queue corrections for later

---

## 7. Data Structures

### 7.1 Sentence Metadata
```python
@dataclass
class SentenceCorrection:
    id: str                    # Unique identifier
    start_index: str           # Text widget index (e.g., "1.0")
    end_index: str             # Text widget index (e.g., "1.45")
    original_text: str         # Original sentence text
    corrected_text: str | None # Corrected text (None if not corrected)
    detected_tense: str        # 'past', 'present', 'future', 'mixed'
    target_tense: str | None   # Selected tense for correction
    status: str                # 'pending', 'corrected', 'skipped', 'error'
    timestamp: datetime | None # When corrected
    tag_name: str              # Text widget tag name
    options: dict              # Correction options used
    error_message: str | None  # If correction failed
```

### 7.2 Correction Session
```python
@dataclass
class CorrectionSession:
    section: DocumentSection          # Section being corrected
    section_hash: str                 # Hash for tracking
    dominant_tense: str               # Most common tense
    consistency_score: float          # Original score (0-10)
    sentences: List[SentenceCorrection]  # All sentences
    statistics: dict                  # Correction stats
    undo_stack: List[SentenceCorrection] # For undo
    created_at: datetime
    modified_at: datetime
```

---

## 8. Testing Requirements

### 8.1 Unit Tests
- ✅ Sentence boundary detection (20+ test cases)
- ✅ Tag creation and removal
- ✅ Click event handling
- ✅ Tense detection accuracy
- ✅ AI response validation
- ✅ State management (corrections, undo)

### 8.2 Integration Tests
- ✅ Full workflow (analyze → correct → commit)
- ✅ Batch corrections
- ✅ Undo/redo functionality
- ✅ Error recovery
- ✅ Tag synchronization with text changes

### 8.3 UI/UX Tests
- ✅ Popup positioning on different screen sizes
- ✅ Color accessibility (color-blind friendly)
- ✅ Keyboard navigation
- ✅ Hover effects responsiveness
- ✅ Animation smoothness

### 8.4 Performance Tests
- ✅ 100+ sentences section
- ✅ Rapid clicking stress test
- ✅ Batch correction of 50 sentences
- ✅ Memory usage over extended session
- ✅ API timeout handling

---

## 9. Dependencies

### 9.1 Required Python Packages
```bash
# Already installed
- tkinter (standard library)
- requests

# New requirements
- nltk>=3.8  # For sentence tokenization
- python-docx>=0.8.11  # Already installed

# For enhanced features (optional)
- textblob>=0.17.1  # For better tense detection
- spacy>=3.5  # For advanced NLP (alternative to NLTK)
```

### 9.2 NLTK Data Files
```python
import nltk
nltk.download('punkt')  # Sentence tokenizer
nltk.download('averaged_perceptron_tagger')  # POS tagging
```

---

## 10. Configuration Options

### 10.1 User Settings
```python
TENSE_CORRECTION_CONFIG = {
    'highlight_colors': {
        'inconsistent': '#ffcccc',  # Light red
        'corrected': '#cce5ff',      # Light blue
        'hover': '#ffaaaa'           # Darker red
    },
    'correction_options': {
        'fix_grammar': True,         # Default checkbox state
        'maintain_terminology': True,
        'preserve_formatting': True
    },
    'batch_settings': {
        'max_sentences_per_batch': 20,
        'delay_between_requests_ms': 500,
        'show_progress_bar': True
    },
    'ui_preferences': {
        'popup_position': 'center',  # 'center' or 'near_cursor'
        'show_preview_button': True,
        'enable_animations': True,
        'animation_duration_ms': 300
    }
}
```

### 10.2 Advanced Settings (Hidden/Developer)
```python
ADVANCED_CONFIG = {
    'sentence_detection': {
        'min_sentence_length': 10,   # chars
        'max_sentence_length': 500,  # chars
        'exclude_code_blocks': True,
        'exclude_headings': False
    },
    'ai_correction': {
        'temperature': 0.1,
        'timeout_seconds': 30,
        'max_retries': 1,
        'validation_strict': True
    },
    'performance': {
        'max_sentences_to_highlight': 50,
        'lazy_load_corrections': True,
        'cache_sentence_positions': True
    }
}
```

---

## 11. Success Metrics

### 11.1 Functional Metrics
- ✅ Sentence detection accuracy > 98%
- ✅ Tag click response time < 100ms
- ✅ AI correction quality score > 8/10 (user rating)
- ✅ Correction preserves meaning > 99% of time
- ✅ Zero data loss during correction process

### 11.2 Performance Metrics
- ✅ Popup open time < 200ms
- ✅ Single sentence correction < 5 seconds
- ✅ Batch 20 sentences < 2 minutes
- ✅ Memory usage < 100MB for 100 sentences
- ✅ No UI freezing during operations

### 11.3 User Experience Metrics
- ✅ User can correct 1 sentence in < 10 seconds
- ✅ Visual feedback appears < 500ms after action
- ✅ Undo works 100% of time
- ✅ No more than 3 clicks per correction
- ✅ Error messages clear and actionable

---

## 12. Documentation Requirements

### 12.1 User Documentation
- ✅ Feature overview with screenshots
- ✅ Step-by-step tutorial (with GIF/video)
- ✅ Keyboard shortcuts reference
- ✅ Troubleshooting guide
- ✅ FAQ section

### 12.2 Developer Documentation
- ✅ Architecture diagram
- ✅ API reference for new functions
- ✅ Tag system explanation
- ✅ State management guide
- ✅ Testing guide

### 12.3 In-App Help
- ✅ Tooltip on first use
- ✅ Help button in popup dialog
- ✅ Context-sensitive help (F1 key)
- ✅ Example sentences with corrections

---

## 13. Future Enhancements (Post-V1)

### 13.1 AI-Powered Suggestions
- Suggest optimal tense based on context
- Auto-detect document style (formal/informal)
- Learn from user corrections (ML feedback loop)

### 13.2 Advanced Visualization
- Heatmap of tense distribution across document
- Timeline view of tense changes by section
- Diff view showing before/after side-by-side

### 13.3 Collaboration Features
- Track who made which corrections (multi-user)
- Comment system for questionable corrections
- Approval workflow for sensitive documents

### 13.4 Integration
- Export corrections log to CSV/JSON
- Integration with grammar checking tools (Grammarly, LanguageTool)
- Support for other languages beyond English

---

## 14. Risk Assessment

### 14.1 High Risk
- **AI hallucinations**: Correction changes meaning
  - *Mitigation*: Preview required, undo always available
- **Performance degradation**: Large documents slow down
  - *Mitigation*: Limit max sentences, lazy loading
- **Data loss**: Corrections lost on crash
  - *Mitigation*: Auto-save to temp file every 5 corrections

### 14.2 Medium Risk
- **User confusion**: Too many options in popup
  - *Mitigation*: Simple defaults, hide advanced options
- **Tag desynchronization**: Text edits break tags
  - *Mitigation*: Detect changes, warn user, re-run analysis
- **API rate limiting**: Too many requests
  - *Mitigation*: Sequential processing, delay between requests

### 14.3 Low Risk
- **Color accessibility**: Red/blue not visible to color-blind users
  - *Mitigation*: Add patterns/icons in addition to colors
- **Keyboard navigation**: Mouse-only interaction
  - *Mitigation*: Full keyboard support from start

---

## 15. Estimated Effort

### Development Time (Solo Developer)
- **Phase 1**: Text Widget Enhancement - 3-5 days
- **Phase 2**: Popup Dialog - 3-4 days
- **Phase 3**: AI Integration - 4-6 days
- **Phase 4**: Visual Feedback - 2-3 days
- **Phase 5**: Batch Operations - 4-5 days
- **Phase 6**: Integration & Polish - 5-7 days

**Total: 21-30 days (4-6 weeks)**

### Testing & Documentation
- **Testing**: 5-7 days
- **Documentation**: 3-4 days
- **Bug Fixes**: 3-5 days

**Grand Total: 32-46 days (6-9 weeks)**

---

## 16. Acceptance Criteria

### Must Have (V1.0)
- ✅ Click on red sentence → Popup appears
- ✅ Select tense → Sentence corrected → Turns blue
- ✅ Undo last correction works
- ✅ Batch "Correct All" works for ≤ 20 sentences
- ✅ No data loss during corrections
- ✅ Works on Windows, macOS, Linux

### Should Have (V1.1)
- ✅ Preview before applying correction
- ✅ Review Changes summary view
- ✅ Keyboard shortcuts (Enter, Escape, Ctrl+Z)
- ✅ Progress bar for batch operations
- ✅ Error recovery (retry, skip)

### Nice to Have (V2.0)
- ✅ Fade animations red → blue
- ✅ Checkmark/pencil icons on corrected sentences
- ✅ Export corrections log
- ✅ Persistent correction history across sessions
- ✅ Multi-language support

---

## 17. Rollout Plan

### Alpha Release (Internal Testing)
- Core functionality only (click → popup → correct)
- Limited to 10 sentences per section
- Manual testing by development team
- Gather feedback on UX flow

### Beta Release (Selected Users)
- Add batch operations and undo
- Increase limit to 50 sentences
- Beta testers provide feedback
- Fix critical bugs, refine UI

### V1.0 Release (Public)
- Full feature set as per "Must Have"
- Comprehensive documentation
- Performance optimizations complete
- Announce via release notes

### V1.1+ (Iterative Improvements)
- Add "Should Have" and "Nice to Have" features
- Performance enhancements based on usage data
- User-requested features

---

## Appendix A: UI Mockups

### Tense Analysis View with Highlighting
```
┌────────────────────────────────────────────────────────┐
│ Section: Introduction > Background                      │
├────────────────────────────────────────────────────────┤
│                                                         │
│ The system [processes the data]🔴 and provides real-   │
│ time insights. It [was designed]🔴 to handle large     │
│ datasets. Users [can access]✅ the dashboard to view   │
│ analytics.                                              │
│                                                         │
│ Legend: 🔴 Needs correction  ✅ Corrected              │
│                                                         │
│ [Correct All]  [Review Changes]  [Close]               │
└────────────────────────────────────────────────────────┘

Legend:
  [text]🔴 = Light red background (inconsistent)
  [text]✅ = Light blue background (corrected)
```

### Sentence Correction Popup
```
┌─────────────────────────────────────────────────────┐
│ Correct Sentence Tense                              │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Original:                                            │
│ ┌──────────────────────────────────────────────────┐│
│ │ The system processes the data and stored it in  ││
│ │ the database for future analysis.                ││
│ └──────────────────────────────────────────────────┘│
│                                                      │
│ Issues: Mixed tense (present "processes" + past     │
│         "stored")                                    │
│                                                      │
│ Correct to:                                          │
│  ○ Past: "The system processed the data and stored  │
│           it..."                                     │
│  ● Present: "The system processes the data and      │
│             stores it..." (recommended)              │
│  ○ Future: "The system will process the data and    │
│            will store it..."                         │
│  ○ Keep original (skip)                             │
│                                                      │
│ Options:                                             │
│  ☑ Fix grammar & punctuation                        │
│  ☑ Maintain technical terms                         │
│                                                      │
│         [Preview]     [Apply]     [Cancel]          │
└─────────────────────────────────────────────────────┘
```

---

## Appendix B: Technical Architecture

### Component Diagram
```
┌─────────────────────────────────────────────────────┐
│ DocumentFiller5 Application                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │ TenseAnalysisManager                       │    │
│  │  - analyze_section()                       │    │
│  │  - highlight_inconsistencies()             │    │
│  │  - manage_correction_session()             │    │
│  └──────────┬─────────────────────────────────┘    │
│             │                                        │
│             ├─ SentenceDetector                     │
│             │   - detect_boundaries()               │
│             │   - tokenize_text()                   │
│             │                                        │
│             ├─ SentenceTagManager                   │
│             │   - create_tags()                     │
│             │   - update_tag_color()                │
│             │   - handle_click_events()             │
│             │                                        │
│             ├─ TenseCorrectionDialog                │
│             │   - show_popup()                      │
│             │   - get_user_selection()              │
│             │   - preview_correction()              │
│             │                                        │
│             ├─ AICorrectionEngine                   │
│             │   - correct_sentence()                │
│             │   - validate_response()               │
│             │   - handle_errors()                   │
│             │                                        │
│             └─ CorrectionSessionManager             │
│                 - track_corrections()               │
│                 - undo/redo()                        │
│                 - generate_summary()                │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Data Flow
```
User Action → Event Handler → State Update → UI Refresh
     ↓              ↓              ↓              ↓
  Click red    on_sentence_   Update           Repaint
  sentence     click()        sentence         widget with
                              metadata         blue tag
                                 ↓
                            Call AI API
                            (query_openwebui)
                                 ↓
                            Validate
                            response
                                 ↓
                            Store in
                            history
```

---

## Conclusion

This requirements document provides a comprehensive blueprint for implementing the interactive tense correction feature. The estimated effort is **6-9 weeks** for a complete implementation including testing and documentation.

**Next Steps:**
1. Review and approve requirements
2. Break down into GitHub issues/tasks
3. Set up development environment (NLTK, etc.)
4. Begin Phase 1 implementation
5. Iterate based on user feedback

**Key Success Factors:**
- Robust sentence detection (NLTK)
- Responsive UI (no freezing)
- Reliable AI corrections (validation)
- Clear visual feedback (colors, animations)
- Comprehensive error handling
