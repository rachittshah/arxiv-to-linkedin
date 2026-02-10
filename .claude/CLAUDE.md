# arxiv-to-linkedin

Pipeline to extract arxiv papers using docling and generate LinkedIn posts.

## Project Structure
- `src/arxiv_to_linkedin/extract.py` — Docling-based paper extraction (PDF → markdown + images + tables)
- `.claude/skills/arxiv-to-linkedin.md` — Main skill for generating LinkedIn posts from papers
- `output/` — Generated extractions and posts (gitignored)

## Commands
- Extract paper: `uv run python src/arxiv_to_linkedin/extract.py <arxiv_url_or_id> [output_dir]`

## Conventions
- Use `uv run` for all Python commands
- Output files go to `output/<arxiv_id>/`
- LinkedIn posts follow Rachit's writing style (see skill file for template)
