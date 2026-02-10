# /arxiv-to-linkedin - Generate LinkedIn Post from arXiv Paper

Extract an arXiv paper using docling and generate a LinkedIn post + summary + open questions, using a team of Opus 4.6 agents.

## Usage

```
/arxiv-to-linkedin <arxiv_url_or_id>
```

## Instructions

When this skill is invoked with an arxiv URL or paper ID:

### Phase 1: Extract the Paper

Run the docling extraction script to pull all content from the paper:

```bash
cd /Users/rshah/arxiv-to-linkedin && uv run python src/arxiv_to_linkedin/extract.py "<arxiv_url_or_id>" output
```

This produces:
- `output/<paper_id>/extraction.json` — metadata, sections, tables, figures
- `output/<paper_id>/content.md` — full markdown extraction
- `output/<paper_id>/figure_*.png` — extracted images

Read the extraction.json and content.md files to get the paper content.

### Phase 2: Launch Agent Team

Create a team called `arxiv-post` with 3 agents, ALL using `model: "opus"`:

#### Agent 1: `paper-analyst` (general-purpose, mode: bypassPermissions)
Task: Read the extracted paper content (content.md and extraction.json) and produce a structured analysis:
- **One-line summary**: What is this paper about in plain English?
- **Key innovation**: What's new/different about this approach?
- **Core results**: Top 3-5 quantitative results or claims
- **Practical applications**: 5-7 real-world use cases (think like a VC — what can you build with this?)
- **Technical highlights**: Architecture, method, or approach details for the "geek section"
- **Limitations/Open questions**: 3-5 open questions or limitations
- **Who should care**: Target audience beyond academics

Save analysis to `output/<paper_id>/analysis.json`.

#### Agent 2: `post-writer` (general-purpose, mode: bypassPermissions)
Task: Wait for paper-analyst to complete (use task dependency). Then read the analysis and generate a LinkedIn post following Rachit's EXACT writing style.

**Rachit's LinkedIn Post Template:**

```
🚀 <Catchy Title> - <Source/Lab if notable>

<Personal hook — 1-2 sentences. Start with "I" or a conversational observation. Show genuine curiosity. Examples: "I keep looking out for...", "This caught my eye...", "Been thinking about...">

📄 Paper: <Title> on arXiv (<arxiv_url>)
---
🌍 What is <Short Name>?

<2-3 paragraphs explaining the paper in accessible language. No jargon walls. Use concrete numbers. End with the "best part" or a standout detail.>

<If there's a public dataset/tool/demo, link it here with 👉>

---
🛠 Why does this matter? (<fun parenthetical like "weekend project?">)

<Context for why someone should care. Frame through practical lens — what can you BUILD with this?>

<Bullet list of 5-7 concrete applications. Start each with a verb. Be specific to real places/problems.>

In short, <one-line elevator pitch metaphor — "it's like having a...">.
---
🔧 For the Geeks
<Technical quickstart — how to try it. Link to docs/code.>
<One-liner vision statement about the broader impact.>
---
Further reading:
1. <link>
2. <link>
---

Authors: <Full author list from paper>
```

**Style rules:**
- Use emoji section headers: 🚀 📄 🌍 🛠 🔧
- Use `---` as section dividers
- Keep paragraphs SHORT (2-4 sentences max)
- Bullet points for applications (verb-first)
- Conversational tone — write like you're telling a smart friend about it
- Include the "weekend project?" or similar playful parenthetical
- End the "Why does this matter" section with an "In short, it's like..." metaphor
- Always include the full author list at the end
- Link to the arxiv paper, any public tools/datasets, and quickstart docs

Save post to `output/<paper_id>/linkedin_post.md`.

#### Agent 3: `summarizer` (general-purpose, mode: bypassPermissions)
Task: Wait for paper-analyst to complete (use task dependency). Then generate:
1. **Executive Summary** (200-300 words): Dense technical summary for someone who wants the gist without reading the paper
2. **Open Questions** (5-7 questions): Thought-provoking questions that the paper raises but doesn't fully answer. Mix of:
   - Technical gaps ("How does this scale to...?")
   - Practical concerns ("What happens when...?")
   - Broader implications ("Could this be applied to...?")
   - VC/builder lens ("What would a startup built on this look like?")

Save to `output/<paper_id>/summary_and_questions.md`.

### Phase 3: Assemble Final Output

After all agents complete, read all three output files and present the final deliverable to the user:

```
═══════════════════════════════════════
📝 LINKEDIN POST
═══════════════════════════════════════
<contents of linkedin_post.md>

═══════════════════════════════════════
📋 EXECUTIVE SUMMARY
═══════════════════════════════════════
<contents of summary section>

═══════════════════════════════════════
❓ OPEN QUESTIONS
═══════════════════════════════════════
<contents of open questions section>

═══════════════════════════════════════
📁 All files saved to: output/<paper_id>/
═══════════════════════════════════════
```

### Phase 4: Cleanup

Shut down all team agents and delete the team with TeamDelete.

## Options

- If the user provides just an arxiv ID (e.g., `2501.12345`), treat it as `https://arxiv.org/abs/2501.12345`
- If extraction fails, try downloading the PDF directly and converting
- The output directory persists between runs — each paper gets its own subdirectory

## Examples

```
/arxiv-to-linkedin https://arxiv.org/abs/2501.12345
/arxiv-to-linkedin 2501.12345
/arxiv-to-linkedin https://arxiv.org/pdf/2501.12345
```

## Implementation Notes

- Docling handles PDF → structured content extraction (text, tables, images)
- arxiv Python library fetches metadata (title, authors, abstract, categories)
- Agent team runs on Opus 4.6 for highest quality analysis and writing
- All outputs are saved to `output/<paper_id>/` for reuse
