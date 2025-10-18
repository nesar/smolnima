"""RAG (Retrieval Augmented Generation) tool for document search."""

import os
import glob
from typing import List, Dict, Optional
from smolagents import tool

try:
    from PyPDF2 import PdfReader
except ImportError:
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "pip", "install", "PyPDF2"], check=True)
    from PyPDF2 import PdfReader


# Global document store
_DOCUMENT_STORE: List[Dict[str, str]] = []


def load_documents_from_directory(pdf_dir: str = "./pdfs") -> int:
    """
    Load all PDF documents from directory into memory.

    Args:
        pdf_dir: Directory containing PDF files

    Returns:
        Number of documents loaded
    """
    global _DOCUMENT_STORE

    if not os.path.exists(pdf_dir):
        return 0

    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    loaded_count = 0

    for pdf_path in pdf_files:
        try:
            # Check if already loaded
            filename = os.path.basename(pdf_path)
            if any(d["name"] == filename for d in _DOCUMENT_STORE):
                continue

            # Read PDF
            reader = PdfReader(pdf_path)
            text_content = ""

            for page in reader.pages:
                text_content += page.extract_text() + "\n"

            # Store document
            _DOCUMENT_STORE.append({
                "name": filename,
                "content": text_content,
                "path": pdf_path,
                "pages": len(reader.pages)
            })

            loaded_count += 1

        except Exception as e:
            print(f"Error loading {pdf_path}: {e}")

    return loaded_count


def get_document_count() -> int:
    """Get number of documents in knowledge base."""
    return len(_DOCUMENT_STORE)


def get_all_document_content() -> str:
    """Get concatenated content of all documents."""
    if not _DOCUMENT_STORE:
        return ""

    contents = []
    for doc in _DOCUMENT_STORE:
        contents.append(f"=== {doc['name']} ({doc['pages']} pages) ===\n{doc['content']}")

    return "\n\n".join(contents)


@tool
def search_knowledge_base(query: str, max_chars: int = 8000) -> str:
    """
    Search the physics knowledge base for information relevant to the query.

    This tool provides access to pre-loaded PDF documents containing physics research
    papers, textbooks, and reference materials. Use it to find theoretical background,
    equations, definitions, and research findings.

    Args:
        query: Search query or topic to look up
        max_chars: Maximum characters to return (default 8000)

    Returns:
        Relevant content from knowledge base or message if not found
    """
    if not _DOCUMENT_STORE:
        return "No documents loaded in knowledge base. Please load PDF documents first."

    # Simple keyword-based search
    # In production, you'd use embeddings and vector search
    query_words = set(query.lower().split())

    # Search through all documents
    relevant_sections = []

    for doc in _DOCUMENT_STORE:
        content = doc["content"]
        lines = content.split('\n')

        # Find paragraphs containing query words
        current_para = []
        for line in lines:
            line_lower = line.lower()

            # Check if line contains any query words
            if any(word in line_lower for word in query_words):
                # Include context (previous and next few lines)
                start_idx = max(0, lines.index(line) - 2)
                end_idx = min(len(lines), lines.index(line) + 3)
                context = '\n'.join(lines[start_idx:end_idx])

                relevant_sections.append({
                    "source": doc["name"],
                    "content": context,
                    "relevance": sum(1 for word in query_words if word in line_lower)
                })

    if not relevant_sections:
        # Return summary of available documents
        doc_list = ", ".join([f"{d['name']} ({d['pages']} pages)" for d in _DOCUMENT_STORE])
        return f"No specific matches found for '{query}'. Available documents: {doc_list}"

    # Sort by relevance and combine
    relevant_sections.sort(key=lambda x: x["relevance"], reverse=True)

    result_parts = [f"Found {len(relevant_sections)} relevant sections:\n"]

    total_chars = 0
    for section in relevant_sections[:10]:  # Top 10 sections
        section_text = f"\n[From {section['source']}]\n{section['content']}\n"

        if total_chars + len(section_text) > max_chars:
            break

        result_parts.append(section_text)
        total_chars += len(section_text)

    return "".join(result_parts)
