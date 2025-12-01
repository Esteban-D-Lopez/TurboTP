"""
SEC EDGAR tools for fetching and parsing 10-K filings.
"""
import requests
from typing import Optional, Dict
import re

def fetch_10k(ticker: str) -> Optional[Dict[str, str]]:
    """
    Fetch the latest 10-K filing for a company from SEC EDGAR.
    
    Args:
        ticker: Company stock ticker symbol
        
    Returns:
        Dictionary with 10-K metadata and full text, or None if not found
    """
    try:
        # Get CIK from ticker
        cik = get_cik_from_ticker(ticker)
        if not cik:
            return {"error": f"Could not find CIK for ticker: {ticker}"}
        
        # Get latest 10-K filing
        filings_url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
        headers = {"User-Agent": "TurboTP Research Tool contact@example.com"}
        
        response = requests.get(filings_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        filings = data.get("filings", {}).get("recent", {})
        
        # Find most recent 10-K
        for i, form in enumerate(filings.get("form", [])):
            if form == "10-K":
                accession_number = filings["accessionNumber"][i].replace("-", "")
                filing_date = filings["filingDate"][i]
                primary_document = filings["primaryDocument"][i]
                
                # Fetch the actual 10-K document
                doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{primary_document}"
                doc_response = requests.get(doc_url, headers=headers)
                doc_response.raise_for_status()
                
                return {
                    "ticker": ticker,
                    "cik": cik,
                    "filing_date": filing_date,
                    "accession_number": filings["accessionNumber"][i],
                    "full_text": doc_response.text
                }
        
        return {"error": f"No 10-K filings found for {ticker}"}
        
    except Exception as e:
        return {"error": f"Error fetching 10-K: {str(e)}"}

def get_cik_from_ticker(ticker: str) -> Optional[str]:
    """Get CIK number from ticker symbol."""
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {"User-Agent": "TurboTP Research Tool contact@example.com"}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        companies = response.json()
        
        for company in companies.values():
            if company["ticker"].upper() == ticker.upper():
                return str(company["cik_str"])
        
        return None
    except Exception as e:
        print(f"Error getting CIK: {str(e)}")
        return None

def parse_10k_sections(filing_text: str) -> Dict[str, str]:
    """
    Parse 10-K filing and extract key sections.
    
    Returns dictionary with section names as keys and content as values.
    """
    sections = {}
    
    # Clean HTML if present
    text = re.sub(r'<[^>]+>', '', filing_text)
    
    # Common 10-K sections
    section_patterns = {
        "Business": r"Item\s+1[.\s]+Business(.*?)Item\s+1A",
        "Risk Factors": r"Item\s+1A[.\s]+Risk Factors(.*?)Item\s+1B",
        "MD&A": r"Item\s+7[.\s]+Management'?s Discussion(.*?)Item\s+7A",
        "Financial Statements": r"Item\s+8[.\s]+Financial Statements(.*?)Item\s+9"
    }
    
    for section_name, pattern in section_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Limit to first 3000 characters to avoid overwhelming the agent
            sections[section_name] = content[:3000] + ("..." if len(content) > 3000 else "")
    
    return sections

def summarize_10k(filing_data: Dict[str, str]) -> str:
    """
    Create a structured summary of 10-K content for agent consumption.
    """
    if "error" in filing_data:
        return f"Error: {filing_data['error']}"
    
    sections = parse_10k_sections(filing_data.get("full_text", ""))
    
    summary = f"""
# 10-K Filing Summary: {filing_data.get('ticker', 'Unknown')}

**Filing Date:** {filing_data.get('filing_date', 'Unknown')}
**CIK:** {filing_data.get('cik', 'Unknown')}

## Business Description
{sections.get('Business', 'Not found')}

## Risk Factors
{sections.get('Risk Factors', 'Not found')}

## MD&A (Management's Discussion and Analysis)
{sections.get('MD&A', 'Not found')}

---
*Note: This is an automated summary. For complete details, refer to the full 10-K filing.*
"""
    
    return summary
