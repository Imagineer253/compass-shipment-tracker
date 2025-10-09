"""
PDF utilities for COMPASS document generation
"""
import os
import tempfile
import logging
from pathlib import Path
from typing import List, Optional
import subprocess
import platform

try:
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logging.warning("PyPDF2 or reportlab not available. PDF features will be limited.")

def convert_docx_to_pdf(docx_path: str, output_path: str = None) -> Optional[str]:
    """
    Convert DOCX file to PDF
    
    Args:
        docx_path: Path to the DOCX file
        output_path: Optional output path for PDF. If None, uses same name with .pdf extension
    
    Returns:
        Path to the generated PDF file, or None if conversion failed
    """
    if not os.path.exists(docx_path):
        logging.error(f"DOCX file not found: {docx_path}")
        return None
    
    if output_path is None:
        output_path = docx_path.replace('.docx', '.pdf')
    
    try:
        # Method 1: Try using python-docx2pdf (works on Windows with Word installed)
        try:
            from docx2pdf import convert
            convert(docx_path, output_path)
            if os.path.exists(output_path):
                logging.info(f"Successfully converted DOCX to PDF using docx2pdf: {output_path}")
                return output_path
        except Exception as e:
            logging.warning(f"docx2pdf conversion failed: {e}")
        
        # Method 2: Try using LibreOffice (cross-platform)
        if platform.system() in ['Linux', 'Darwin']:  # Linux or macOS
            try:
                cmd = [
                    'libreoffice', '--headless', '--convert-to', 'pdf',
                    '--outdir', os.path.dirname(output_path),
                    docx_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # LibreOffice creates PDF with same name as DOCX
                    expected_pdf = os.path.join(
                        os.path.dirname(output_path),
                        os.path.basename(docx_path).replace('.docx', '.pdf')
                    )
                    if os.path.exists(expected_pdf) and expected_pdf != output_path:
                        os.rename(expected_pdf, output_path)
                    
                    if os.path.exists(output_path):
                        logging.info(f"Successfully converted DOCX to PDF using LibreOffice: {output_path}")
                        return output_path
                else:
                    logging.error(f"LibreOffice conversion failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                logging.error("LibreOffice conversion timed out")
            except Exception as e:
                logging.error(f"LibreOffice conversion error: {e}")
        
        # Method 3: Fallback - create a simple PDF with error message
        if PYPDF2_AVAILABLE:
            create_error_pdf(output_path, "PDF conversion not available on this system")
            return output_path
        
        logging.error("No PDF conversion method available")
        return None
        
    except Exception as e:
        logging.error(f"PDF conversion failed: {e}")
        return None

def create_error_pdf(output_path: str, message: str):
    """Create a simple PDF with an error message"""
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 100, "COMPASS Document Generation")
        
        # Add error message
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 150, message)
        c.drawString(50, height - 170, "Please contact system administrator for assistance.")
        
        # Add timestamp
        from datetime import datetime
        c.drawString(50, height - 200, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        logging.info(f"Created error PDF: {output_path}")
    except Exception as e:
        logging.error(f"Failed to create error PDF: {e}")

def merge_pdfs(pdf_paths: List[str], output_path: str) -> bool:
    """
    Merge multiple PDF files into one
    
    Args:
        pdf_paths: List of paths to PDF files to merge
        output_path: Path for the merged PDF output
    
    Returns:
        True if successful, False otherwise
    """
    if not PYPDF2_AVAILABLE:
        logging.error("PyPDF2 not available for PDF merging")
        return False
    
    try:
        writer = PdfWriter()
        
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                logging.warning(f"PDF file not found, skipping: {pdf_path}")
                continue
            
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
                logging.info(f"Added PDF to merge: {pdf_path}")
            except Exception as e:
                logging.error(f"Error reading PDF {pdf_path}: {e}")
                continue
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        logging.info(f"Successfully merged PDFs to: {output_path}")
        return True
        
    except Exception as e:
        logging.error(f"PDF merge failed: {e}")
        return False

def get_extra_documents(shipment_type: str, temperature_type: str = None) -> List[str]:
    """
    Get list of extra documents to append based on shipment type
    Only for Normal Sample Import shipments
    
    Args:
        shipment_type: Type of shipment (import, export, etc.)
        temperature_type: Temperature type (normal, cold, etc.)
    
    Returns:
        List of PDF file paths to append
    """
    extra_docs = []
    
    try:
        # Only add extra documents for Normal Sample Import
        if shipment_type == 'import' and temperature_type == 'normal':
            docs_folder = Path(__file__).parent.parent / 'static' / 'extra_docs' / 'normal_temp_import'
            
            if docs_folder.exists():
                # Get all PDF files in the folder, sorted alphabetically
                pdf_files = sorted(docs_folder.glob('*.pdf'))
                extra_docs = [str(pdf_file) for pdf_file in pdf_files]
                logging.info(f"Found {len(extra_docs)} extra documents for Normal Sample Import")
            else:
                logging.info(f"No extra documents folder found: {docs_folder}")
        else:
            logging.info(f"No extra documents configured for {shipment_type}/{temperature_type}")
    
    except Exception as e:
        logging.error(f"Error getting extra documents: {e}")
    
    return extra_docs

def generate_pdf_with_extras(docx_path: str, shipment_type: str, temperature_type: str = None) -> Optional[str]:
    """
    Generate PDF from DOCX and append extra documents if available
    
    Args:
        docx_path: Path to the main DOCX document
        shipment_type: Type of shipment
        temperature_type: Temperature type
    
    Returns:
        Path to the final PDF with extras appended, or None if failed
    """
    try:
        # Convert main document to PDF
        main_pdf_path = convert_docx_to_pdf(docx_path)
        if not main_pdf_path:
            logging.error("Failed to convert main document to PDF")
            return None
        
        # Get extra documents
        extra_docs = get_extra_documents(shipment_type, temperature_type)
        
        if not extra_docs:
            # No extra documents, return the main PDF
            logging.info("No extra documents to append")
            return main_pdf_path
        
        # Create final PDF with extras
        final_pdf_path = main_pdf_path.replace('.pdf', '_with_extras.pdf')
        pdf_list = [main_pdf_path] + extra_docs
        
        if merge_pdfs(pdf_list, final_pdf_path):
            # Clean up the intermediate main PDF
            try:
                os.remove(main_pdf_path)
            except:
                pass
            
            logging.info(f"Successfully created PDF with extras: {final_pdf_path}")
            return final_pdf_path
        else:
            logging.error("Failed to merge PDFs")
            return main_pdf_path  # Return main PDF as fallback
    
    except Exception as e:
        logging.error(f"Error generating PDF with extras: {e}")
        return None

def install_pdf_dependencies():
    """Install required PDF dependencies"""
    try:
        import subprocess
        import sys
        
        # Install Python packages
        packages = ['PyPDF2==3.0.1', 'reportlab==4.0.4', 'python-docx2pdf==0.1.8']
        for package in packages:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        
        logging.info("PDF dependencies installed successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to install PDF dependencies: {e}")
        return False
