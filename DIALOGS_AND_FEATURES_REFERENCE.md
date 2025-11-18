# DocumentFiller: Dialogs and Features Quick Reference

## Visual Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│           DocumentFiller Main Window (1400x900)                  │
├──────────────┬──────────────────────────────────────────────────┤
│   MENU BAR   │ File | Edit | Section | Document | Tools | View  │
├──────────────┼──────────────────────────────────────────────────┤
│              │                                                    │
│              │  ┌─────── PREVIEW TAB ───────┐                   │
│ LEFT PANEL   │  │ Existing  │  Generated    │                   │
│ (Controls)   │  │ Content   │  Content      │                   │
│              │  │ (Read)    │  (Editable)   │                   │
│              │  │───────────┼──────────────│                   │
│ • Load Doc   │  │ [Commit] [Clear] [Export]                    │
│ • Configure  │  │                          │                   │
│ • Op Mode    │  │  ┌─────── PROMPT TAB ────┐                  │
│ • Generate   │  │  │ [Last Sent Prompt]    │                  │
│ • Review     │  │  │                       │                  │
│ • Tense      │  │  │ [Regenerate] [Compare]                  │
│ • etc...     │  │  └───────────────────────┘                  │
│              │  │                                                │
│              │  │  ┌─────── CONSOLE TAB ───┐                  │
│ • Manage     │  │  │ [Status Messages]      │                  │
│   Prompts    │  │  │ [Log Output]           │                  │
│ • Settings   │  │  └───────────────────────┘                  │
│              │  │                                                │
│              │  │  ┌────── HISTORY TAB ────┐                  │
│              │  │  │ [Prompt History]       │                  │
│              │  │  └───────────────────────┘                  │
│              │  │                                                │
│              │  │  ┌────── CHAT TAB ───────┐                  │
│              │  │  │ [Section Chat]         │                  │
│              │  │  └───────────────────────┘                  │
│              │                                                    │
└──────────────┴──────────────────────────────────────────────────┘
```

---

## Dialogs by Category

### A. Configuration & Settings Dialogs

#### 1. Configuration Dialog (Ctrl+Shift+C)
```
DIALOG: OpenWebUI Configuration
┌─────────────────────────────────────────┐
│ OpenWebUI Configuration                 │
├─────────────────────────────────────────┤
│ Connection:                             │
│  Base URL: [http://172.16.27.122:3000] │
│  API Key: [***hidden***]                │
│ [Test Connection] [Refresh]             │
│                                         │
│ Model Selection:                        │
│  [Model 1 ▼] [Refresh Models]          │
│                                         │
│ Generation Parameters:                  │
│  Temperature: [0.1] (0.0 - 2.0)        │
│  Max Tokens: [8000]                    │
│                                         │
│ Knowledge Collections:                  │
│  ☑ USMC        ☑ NIST                  │
│  ☑ DoD         ☑ CCI                   │
│  [Refresh Collections]                  │
│                                         │
│ [Load] [Save] [Reset] [Save] [Cancel]  │
└─────────────────────────────────────────┘
```

#### 2. Auto Features Dialog
```
DIALOG: Auto Features Configuration
┌──────────────────────────────────┐
│ Auto Features                    │
├──────────────────────────────────┤
│ ☑ Auto-Backup                   │
│   Interval: [5] minutes          │
│                                  │
│ ☑ Auto-Save                      │
│                                  │
│ ☑ Auto-Reload                    │
│                                  │
│ ☑ Ask Before Backup              │
│                                  │
│ [Save] [Cancel]                  │
└──────────────────────────────────┘
```

#### 3. Formatting Options Dialog
```
DIALOG: Text Formatting Configuration
┌──────────────────────────────────┐
│ Formatting Options               │
├──────────────────────────────────┤
│ Highlighting:                    │
│  ☑ Enable                        │
│    Color: [Yellow ▼]             │
│    [Pick Color]                  │
│                                  │
│ Text Styling:                    │
│  ☐ Bold                          │
│  ☐ Italic                        │
│  ☐ Underline                     │
│                                  │
│ Font:                            │
│  Color: [#000000] [Pick]         │
│  Size: [11] pt                   │
│                                  │
│ [Save] [Cancel]                  │
└──────────────────────────────────┘
```

#### 4. Config File Manager Dialog
```
DIALOG: Configuration File Manager
┌──────────────────────────────────┐
│ Configuration Files              │
├──────────────────────────────────┤
│ Current: openwebui_config.json   │
│                                  │
│ [Load Configuration...]          │
│ [Save Configuration As...]       │
│ [Reset to Defaults]              │
│                                  │
│ [Save] [Cancel]                  │
└──────────────────────────────────┘
```

---

### B. Feature-Specific Dialogs

#### 5. Prompt Manager Dialog
```
DIALOG: Prompt Manager
┌────────────────────────────────────────┐
│ Manage Prompts                         │
├────────────────────────────────────────┤
│ Saved Prompts:                         │
│ ┌────────────────────────────────────┐ │
│ │ • DoD Cybersecurity Prompt         │ │
│ │ • FedRAMP Compliance Prompt        │ │
│ │ • NIST RMF Prompt                  │ │
│ │ • Custom Research Prompt           │ │
│ └────────────────────────────────────┘ │
│ [Add New] [Import] [Remove]            │
│                                        │
│ Editor:                                │
│ ┌────────────────────────────────────┐ │
│ │ [Prompt text here...]              │ │
│ └────────────────────────────────────┘ │
│ [Save Changes] [Make Master]           │
│ [Save to Library]                      │
│                                        │
│ [Reset to Default] [Close]             │
└────────────────────────────────────────┘
```

#### 6. Tense Fix Dialog (appears after tense analysis)
```
DIALOG: Fix Tense Issues
┌──────────────────────────────────┐
│ Fix Tense Issues                 │
├──────────────────────────────────┤
│ Scope: ◉ Section ○ Document      │
│                                  │
│ Target Tense:                    │
│  [📖 Fix to Past]                │
│  [📝 Fix to Present]             │
│  [🔮 Fix to Future]              │
│                                  │
│ [Close]                          │
└──────────────────────────────────┘
```

#### 7. Processing Strategy Dialog
```
DIALOG: Processing Strategy Analysis
┌──────────────────────────────────────┐
│ Processing Strategy                  │
├──────────────────────────────────────┤
│ Strategy: RAG (Retrieval)             │
│ Reason: Large document with context  │
│                                      │
│ Details:                             │
│ • Token Estimate: 2,450 / 8,000      │
│ • Chunks: 5                          │
│ • Confidence: 8.5/10                 │
│                                      │
│ Recommendation: Use selected         │
│ knowledge collections for context.   │
│                                      │
│ [Close]                              │
└──────────────────────────────────────┘
```

#### 8. Model Comparison Window
```
DIALOG: Compare 3 Models
┌─────────────────────────────────────────────────────┐
│ Model Comparison                                    │
├─────────────────────────────────────────────────────┤
│ Select 3 Models:                                    │
│  ☑ llama3.1:latest    ☐ mistral    ☐ neural-chat  │
│  ☑ dolphin           ☐ orca       ☐ neural-chat   │
│  ☑ llama2            ☐ neural     ☐ orca          │
│                                                    │
│  [Generate Comparison]                             │
│                                                    │
│ ┌─────────────┬─────────────┬─────────────┐       │
│ │  Model 1    │  Model 2    │  Model 3    │       │
│ │  (Result)   │  (Result)   │  (Result)   │       │
│ ├─────────────┼─────────────┼─────────────┤       │
│ │  [Select]   │  [Select]   │  [Select]   │       │
│ └─────────────┴─────────────┴─────────────┘       │
│                                                    │
│ [Update Master Prompt] [Cancel]                   │
└─────────────────────────────────────────────────────┘
```

#### 9. Auto-Complete Progress Window
```
DIALOG: Auto-Complete Document Progress
┌────────────────────────────────────────┐
│ Auto-Complete Progress                 │
├────────────────────────────────────────┤
│ Overall Progress: ████████░░░░░░░░░░   │
│ (42/100 sections completed)            │
│                                        │
│ Current Section: Section 4.2           │
│ Status: Generating...                  │
│                                        │
│ Sections:                              │
│ ┌────────────────────────────────────┐ │
│ │ ✓ Introduction                     │ │
│ │ ✓ Background                       │ │
│ │ ✓ Methodology                      │ │
│ │ ⟳ Section 4.1                      │ │
│ │ ⟳ Section 4.2 (current)            │ │
│ │ ○ Section 4.3                      │ │
│ │ ○ Results                          │ │
│ │ ○ Conclusion                       │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Live Log:                              │
│ ┌────────────────────────────────────┐ │
│ │ Generating "Introduction"...       │ │
│ │ ✓ Introduction completed           │ │
│ │ Generating "Background"...         │ │
│ └────────────────────────────────────┘ │
│                                        │
│ [Pause] [Stop] [Close]                 │
└────────────────────────────────────────┘
```

#### 10. External RAG Content Manager
```
DIALOG: External RAG Content Manager
┌───────────────────────────────────────────┐
│ External RAG Content                      │
├───────────────────────────────────────────┤
│ Content Library:                          │
│ ┌───────────────────────────────────────┐ │
│ │ [Title] - [Category] - [Date]         │ │
│ │ [Content snippet...]                  │ │
│ ├───────────────────────────────────────┤ │
│ │ [More content...]                     │ │
│ └───────────────────────────────────────┘ │
│                                           │
│ [Add New Content]                         │
│ [Import from File]                        │
│                                           │
│ Actions on Selected:                      │
│ [View Details] [Edit] [Delete]            │
│                                           │
│ [Close]                                   │
└───────────────────────────────────────────┘
```

#### 11. Credentials Manager Dialog
```
DIALOG: Credentials Manager
┌──────────────────────────────────┐
│ Credentials Manager              │
├──────────────────────────────────┤
│ Master Password:                 │
│  ☑ Encrypted                     │
│                                  │
│ [Set/Change Password]            │
│ [Enable Encryption]              │
│                                  │
│ Credential Actions:              │
│  [Load From File]                │
│  [Save to File]                  │
│  [Backup Credentials]            │
│                                  │
│ [Save] [Cancel]                  │
└──────────────────────────────────┘
```

---

### C. Help & Info Dialogs

#### 12. About Dialog
```
DIALOG: About
┌────────────────────────────────────┐
│ Document Content Generator         │
├────────────────────────────────────┤
│ Version: 5.0                       │
│                                    │
│ OpenWebUI Integration              │
│ Automatically fills Word document  │
│ sections using OpenWebUI/Ollama    │
│ with RAG support                   │
│                                    │
│ Features:                          │
│ • Markdown conversion              │
│ • Prompt learning                  │
│ • Auto-features                    │
│ • Model comparison                 │
│                                    │
│ DoD Compliance Ready               │
│ NIST | RMF | FedRAMP               │
│                                    │
│ [OK]                               │
└────────────────────────────────────┘
```

#### 13. Keyboard Shortcuts Dialog
```
DIALOG: Keyboard Shortcuts
┌──────────────────────────────────┐
│ Keyboard Shortcuts               │
├──────────────────────────────────┤
│ File Operations:                 │
│  Ctrl+O  - Load Document         │
│  Ctrl+R  - Reload Document       │
│  Ctrl+S  - Save As               │
│  Ctrl+Q  - Exit                  │
│                                  │
│ Content Generation:              │
│  Ctrl+G  - Generate Content      │
│  Ctrl+P  - Manage Prompts        │
│  Ctrl+Shift+R - Review Section   │
│  Ctrl+Shift+D - Review Document  │
│  Ctrl+Shift+A - Auto-Complete    │
│  Ctrl+Shift+C - Configure AI     │
│                                  │
│ [Close]                          │
└──────────────────────────────────┘
```

---

## Menu Command Reference

### File Menu (6 Commands)
- Load Document... (Ctrl+O)
- Reload Document (Ctrl+R)
- Save Document As... (Ctrl+S)
- Load Configuration...
- Save Configuration As...
- Exit (Ctrl+Q)

### Edit Menu (4 Commands)
- Manage Prompts... (Ctrl+P)
- Config Files...
- Formatting Options...
- Auto Features...

### Section Menu (7 Commands)
- Generate Content (Ctrl+G)
- Review Section (Ctrl+Shift+R)
- Analyze Tenses
- Check & Fix Tenses
- Apply Suggestions
- Regenerate Review
- Processing Strategy...

### Document Menu (4 Commands)
- Review Whole Document (Ctrl+Shift+D)
- Check & Fix Document Tenses
- Auto Complete Document (Ctrl+Shift+A)
- Processing Strategy...

### Tools Menu (3 Commands)
- Configure AI... (Ctrl+Shift+C)
- Credentials Manager...
- External RAG Content...

### View Menu (5 Commands)
- Preview Tab
- Prompt Tab
- Console Tab
- Prompt History Tab
- Section Chat Tab

### Help Menu (2 Commands)
- About
- Keyboard Shortcuts

---

## Control Panel Button Reference

### Document Controls (2 Buttons)
1. Load - Opens file browser to select DOCX file
2. Reload - Reloads currently open document

### Configuration (3 Buttons)
1. Configure AI - Opens full configuration dialog
2. External RAG - Opens RAG content manager
3. Credentials - Opens credentials/encryption manager

### Operation Mode (3 Radio Buttons)
1. Replace - Generate content from scratch
2. Rework - Enhance existing content
3. Append - Add to existing content

### Section Controls (7 Buttons)
1. Generate Content - Create new section content
2. 📝 Review - Technical review analysis
3. 🎯 Analyze Tenses - Check tense consistency
4. ✏️ Check & Fix Tenses - Analyze and fix
5. ✅ Apply Suggestions - Apply review feedback
6. 🔄 Regenerate - Create new version from review
7. 🧠 Processing Strategy - Show RAG/full analysis

### Document Controls (4 Buttons)
1. 📋 Review Document - Review all sections
2. ✏️ Check & Fix Tenses - Fix document tenses
3. 🚀 Auto Complete - Batch generate sections
4. 🧠 Processing Strategy - Document-level analysis

### Utilities (4 Buttons)
1. 📚 Manage Prompts - Prompt library
2. ⚙ Config Files - Load/save configurations
3. ⚙ Formatting - Text formatting options
4. 🔄 Auto Features - Auto-save/backup settings

---

## Right Panel Tabs

### Tab 1: Preview
- **Left Column:** Existing content (read-only)
- **Right Column:** Generated content (editable)
- **Buttons:** Commit, Clear, Export
- **Purpose:** Review and edit generated content before committing

### Tab 2: Prompt
- **Content:** Last sent prompt to API
- **Buttons:** Regenerate, Compare 3 Models, Update Master Prompt
- **Purpose:** Review, modify, and test prompts

### Tab 3: Console
- **Content:** Real-time status messages and logs
- **Auto-scroll:** Latest messages at bottom
- **Purpose:** Monitor generation and review progress

### Tab 4: Prompt History
- **Content:** Log of all previous prompts and responses
- **Buttons:** Clear History, Export History
- **Features:** Searchable, timestamped entries
- **Purpose:** Learn from successful prompts and track changes

### Tab 5: Section Chat
- **Content:** Conversation history for current section
- **Input:** Chat message field
- **Button:** Send
- **Purpose:** Interactive Q&A about section content

---

## Configuration Settings Summary

### OpenWebUI Settings
- Base URL: Server endpoint (default: http://172.16.27.122:3000)
- API Key: Authentication token
- Selected Model: Active LLM model
- Temperature: Generation randomness (0.0-2.0, default: 0.1)
- Max Tokens: Response length limit (default: 8000)
- Knowledge Collections: RAG data sources to use

### Format Settings
- Highlight: Enable/disable, color choice
- Bold/Italic/Underline: Text styling toggles
- Font Color: RGB hex value
- Font Size: Point size (default: 11)

### Auto Features
- Auto-Backup: Enable automatic backups (default: enabled)
- Backup Interval: Minutes between backups (default: 5)
- Auto-Save: Save document after commit (default: disabled)
- Auto-Reload: Reload document after save (default: enabled)
- Ask Before Backup: Prompt user for confirmation (default: enabled)

---

## Modal Dialog Tracking

The application prevents duplicate dialog windows using modal tracking:
- Each dialog is registered when opened
- Opening same dialog again brings existing window to front
- Closing dialog removes it from tracking
- Prevents accidental multiple instances of same dialog

---

## File Operations

### File Types Supported
- DOCX (Word documents) - primary format
- JSON (configuration files)
- ENC (encrypted credentials)
- TXT (prompts, exports)
- MD (markdown exports)

### Common File Operations
- Load Document → Browse for .docx file
- Save As → Save with new name/location
- Load Config → Import configuration from file
- Export Prompt History → Save to .txt or .md
- Add External Content → Import from file

---

## Summary

DocumentFiller provides a comprehensive set of dialogs and controls for:
- **13 major dialogs** for configuration, features, and settings
- **36 menu commands** organized across 7 menus
- **23 main control buttons** plus radio options
- **5 tabbed interfaces** for different workflows
- **3+ configuration categories** with 15+ total settings

All dialogs follow consistent dark theme styling and support keyboard shortcuts where applicable.

