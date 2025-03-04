import os
import re
from PyPDF2 import PdfReader
from typing import List, Optional, Dict

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.content = None
        self.overview = {}
        self.is_loaded = False

    def load_pdf(self) -> bool:
        """
        Loads and processes the PDF file.
        """
        try:
            if not os.path.exists(self.pdf_path):
                return False

            reader = PdfReader(self.pdf_path)
            text_content = []

            for page in reader.pages:
                text_content.append(page.extract_text())

            full_text = "\n".join(text_content)
            self.content = full_text

            # Extract essential information
            self._extract_overview(full_text)
            self.is_loaded = True
            return True

        except Exception as e:
            print(f"Error loading PDF: {str(e)}")
            return False

    def _extract_overview(self, text: str) -> None:
        """
        Extracts essential event information from the text.
        """
        patterns = {
            'date': r"(?:Date|When):?\s*([^\n]+)",
            'time': r"(?:Time):?\s*([^\n]+)",
            'location': r"(?:Location|Venue|Where):?\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|\n(?:[A-Z]|\d))",
            'organizer': r"(?:Organizer|Host|Organized by):?\s*([^\n]+)",
            'pricing': r"(?:Price|Cost|Ticket):?\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|\n(?:[A-Z]|\d))",
            'contact': r"(?:Contact|For inquiries):?\s*([^\n]+)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                self.overview[key] = match.group(1).strip()

    def get_chunks(self, chunk_size: int = 1000) -> List[str]:
        """
        Creates informative chunks with overview priority.
        """
        if not self.is_loaded or not self.content:
            return []

        chunks = []

        # Add overview as first chunk
        if self.overview:
            overview_text = "[OVERVIEW]\n"
            for key, value in self.overview.items():
                if value:
                    overview_text += f"{key.title()}: {value}\n"
            chunks.append(overview_text.strip())

        # Process remaining content in meaningful chunks
        paragraphs = self.content.split("\n\n")
        current_section = ""
        current_chunk = ""

        for paragraph in paragraphs:
            # Detect section headers
            if re.match(r"^[A-Z\s]{2,}:?$", paragraph.strip()):
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_section = paragraph.strip()
                current_chunk = f"[{current_section}]\n"
                continue

            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = f"[{current_section}]\n" if current_section else ""
                current_chunk += paragraph + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def get_overview(self) -> Dict[str, str]:
        """
        Returns the extracted overview information.
        """
        return self.overview

    def get_content(self) -> Optional[str]:
        """
        Returns the full content of the PDF if loaded.
        """
        return self.content if self.is_loaded else None