"""
Document Ingestion and Parsing Module.

Purpose:
  Extracts raw text and structured metadata from multi-format practice
  documents (Portable Document Format [PDF], Microsoft Word [.docx],
  Microsoft Excel [.xlsx], and plain text [.txt]). Provides local Optical
  Character Recognition (OCR) fallback for scanned image-only pages and
  segments content into semantic chunks for vector indexing.

Deliberately Not For:
  Vector embedding generation, Large Language Model (LLM) querying, or
  network communication.

Invariants:
  1. Files are opened in strict read-only mode to prevent document mutation.
  2. Every generated chunk retains deterministic metadata tracking its exact
     source path, file modification timestamp, page number, and section.
"""

import email
import mailbox
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None

try:
    import openpyxl
except ImportError:
    openpyxl = None


@dataclass
class DocumentChunk:
    """
    Represents an atomic, contextual text segment extracted from a document.

    Attributes:
      chunk_id: Deterministic identifier formatted as 'filepath#page#index'.
      source_path: Absolute filesystem path to the origin file.
      file_name: Basename of the file for citation rendering.
      page_number: 1-indexed document page or sheet index.
      section_heading: Nearest preceding heading or contextual label.
      text: Extracted narrative text content.
      modified_at: ISO-8601 modification timestamp of the source document.
      word_count: Approximate count of words contained within the chunk.
    """

    chunk_id: str
    source_path: str
    file_name: str
    page_number: int
    section_heading: str
    text: str
    modified_at: str
    word_count: int = field(init=False)

    def __post_init__(self) -> None:
        """Calculate word count upon instance initialisation."""
        self.word_count = len(self.text.split())


class DocumentIngestionPipeline:
    """
    Co-ordinates document parsing, OCR fallback, and semantic text chunking.

    Attributes:
      target_chunk_words: Desired token/word volume per chunk (default: 400).
      chunk_overlap_words: Overlapping word boundary count (default: 40).
    """

    def __init__(
        self,
        target_chunk_words: int = 400,
        chunk_overlap_words: int = 40,
    ) -> None:
        """
        Initialise ingestion parameters.

        Args:
          target_chunk_words: Approximate word limit per indexed fragment.
          chunk_overlap_words: Overlap boundary ensuring narrative continuity.
        """
        self.target_chunk_words = target_chunk_words
        self.chunk_overlap_words = chunk_overlap_words

    def parse_file(self, file_path: Path) -> List[DocumentChunk]:
        """
        Parse a single file based on its file extension.

        Execution steps:
          1. Step 1: Validate file existence and determine extension.
          2. Step 2: Route file to matching format extractor.
          3. Step 3: Segment raw page text into indexed DocumentChunk instances.

        Args:
          file_path: Filesystem path pointing to the target document.

        Returns:
          List of DocumentChunk instances with populated metadata.
        """
        # Step 1: Validate file existence and determine extension.
        resolved_path = Path(file_path).resolve()
        if not resolved_path.is_file():
            return []

        suffix = resolved_path.suffix.lower()
        modified_at = datetime.fromtimestamp(
            resolved_path.stat().st_mtime, tz=timezone.utc
        ).isoformat()

        # Step 2: Route file to matching format extractor.
        raw_pages: List[Dict[str, any]] = []
        if suffix == ".pdf":
            raw_pages = self._extract_pdf(resolved_path)
        elif suffix == ".docx":
            raw_pages = self._extract_docx(resolved_path)
        elif suffix in [".xlsx", ".xls"]:
            raw_pages = self._extract_xlsx(resolved_path)
        elif suffix in [".txt", ".md"]:
            raw_pages = self._extract_text(resolved_path)
        elif suffix == ".eml":
            raw_pages = self._extract_eml(resolved_path)
        elif suffix == ".mbox":
            raw_pages = self._extract_mbox(resolved_path)
        else:
            return []

        # Step 3: Segment raw page text into indexed DocumentChunk instances.
        chunks: List[DocumentChunk] = []
        for page_data in raw_pages:
            page_num = page_data.get("page_number", 1)
            heading = page_data.get("heading", "")
            page_text = page_data.get("text", "").strip()

            if not page_text:
                continue

            segmented_texts = self._chunk_text(page_text)
            for idx, text_block in enumerate(segmented_texts):
                chunk_id = f"{resolved_path.name}#p{page_num}#c{idx}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        source_path=str(resolved_path),
                        file_name=resolved_path.name,
                        page_number=page_num,
                        section_heading=heading,
                        text=text_block,
                        modified_at=modified_at,
                    )
                )

        return chunks

    def scan_directory(self, directory_path: Path) -> List[DocumentChunk]:
        """
        Recursively traverse a directory and parse all supported documents.

        Execution steps:
          1. Step 1: Verify directory path exists on disk.
          2. Step 2: Iterate recursively through files, ignoring hidden files.
          3. Step 3: Extract chunks from each supported file and aggregate.

        Args:
          directory_path: Directory to inspect for practice files.

        Returns:
          Aggregated list of all extracted DocumentChunk instances.
        """
        # Step 1: Verify directory path exists on disk.
        dir_path = Path(directory_path).resolve()
        if not dir_path.is_dir():
            return []

        all_chunks: List[DocumentChunk] = []

        # Step 2: Iterate recursively through files, ignoring hidden files.
        for root, _, files in os.walk(dir_path):
            for file in sorted(files):
                if file.startswith("."):
                    continue
                file_path = Path(root) / file

                # Step 3: Extract chunks from each supported file.
                file_chunks = self.parse_file(file_path)
                all_chunks.extend(file_chunks)

        return all_chunks

    def _extract_pdf(self, path: Path) -> List[Dict[str, any]]:
        """
        Extract text from PDF pages, invoking OCR if no digital text is found.

        Execution steps:
          1. Step 1: Attempt native text extraction via pdfplumber or pypdf.
          2. Step 2: If page text is empty, invoke local Tesseract OCR fallback.
          3. Step 3: Return page records with page numbers and text.
        """
        pages = []
        # Step 1: Attempt native extraction.
        if pdfplumber is not None:
            try:
                with pdfplumber.open(path) as pdf:
                    for idx, page in enumerate(pdf.pages, start=1):
                        text = page.extract_text() or ""
                        # Step 2: Fallback to OCR if page has negligible text.
                        if len(text.strip()) < 30:
                            ocr_text = self._ocr_fallback_page(path, idx)
                            if ocr_text:
                                text = ocr_text
                        pages.append(
                            {"page_number": idx, "heading": "", "text": text}
                        )
                return pages
            except Exception:
                pass

        if pypdf is not None:
            try:
                reader = pypdf.PdfReader(str(path))
                for idx, page in enumerate(reader.pages, start=1):
                    text = page.extract_text() or ""
                    pages.append(
                        {"page_number": idx, "heading": "", "text": text}
                    )
                return pages
            except Exception:
                pass

        return pages

    def _ocr_fallback_page(self, path: Path, page_num: int) -> str:
        """
        Execute local Tesseract OCR on a specific page via pdftoppm.

        Execution steps:
          1. Step 1: Convert target page to Portable Network Graphics (PNG).
          2. Step 2: Execute Tesseract OCR subprocess on generated image.
          3. Step 3: Clean up temporary files and return transcribed text.
        """
        # Step 1: Convert target page to PNG via pdftoppm.
        temp_img_prefix = f"/tmp/vault_ocr_{os.getpid()}_{page_num}"
        try:
            cmd = [
                "pdftoppm",
                "-png",
                "-f",
                str(page_num),
                "-l",
                str(page_num),
                "-r",
                "150",
                str(path),
                temp_img_prefix,
            ]
            subprocess.run(cmd, check=True, capture_output=True, timeout=15)

            generated_img = Path(f"{temp_img_prefix}-{page_num}.png")
            if not generated_img.exists():
                generated_img = Path(f"{temp_img_prefix}-0{page_num}.png")
            if not generated_img.exists():
                return ""

            # Step 2: Execute Tesseract OCR subprocess.
            ocr_cmd = [
                "tesseract",
                str(generated_img),
                "stdout",
                "-l",
                "eng",
            ]
            proc = subprocess.run(
                ocr_cmd, check=True, capture_output=True, text=True, timeout=20
            )

            # Step 3: Clean up temporary file.
            if generated_img.exists():
                generated_img.unlink()

            return proc.stdout.strip()
        except Exception:
            return ""

    def _extract_docx(self, path: Path) -> List[Dict[str, any]]:
        """Extract paragraph text and headings from Microsoft Word files."""
        if docx is None:
            return []
        try:
            doc = docx.Document(path)
            full_text = []
            current_heading = ""
            for p in doc.paragraphs:
                text = p.text.strip()
                if not text:
                    continue
                if p.style and p.style.name.startswith("Heading"):
                    current_heading = text
                full_text.append(text)

            combined_text = "\n\n".join(full_text)
            return [
                {
                    "page_number": 1,
                    "heading": current_heading,
                    "text": combined_text,
                }
            ]
        except Exception:
            return []

    def _extract_xlsx(self, path: Path) -> List[Dict[str, any]]:
        """Extract tabular rows and values from Microsoft Excel worksheets."""
        if openpyxl is None:
            return []
        try:
            wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
            pages = []
            for sheet_idx, sheet_name in enumerate(wb.sheetnames, start=1):
                sheet = wb[sheet_name]
                rows_text = []
                for row in sheet.iter_rows(values_only=True):
                    row_vals = [
                        str(cell).strip()
                        for cell in row
                        if cell is not None and str(cell).strip()
                    ]
                    if row_vals:
                        rows_text.append(" | ".join(row_vals))
                combined = "\n".join(rows_text)
                if combined:
                    pages.append(
                        {
                            "page_number": sheet_idx,
                            "heading": f"Sheet: {sheet_name}",
                            "text": combined,
                        }
                    )
            return pages
        except Exception:
            return []

    def _extract_text(self, path: Path) -> List[Dict[str, any]]:
        """Extract text from plain UTF-8 text or markdown documents."""
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            return [{"page_number": 1, "heading": "", "text": text}]
        except Exception:
            return []

    def _extract_eml(self, path: Path) -> List[Dict[str, any]]:
        """
        Extract subject, sender, date, and body from an RFC-822 .eml file.
        """
        try:
            with open(path, "rb") as f:
                msg = email.message_from_binary_file(f)
            subject = msg.get("Subject", "Untitled Email")
            sender = msg.get("From", "Unknown Sender")
            date_str = msg.get("Date", "")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode("utf-8", errors="replace") + "\n"
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="replace")

            header_summary = (
                f"Subject: {subject}\nFrom: {sender}\nDate: {date_str}\n\n"
            )
            full_text = header_summary + body.strip()
            return [{"page_number": 1, "heading": f"Email: {subject}", "text": full_text}]
        except Exception:
            return []

    def _extract_mbox(self, path: Path) -> List[Dict[str, any]]:
        """
        Extract individual email messages from a Google Takeout / Unix .mbox file.
        """
        pages = []
        try:
            box = mailbox.mbox(str(path))
            for idx, msg in enumerate(box, start=1):
                subject = msg.get("Subject", f"Message {idx}")
                sender = msg.get("From", "Unknown Sender")
                date_str = msg.get("Date", "")

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body += payload.decode("utf-8", errors="replace") + "\n"
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode("utf-8", errors="replace")

                header_summary = (
                    f"Subject: {subject}\nFrom: {sender}\nDate: {date_str}\n\n"
                )
                full_text = header_summary + body.strip()
                if full_text.strip():
                    pages.append(
                        {
                            "page_number": idx,
                            "heading": f"Email #{idx}: {subject}",
                            "text": full_text,
                        }
                    )
            return pages
        except Exception:
            return []

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split a block of text into overlapping word windows.

        Execution steps:
          1. Step 1: Tokenise text into whitespace-delimited words.
          2. Step 2: Advance a sliding window of target_chunk_words.
          3. Step 3: Shift window by (target_chunk_words - overlap) words.
        """
        words = text.split()
        if not words:
            return []

        step = max(1, self.target_chunk_words - self.chunk_overlap_words)
        chunks = []
        for i in range(0, len(words), step):
            window = words[i : i + self.target_chunk_words]
            chunk_str = " ".join(window)
            if chunk_str:
                chunks.append(chunk_str)
            if i + self.target_chunk_words >= len(words):
                break

        return chunks
