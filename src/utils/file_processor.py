"""
File processing utilities for Document Composer.
Handles uploaded files and extracts processable content.
"""
import os
from typing import Optional, List
import PyPDF2
from docx import Document

def save_uploaded_file(uploaded_file, destination_folder: str = "./temp_uploads") -> str:
    """
    Save Streamlit uploaded file to temporary location.
    Returns the file path.
    """
    os.makedirs(destination_folder, exist_ok=True)
    file_path = os.path.join(destination_folder, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file."""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from DOCX file."""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"

def extract_text_from_txt(file_path: str) -> str:
    """Extract text content from TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        return f"Error extracting TXT: {str(e)}"

def process_uploaded_file(uploaded_file) -> str:
    """
    Process uploaded file and extract text content.
    Returns extracted text.
    """
    file_path = save_uploaded_file(uploaded_file)
    
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif file_ext in ['.txt', '.md']:
        return extract_text_from_txt(file_path)
    else:
        return f"Unsupported file type: {file_ext}"

def process_multiple_files(uploaded_files: List) -> str:
    """
    Process multiple uploaded files and combine their content.
    Returns combined text.
    """
    combined_text = []
    
    for uploaded_file in uploaded_files:
        text = process_uploaded_file(uploaded_file)
        combined_text.append(f"--- {uploaded_file.name} ---\n{text}\n")
    
    return "\n\n".join(combined_text)

def process_interview_notes(uploaded_files: List) -> str:
    """
    Process interview notes and structure them for agent consumption.
    """
    combined_notes = process_multiple_files(uploaded_files)
    
    # Add structure
    structured = f"""
# Interview/Meeting Notes Summary

{combined_notes}

## Instructions for Analysis
- Extract functional responsibilities mentioned
- Identify risks discussed  
- Note assets and capabilities referenced
- Capture any quotes or specific examples
"""
    
    return structured

def parse_excel_benchmarking(file_path: str) -> str:
    """
    Parse uploaded Excel benchmarking study.
    Returns summary of key metrics.
    """
    try:
        import pandas as pd
        df = pd.read_excel(file_path)
        
        summary = f"""
# Benchmarking Study Summary

## Data Overview
- Total comparables: {len(df)}
- Columns: {', '.join(df.columns.tolist())}

## Sample Data (first 5 rows)
{df.head().to_markdown()}

## Key Statistics
{df.describe().to_markdown()}
"""
        return summary
    except Exception as e:
        return f"Error parsing Excel: {str(e)}"

def parse_csv_benchmarking(file_path: str) -> str:
    """
    Parse uploaded CSV benchmarking data.
    Returns summary of key metrics.
    """
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        
        summary = f"""
# Benchmarking Data Summary

## Data Overview
- Total comparables: {len(df)}
- Columns: {', '.join(df.columns.tolist())}

## Sample Data (first 5 rows)
{df.head().to_markdown()}

## Key Statistics
{df.describe().to_markdown()}
"""
        return summary
    except Exception as e:
        return f"Error parsing CSV: {str(e)}"
