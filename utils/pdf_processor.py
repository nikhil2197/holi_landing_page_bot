import os
import re
from PyPDF2 import PdfReader
from typing import List, Optional, Dict, Tuple

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.content = None
        self.sections = {}
        self.overview = {}
        self.is_loaded = False

    def load_pdf(self) -> bool:
        """
        Loads and processes the PDF file with improved overview and section detection.
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

            # Extract essential information first
            self._extract_overview(full_text)
            # Extract sections
            self._extract_sections(full_text)
            self.is_loaded = True
            return True

        except Exception as e:
            print(f"Error loading PDF: {str(e)}")
            return False

    def _extract_overview(self, text: str) -> None:
        """
        Extracts essential event information from the text.
        """
        # Extract date and time
        date_pattern = r"(?:Date|When):?\s*([^\n]+)"
        time_pattern = r"(?:Time):?\s*([^\n]+)"
        location_pattern = r"(?:Location|Venue|Where):?\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|\n(?:[A-Z]|\d))"
        organizer_pattern = r"(?:Organizer|Host|Organized by):?\s*([^\n]+)"
        contact_pattern = r"(?:Contact|For inquiries):?\s*([^\n]+)"

        # Extract key information
        date_match = re.search(date_pattern, text, re.IGNORECASE)
        time_match = re.search(time_pattern, text, re.IGNORECASE)
        location_match = re.search(location_pattern, text, re.IGNORECASE)
        organizer_match = re.search(organizer_pattern, text, re.IGNORECASE)
        contact_match = re.search(contact_pattern, text, re.IGNORECASE)

        # Store matches in overview
        if date_match:
            self.overview['date'] = date_match.group(1).strip()
        if time_match:
            self.overview['time'] = time_match.group(1).strip()
        if location_match:
            self.overview['location'] = location_match.group(1).strip()
        if organizer_match:
            self.overview['organizer'] = organizer_match.group(1).strip()
        if contact_match:
            self.overview['contact'] = contact_match.group(1).strip()

        # Extract brief description (first few paragraphs)
        description_pattern = r"^(?!.*(?:FAQ|Schedule|Price|Contact))(.+?)(?=\n\n[A-Z])"
        description_match = re.search(description_pattern, text, re.DOTALL)
        if description_match:
            self.overview['description'] = description_match.group(1).strip()

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

        # Extract Location Information
        location_pattern = r"(?:Location Details|Venue Information|Getting There).*?(?=\n\n[A-Z]|$)"
        location_match = re.search(location_pattern, text, re.DOTALL | re.IGNORECASE)
        if location_match:
            self.sections['location_details'] = location_match.group(0)

        # Extract Pricing Information
        pricing_pattern = r"(?:Pricing|Ticket|Cost|Price).*?(?=\n\n[A-Z]|$)"
        pricing_match = re.search(pricing_pattern, text, re.DOTALL | re.IGNORECASE)
        if pricing_match:
            self.sections['pricing'] = pricing_match.group(0)

    def get_chunks(self, chunk_size: int = 1000) -> List[str]:
        """
        Creates semantically meaningful chunks with overview priority.
        """
        if not self.is_loaded or not self.content:
            return []

        chunks = []

        # Add overview information first
        if self.overview:
            overview_chunk = "[OVERVIEW]\n"
            for key, value in self.overview.items():
                if value:
                    overview_chunk += f"{key.title()}: {value}\n"
            chunks.append(overview_chunk.strip())

        # Add section-specific chunks
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

        return chunks

    def get_section(self, section_name: str) -> Optional[str]:
        """
        Returns content of a specific section if available.
        """
        return self.sections.get(section_name)

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