"""
Medical Report PDF Extractor v3
Extracts test names and results from medical laboratory reports
Optimized for macOS M-series chips - Multi-line format support
"""

import fitz  # PyMuPDF
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MedicalReportExtractor:
    """
    Extractor for medical laboratory reports
    Handles multi-line format where test, unit, range, and result are on separate lines
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize the extractor
        
        Args:
            debug: Enable debug logging
        """
        if debug:
            logger.setLevel(logging.DEBUG)
        
        # Words/phrases that indicate this is NOT a test name
        self.skip_keywords = [
            'TEST PARAMETER', 'REFERENCE RANGE', 'RESULT', 'UNIT', 'SAMPLE TYPE',
            'Page', 'Report Status', 'Collected On', 'Reported On', 'Final',
            'Method:', 'Automated', 'Patient Location', 'Flowcytometry',
            'Lab ID', 'UH ID', 'Registered On', 'Age/Gender', 'Electrical Impedence',
            'LABORATORY TEST REPORT', 'HAEMATOLOGY', 'Ref. By', 'Calculated',
            'Processed By', 'End Of Report', 'EDTA', 'Pathologist', 'whole blood',
            'TERMS & CONDITIONS', 'Dr ', 'KMC-', 'Meda Salomi',
            'COMPLETE BLOOD COUNT', 'Male', 'Female', 'Years', 'Name', 'Mr.', 'Mrs.', 'Ms.',
            'Differential Leucocyte Count', 'IP/OP No', 'AKSHAYA NEURO'
        ]
    
    def extract_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract test results from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return self._empty_result(str(pdf_path), "File not found")
        
        logger.info(f"Processing: {pdf_path.name}")
        
        try:
            doc = fitz.open(str(pdf_path))
            all_results = []
            metadata = self._extract_metadata(doc)
            
            for page_num in range(len(doc)):
                logger.debug(f"Processing page {page_num + 1}/{len(doc)}")
                page = doc[page_num]
                text = page.get_text()
                
                page_results = self._parse_multiline_format(text)
                all_results.extend(page_results)
                
                logger.debug(f"Found {len(page_results)} results on page {page_num + 1}")
            
            doc.close()
            
            # Remove duplicates
            unique_results = self._deduplicate_results(all_results)
            
            logger.info(f"Extracted {len(unique_results)} unique test results")
            
            return {
                'success': True,
                'file': pdf_path.name,
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(unique_results),
                'metadata': metadata,
                'results': unique_results
            }
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {str(e)}", exc_info=True)
            return self._empty_result(str(pdf_path), str(e))
    
    def extract_from_directory(self, directory_path: str, pattern: str = "*.pdf") -> List[Dict]:
        """
        Extract from all PDFs in a directory
        
        Args:
            directory_path: Path to directory containing PDFs
            pattern: Glob pattern for PDF files
            
        Returns:
            List of extraction results for each PDF
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return []
        
        pdf_files = list(directory.glob(pattern))
        logger.info(f"Found {len(pdf_files)} PDF files in {directory}")
        
        results = []
        for pdf_file in pdf_files:
            result = self.extract_from_pdf(str(pdf_file))
            results.append(result)
        
        return results
    
    def _parse_multiline_format(self, text: str) -> List[Dict[str, str]]:
        """
        Parse text where test data is on multiple consecutive lines:
        Line 1: TEST NAME
        Line 2: unit
        Line 3: range
        Line 4: result (or method line then result)
        """
        results = []
        # Keep all lines, including empty ones, to maintain proper indexing
        lines = [line.strip() for line in text.split('\n')]
        
        logger.debug(f"Processing {len(lines)} total lines")
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Skip lines with skip keywords
            if self._should_skip_line(line):
                logger.debug(f"Skipping line {i}: {line[:50]}")
                i += 1
                continue
            
            # Check if this looks like a test name
            # Must be mostly uppercase and at least 3 chars
            if self._is_potential_test_name(line):
                test_name = line
                logger.debug(f"Potential test at line {i}: {test_name}")
                
                # Look ahead for the result (a pure number)
                result_value = None
                for j in range(i + 1, min(i + 7, len(lines))):
                    if j >= len(lines):
                        break
                    
                    next_line = lines[j].strip()
                    
                    # Skip empty lines
                    if not next_line:
                        continue
                    
                    # Skip method/automated lines
                    if any(skip in next_line for skip in ['Method:', 'Automated', 'Calculated']):
                        logger.debug(f"  Skipping method line at {j}: {next_line[:30]}")
                        continue
                    
                    # Check if it's a pure number (the result)
                    if self._is_result_value(next_line):
                        result_value = next_line
                        logger.debug(f"  Found result at line {j}: {result_value}")
                        i = j  # Move index to result line
                        break
                
                # If we found a result, save it
                if result_value:
                    cleaned_name = self._clean_test_name(test_name)
                    results.append({
                        'test': cleaned_name,
                        'result': result_value
                    })
                    logger.debug(f"✓ Extracted: {cleaned_name} = {result_value}")
            
            i += 1
        
        return results
    
    def _is_potential_test_name(self, line: str) -> bool:
        """Check if line looks like a test name"""
        # Must have at least 3 characters
        if len(line) < 3:
            return False
        
        # Must start with uppercase letter
        if not line[0].isupper():
            return False
        
        # Check if it contains skip keywords
        if self._should_skip_line(line):
            return False
        
        # Should be mostly uppercase letters (allow spaces, colons, parentheses, dots)
        # At least 50% uppercase letters
        letters = [c for c in line if c.isalpha()]
        if not letters:
            return False
        
        uppercase_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        
        return uppercase_ratio >= 0.5
    
    def _is_result_value(self, line: str) -> bool:
        """Check if line is a result value (pure number)"""
        # Must be digits, dots, and maybe leading zeros
        # Examples: "13.2", "4.46", "38.90", "49", "03", "00", "0"
        pattern = r'^[\d\.]+$'
        return bool(re.match(pattern, line))
    
    def _should_skip_line(self, line: str) -> bool:
        """Check if line should be skipped"""
        # Check for skip keywords
        for keyword in self.skip_keywords:
            if keyword.lower() in line.lower():
                return True
        
        # Skip lines that are just symbols or very short
        if len(line) <= 1:
            return True
        
        # Skip lines that are just dashes or colons
        if all(c in '-:/' for c in line):
            return True
        
        return False
    
    def _clean_test_name(self, name: str) -> str:
        """Clean and standardize test name"""
        # Remove extra whitespace
        name = ' '.join(name.split())
        # Remove trailing colons
        name = name.rstrip(':')
        return name.strip()
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate test results"""
        seen = set()
        unique = []
        
        for item in results:
            key = (item['test'].lower(), item['result'])
            if key not in seen:
                seen.add(key)
                unique.append({
                    'test': item['test'],
                    'result': item['result']
                })
        
        return unique
    
    def _extract_metadata(self, doc) -> Dict:
        """Extract metadata from PDF document"""
        try:
            metadata = doc.metadata
            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'pages': len(doc)
            }
        except Exception as e:
            logger.debug(f"Could not extract metadata: {e}")
            return {'pages': len(doc)}
    
    def _empty_result(self, filename: str, error: str) -> Dict:
        """Return empty result structure with error"""
        return {
            'success': False,
            'file': filename,
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'error': error,
            'results': []
        }
    
    def save_results(self, data: Dict, output_path: str, format: str = 'json'):
        """
        Save extraction results to file
        
        Args:
            data: Extraction results
            output_path: Output file path
            format: Output format ('json' or 'csv')
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved JSON to: {output_path}")
                
            elif format.lower() == 'csv':
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    if data.get('results'):
                        writer = csv.DictWriter(f, fieldnames=['test', 'result'])
                        writer.writeheader()
                        writer.writerows(data['results'])
                    logger.info(f"Saved CSV to: {output_path}")
            else:
                logger.error(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error saving results: {e}", exc_info=True)
    
    def batch_process(self, input_dir: str, output_dir: str, format: str = 'json'):
        """
        Process multiple PDFs and save results
        
        Args:
            input_dir: Directory containing PDFs
            output_dir: Directory for output files
            format: Output format ('json' or 'csv')
        """
        results = self.extract_from_directory(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save individual results
        for result in results:
            if result['success']:
                filename = Path(result['file']).stem
                output_file = output_path / f"{filename}_extracted.{format}"
                self.save_results(result, str(output_file), format)
        
        # Save combined summary
        summary = {
            'processed': len(results),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'total_tests_extracted': sum(r['total_tests'] for r in results),
            'timestamp': datetime.now().isoformat(),
            'files': results
        }
        
        summary_file = output_path / f"extraction_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Batch processing complete. Summary saved to: {summary_file}")
        return summary


# Convenience function for simple usage
def extract_medical_report(pdf_path: str) -> Dict:
    """
    Simple function to extract data from a single PDF
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extraction results dictionary
    """
    extractor = MedicalReportExtractor()
    return extractor.extract_from_pdf(pdf_path)