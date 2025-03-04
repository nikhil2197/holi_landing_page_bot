import os
import re
from PyPDF2 import PdfReader
from typing import List, Optional, Dict, Tuple

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.content = None
        self.sections = {}
        self.is_loaded = False

    def load_pdf(self) -> bool:
        """
        Loads and processes the PDF file with improved section detection.
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

            # Extract sections
            self._extract_sections(full_text)
            self.is_loaded = True
            return True

        except Exception as e:
            print(f"Error loading PDF: {str(e)}")
            return False

    def _extract_sections(self, text: str) -> None:
        """
        Extracts different sections from the text using pattern matching.
        """
        # Extract FAQs
        faq_pattern = r"(?:FAQ|Frequently Asked Questions).*?(?=\n\n[A-Z]|$)"
        faq_match = re.search(faq_pattern, text, re.DOTALL | re.IGNORECASE)
        if faq_match:
            self.sections['faqs'] = faq_match.group(0)

        # Extract Session Details/Schedule
        session_pattern = r"(?:Session Details|Schedule|Program Details).*?(?=\n\n[A-Z]|$)"
        session_match = re.search(session_pattern, text, re.DOTALL | re.IGNORECASE)
        if session_match:
            self.sections['session_details'] = session_match.group(0)

        # Extract Location/Venue Information
        location_pattern = r"(?:Location|Venue|Address).*?(?=\n\n[A-Z]|$)"
        location_match = re.search(location_pattern, text, re.DOTALL | re.IGNORECASE)
        if location_match:
            self.sections['location'] = location_match.group(0)

        # Extract Pricing Information
        pricing_pattern = r"(?:Pricing|Ticket|Cost|Price).*?(?=\n\n[A-Z]|$)"
        pricing_match = re.search(pricing_pattern, text, re.DOTALL | re.IGNORECASE)
        if pricing_match:
            self.sections['pricing'] = pricing_match.group(0)

    def get_chunks(self, chunk_size: int = 1000) -> List[str]:
        """
        Creates semantically meaningful chunks preserving section context.
        """
        if not self.is_loaded or not self.content:
            return []

        chunks = []

        # First add section-specific chunks
        for section_name, section_content in self.sections.items():
            if section_content:
                # Add section identifier at the start
                section_chunk = f"[{section_name.upper()}]\n{section_content}"

                # Split large sections into smaller chunks while preserving context
                if len(section_chunk) > chunk_size:
                    current_chunk = ""
                    for paragraph in section_chunk.split("\n\n"):
                        if len(current_chunk) + len(paragraph) <= chunk_size:
                            current_chunk += paragraph + "\n\n"
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = f"[{section_name.upper()}] (continued)\n{paragraph}\n\n"
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                else:
                    chunks.append(section_chunk)

        # Add remaining content
        remaining_text = self.content
        for section_content in self.sections.values():
            if section_content:
                remaining_text = remaining_text.replace(section_content, '')

        # Process remaining text
        current_chunk = ""
        for paragraph in remaining_text.split("\n\n"):
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def get_section(self, section_name: str) -> Optional[str]:
        """
        Returns content of a specific section if available.
        """
        return self.sections.get(section_name)

    def get_content(self) -> Optional[str]:
        """
        Returns the full content of the PDF if loaded.
        """
        return self.content if self.is_loaded else None