"""Extract content from arxiv papers using docling."""

import json
import re
import sys
import tempfile
from pathlib import Path

import arxiv
import requests
from docling.document_converter import DocumentConverter


def resolve_arxiv_url(url_or_id: str) -> tuple[str, str]:
    """Resolve an arxiv URL or ID to a PDF URL and paper ID."""
    # Extract arxiv ID from various URL formats
    patterns = [
        r"arxiv\.org/abs/(\d+\.\d+(?:v\d+)?)",
        r"arxiv\.org/pdf/(\d+\.\d+(?:v\d+)?)",
        r"^(\d+\.\d+(?:v\d+)?)$",
    ]
    arxiv_id = None
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            arxiv_id = match.group(1)
            break

    if not arxiv_id:
        raise ValueError(f"Could not extract arxiv ID from: {url_or_id}")

    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    return pdf_url, arxiv_id


def fetch_arxiv_metadata(arxiv_id: str) -> dict:
    """Fetch paper metadata from arxiv API."""
    clean_id = arxiv_id.split("v")[0]  # Remove version suffix
    client = arxiv.Client()
    search = arxiv.Search(id_list=[clean_id])
    results = list(client.results(search))

    if not results:
        raise ValueError(f"No paper found for arxiv ID: {arxiv_id}")

    paper = results[0]
    return {
        "title": paper.title,
        "authors": [a.name for a in paper.authors],
        "summary": paper.summary,
        "published": paper.published.isoformat(),
        "updated": paper.updated.isoformat() if paper.updated else None,
        "categories": paper.categories,
        "primary_category": paper.primary_category,
        "pdf_url": paper.pdf_url,
        "arxiv_url": paper.entry_id,
        "doi": paper.doi,
        "comment": paper.comment,
    }


def extract_paper(url_or_id: str, output_dir: str = "output") -> dict:
    """
    Extract full paper content using docling.

    Returns a dict with:
    - metadata: arxiv API metadata
    - content: full extracted text (markdown)
    - sections: list of section headers and content
    - tables: extracted tables
    - figures: figure references and captions
    - images: paths to extracted images
    """
    pdf_url, arxiv_id = resolve_arxiv_url(url_or_id)
    output_path = Path(output_dir) / arxiv_id.replace("/", "_")
    output_path.mkdir(parents=True, exist_ok=True)

    # Fetch metadata
    metadata = fetch_arxiv_metadata(arxiv_id)

    # Download PDF to temp file for docling
    print(f"Downloading PDF from {pdf_url}...")
    response = requests.get(pdf_url, timeout=60)
    response.raise_for_status()

    pdf_path = output_path / f"{arxiv_id.replace('/', '_')}.pdf"
    pdf_path.write_bytes(response.content)

    # Extract with docling
    print("Extracting content with docling...")
    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))

    # Get full markdown content
    full_markdown = result.document.export_to_markdown()

    # Extract sections
    sections = []
    current_section = {"title": "Abstract", "content": ""}
    for line in full_markdown.split("\n"):
        if line.startswith("#"):
            if current_section["content"].strip():
                sections.append(current_section)
            level = len(line) - len(line.lstrip("#"))
            current_section = {
                "title": line.lstrip("#").strip(),
                "level": level,
                "content": "",
            }
        else:
            current_section["content"] += line + "\n"
    if current_section["content"].strip():
        sections.append(current_section)

    # Extract tables
    tables = []
    table_pattern = re.compile(r"\|.*\|", re.MULTILINE)
    in_table = False
    current_table = []
    for line in full_markdown.split("\n"):
        if table_pattern.match(line):
            in_table = True
            current_table.append(line)
        elif in_table:
            if line.strip() == "":
                tables.append("\n".join(current_table))
                current_table = []
                in_table = False
            else:
                current_table.append(line)
    if current_table:
        tables.append("\n".join(current_table))

    # Extract figure captions
    figures = []
    fig_pattern = re.compile(
        r"(?:Figure|Fig\.?)\s*(\d+)[.:]\s*(.*?)(?:\n\n|\Z)", re.IGNORECASE | re.DOTALL
    )
    for match in fig_pattern.finditer(full_markdown):
        figures.append(
            {"number": match.group(1), "caption": match.group(2).strip()}
        )

    # Save extracted images from docling
    image_paths = []
    pictures = result.document.pictures
    if isinstance(pictures, dict):
        pic_items = pictures.values()
    elif isinstance(pictures, list):
        pic_items = pictures
    else:
        pic_items = []
    for i, image in enumerate(pic_items):
        img_path = output_path / f"figure_{i+1}.png"
        try:
            pil_image = image.get_image(result.document)
            if pil_image:
                pil_image.save(str(img_path))
                image_paths.append(str(img_path))
        except Exception as e:
            print(f"Warning: Could not save image {i+1}: {e}")

    # Build extraction result
    extraction = {
        "arxiv_id": arxiv_id,
        "metadata": metadata,
        "content_markdown": full_markdown,
        "sections": sections,
        "tables": tables,
        "figures": figures,
        "image_paths": image_paths,
        "pdf_path": str(pdf_path),
        "output_dir": str(output_path),
    }

    # Save extraction to JSON
    json_path = output_path / "extraction.json"
    with open(json_path, "w") as f:
        json.dump(
            {k: v for k, v in extraction.items() if k != "content_markdown"},
            f,
            indent=2,
            default=str,
        )

    # Save markdown
    md_path = output_path / "content.md"
    md_path.write_text(full_markdown)

    print(f"Extraction complete. Output saved to {output_path}")
    return extraction


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract.py <arxiv_url_or_id> [output_dir]")
        sys.exit(1)

    url = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "output"
    result = extract_paper(url, out)
    print(f"\nTitle: {result['metadata']['title']}")
    print(f"Authors: {', '.join(result['metadata']['authors'][:5])}...")
    print(f"Sections: {len(result['sections'])}")
    print(f"Tables: {len(result['tables'])}")
    print(f"Figures: {len(result['figures'])}")
    print(f"Images saved: {len(result['image_paths'])}")
