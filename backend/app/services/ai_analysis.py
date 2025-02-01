from typing import Dict, List, Tuple
import openai
from ..core.config import settings
import PyPDF2
import docx
import io
import mimetypes

class AIAnalysisService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    async def extract_text(self, file_content: bytes, mime_type: str) -> str:
        """Extract text content from various file types"""
        try:
            if mime_type == "application/pdf":
                # Handle PDF files
                pdf_file = io.BytesIO(file_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            
            elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                # Handle Word documents
                doc = docx.Document(io.BytesIO(file_content))
                return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            elif mime_type.startswith("text/"):
                # Handle text files
                return file_content.decode('utf-8')
            
            else:
                raise ValueError(f"Unsupported file type: {mime_type}")
        
        except Exception as e:
            raise ValueError(f"Error extracting text: {str(e)}")

    async def analyze_document(self, file_content: bytes, mime_type: str) -> Tuple[str, List[str], List[str]]:
        """
        Analyze document content and return:
        - Summary description
        - Suggested categories
        - Suggested tags
        """
        # Extract text from document
        text = await self.extract_text(file_content, mime_type)
        
        # Truncate text if too long (OpenAI has token limits)
        max_chars = 3000  # Adjust based on token limits
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        # Create prompt for GPT
        prompt = f"""Analyze this document and provide:
1. A brief summary (2-3 sentences)
2. Suggested categories (choose from: Invoice, Contract, Report, Other)
3. Relevant tags (3-5 keywords)

Document content:
{text}

Format your response as JSON:
{{
    "summary": "...",
    "categories": ["..."],
    "tags": ["..."]
}}"""

        # Get AI analysis
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a document analysis assistant. Provide concise, relevant analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent results
            max_tokens=500
        )
        
        try:
            import json
            result = json.loads(response.choices[0].message.content)
            return (
                result["summary"],
                result["categories"],
                result["tags"]
            )
        except Exception as e:
            raise ValueError(f"Error parsing AI response: {str(e)}")

    async def get_summary(self, file_content: bytes, mime_type: str) -> str:
        """Get just the summary of a document"""
        summary, _, _ = await self.analyze_document(file_content, mime_type)
        return summary

    async def get_suggestions(self, file_content: bytes, mime_type: str) -> Dict[str, List[str]]:
        """Get category and tag suggestions"""
        _, categories, tags = await self.analyze_document(file_content, mime_type)
        return {
            "categories": categories,
            "tags": tags
        } 