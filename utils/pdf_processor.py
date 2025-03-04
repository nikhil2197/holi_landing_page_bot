import os
from PyPDF2 import PdfReader
from typing import List, Optional

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.content = None
        self.is_loaded = False

    def load_pdf(self) -> bool:
        """
        Loads and processes the PDF file.
        Returns True if successful, False otherwise.
        """
        try:
            if not os.path.exists(self.pdf_path):
                return False
            
            reader = PdfReader(self.pdf_path)
            text_content = []
            
            for page in reader.pages:
                text_content.append(page.extract_text())
            
            self.content = "\n".join(text_content)
            self.is_loaded = True
            return True
            
        except Exception as e:
            print(f"Error loading PDF: {str(e)}")
            return False

    def get_chunks(self, chunk_size: int = 1000) -> List[str]:
        """
        Splits the PDF content into manageable chunks.
        """
        if not self.is_loaded or not self.content:
            return []
        
        chunks = []
        current_chunk = ""
        
        for paragraph in self.content.split("\n\n"):
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def get_content(self) -> Optional[str]:
        """
        Returns the full content of the PDF if loaded.
        """
        return self.content if self.is_loaded else None
