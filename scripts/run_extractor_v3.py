#!/usr/bin/env python3
"""
Runner script for Medical Report Extractor v3
Process single or multiple PDF medical reports
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.extractor_v3 import MedicalReportExtractor, extract_medical_report


def main():
    """Main entry point for the extractor"""
    parser = argparse.ArgumentParser(
        description='Extract test results from medical report PDFs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from a single PDF
  python scripts/run_extractor_v3.py input.pdf
  
  # Extract and save to specific output file
  python scripts/run_extractor_v3.py input.pdf -o results.json
  
  # Process all PDFs in a directory
  python scripts/run_extractor_v3.py /path/to/reports/ -d
  
  # Batch process with CSV output
  python scripts/run_extractor_v3.py /path/to/reports/ -d -f csv -o ./output/
  
  # Enable debug logging
  python scripts/run_extractor_v3.py input.pdf --debug
        """
    )
    
    parser.add_argument(
        'input',
        type=str,
        help='Input PDF file or directory containing PDFs'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file or directory path (default: same name as input with _extracted suffix)'
    )
    
    parser.add_argument(
        '-f', '--format',
        type=str,
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '-d', '--directory',
        action='store_true',
        help='Process all PDFs in the input directory'
    )
    
    parser.add_argument(
        '--pattern',
        type=str,
        default='*.pdf',
        help='File pattern for directory processing (default: *.pdf)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print results to console'
    )
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = MedicalReportExtractor(debug=args.debug)
    
    input_path = Path(args.input)
    
    # Validate input
    if not input_path.exists():
        print(f"❌ Error: Input path does not exist: {input_path}")
        sys.exit(1)
    
    # Process directory or single file
    if args.directory or input_path.is_dir():
        if not input_path.is_dir():
            print(f"❌ Error: {input_path} is not a directory")
            sys.exit(1)
        
        print(f"📁 Processing directory: {input_path}")
        
        # Determine output directory
        if args.output:
            output_dir = Path(args.output)
        else:
            output_dir = input_path / 'extracted_results'
        
        # Batch process
        summary = extractor.batch_process(
            str(input_path),
            str(output_dir),
            format=args.format
        )
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 EXTRACTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total files processed: {summary['processed']}")
        print(f"✅ Successful: {summary['successful']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📝 Total tests extracted: {summary['total_tests_extracted']}")
        print(f"💾 Results saved to: {output_dir}")
        print(f"{'='*60}\n")
        
        if args.pretty:
            print_summary_details(summary)
    
    else:
        # Process single file
        if not input_path.is_file():
            print(f"❌ Error: {input_path} is not a file")
            sys.exit(1)
        
        print(f"📄 Processing file: {input_path.name}")
        
        # Extract data
        result = extractor.extract_from_pdf(str(input_path))
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.parent / f"{input_path.stem}_extracted.{args.format}"
        
        # Save results
        if result['success']:
            extractor.save_results(result, str(output_path), format=args.format)
            
            print(f"\n✅ Success!")
            print(f"📝 Extracted {result['total_tests']} test results")
            print(f"💾 Saved to: {output_path}")
            
            if args.pretty:
                print_results(result)
        else:
            print(f"\n❌ Failed to process file")
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)


def print_results(result: dict):
    """Pretty print extraction results"""
    print(f"\n{'='*60}")
    print(f"📋 EXTRACTED TEST RESULTS")
    print(f"{'='*60}")
    
    if result.get('metadata'):
        meta = result['metadata']
        if meta.get('title'):
            print(f"Report: {meta['title']}")
        print(f"Pages: {meta.get('pages', 'N/A')}")
        print()
    
    for i, test in enumerate(result['results'], 1):
        print(f"{i:3d}. {test['test']:<50} {test['result']:>10}")
    
    print(f"{'='*60}\n")


def print_summary_details(summary: dict):
    """Pretty print batch processing summary"""
    print(f"\n{'='*60}")
    print(f"📁 FILES PROCESSED")
    print(f"{'='*60}\n")
    
    for file_result in summary['files']:
        status = "✅" if file_result['success'] else "❌"
        filename = Path(file_result['file']).name
        tests = file_result['total_tests']
        print(f"{status} {filename:<40} ({tests} tests)")
    
    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
