# arxiv-to-linkedin

Turn any arXiv paper into a LinkedIn post, executive summary, and open questions — using [docling](https://github.com/DS4SD/docling) for PDF extraction and a team of Claude Opus 4.6 agents for analysis and writing.

Built as a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill.

## What it does

```
/arxiv-to-linkedin https://arxiv.org/abs/2602.01313
```

1. **Extracts** the full paper with docling (text, tables, figures, images)
2. **Analyzes** the paper with a dedicated agent (key findings, applications, technical details)
3. **Writes** a LinkedIn post matching your writing style
4. **Generates** an executive summary + open questions

All three agents run on Opus 4.6 and work in parallel where possible.

### Output

```
output/<paper_id>/
  ├── content.md              # Full paper markdown
  ├── extraction.json         # Metadata, sections, tables, figures
  ├── analysis.json           # Structured paper analysis
  ├── linkedin_post.md        # Ready-to-post LinkedIn content
  ├── summary_and_questions.md # Executive summary + open questions
  ├── <paper_id>.pdf          # Downloaded PDF
  └── figure_*.png            # Extracted images
```

## Setup

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- [uv](https://docs.astral.sh/uv/) package manager
- Python 3.11+

### Install

```bash
git clone https://github.com/rachittshah/arxiv-to-linkedin.git
cd arxiv-to-linkedin
uv sync
```

### Register the skill with Claude Code

Copy or symlink the skill into your Claude Code skills directory:

```bash
# Option 1: Symlink (recommended — stays in sync with repo)
mkdir -p ~/.claude/skills
ln -s "$(pwd)/.claude/skills/arxiv-to-linkedin.md" ~/.claude/skills/arxiv-to-linkedin.md

# Option 2: Project-local (skill available only when cd'd into this project)
# Already set up — just run Claude Code from this directory
```

### Verify

```bash
# Check dependencies are installed
uv run python -c "from docling.document_converter import DocumentConverter; print('docling OK')"

# Test extraction standalone
uv run python src/arxiv_to_linkedin/extract.py 2602.01313 output
```

## Usage

### Via Claude Code skill (recommended)

```bash
cd ~/arxiv-to-linkedin
claude

# Then in Claude Code:
/arxiv-to-linkedin https://arxiv.org/abs/2602.01313
/arxiv-to-linkedin 2501.12345
/arxiv-to-linkedin https://arxiv.org/pdf/2501.12345
```

This launches a 3-agent team:

| Agent | Role | Output |
|-------|------|--------|
| `paper-analyst` | Reads extracted content, produces structured analysis | `analysis.json` |
| `post-writer` | Generates LinkedIn post in your writing style | `linkedin_post.md` |
| `summarizer` | Creates executive summary + open questions | `summary_and_questions.md` |

### Standalone extraction (no agents)

```bash
uv run python src/arxiv_to_linkedin/extract.py <arxiv_url_or_id> [output_dir]
```

## Customizing the writing style

The LinkedIn post template lives in `.claude/skills/arxiv-to-linkedin.md`. Edit the template under "Rachit's LinkedIn Post Template" to match your own style. Key elements:

- **Section structure**: Emoji headers, `---` dividers
- **Tone**: Conversational, VC lens, "telling a smart friend"
- **Sections**: Hook, "What is it?", "Why does it matter?", "For the Geeks", Further reading, Authors

## Architecture

```
┌─────────────────┐
│  arxiv URL/ID   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     docling + arxiv API
│    extract.py   │────► PDF → markdown, tables, images, metadata
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│           Claude Code Team              │
│                                         │
│  ┌──────────────┐                       │
│  │paper-analyst │──► analysis.json      │
│  └──────┬───────┘                       │
│         │ (dependency)                  │
│    ┌────┴────┐                          │
│    ▼         ▼                          │
│ ┌────────┐ ┌──────────┐                │
│ │post-   │ │summarizer│                │
│ │writer  │ │          │                │
│ └───┬────┘ └────┬─────┘                │
│     │           │                       │
│     ▼           ▼                       │
│ linkedin_   summary_and_               │
│ post.md     questions.md               │
└─────────────────────────────────────────┘
```

## Stack

- **[docling](https://github.com/DS4SD/docling)** — PDF to structured content extraction
- **[arxiv](https://pypi.org/project/arxiv/)** — Paper metadata from arxiv API
- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** — Agent orchestration via skills and teams
- **[uv](https://docs.astral.sh/uv/)** — Python package management
