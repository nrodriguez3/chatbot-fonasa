import os
from fpdf import FPDF
from typing import List
import re
from tqdm import tqdm

def clean_filename(filename: str) -> str:
    """
    Clean filename by removing asterisks and simplifying dashes.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Cleaned filename
    """
    # Remove file extension first
    name, ext = os.path.splitext(filename)
    
    # Replace *_-_* pattern with single underscore
    cleaned = re.sub(r'\*_-_', '_', name)
    
    # Remove any remaining asterisks
    cleaned = cleaned.replace('*', '')
    
    # Remove any double underscores that might have been created
    cleaned = re.sub(r'_{2,}', '_', cleaned)
    
    # Add back the extension
    return cleaned + ext

def convert_to_pdf(txt_path: str, pdf_path: str) -> None:
    """
    Convert a text file to PDF.
    
    Args:
        txt_path (str): Path to the input text file
        pdf_path (str): Path where the PDF should be saved
    """
    try:
        # Create PDF object
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Read and write text content
        with open(txt_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Encode string to prevent encoding errors
                clean_line = line.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, txt=clean_line)
        
        # Save the PDF
        pdf.output(pdf_path)
        
    except Exception as e:
        print(f"Error converting {txt_path}: {str(e)}")

def process_folder(input_folder: str, output_folder: str = None) -> None:
    """
    Process all txt files in a folder and its subfolders:
    1. Clean filenames (remove * and simplify dashes)
    2. Convert to PDF
    
    Args:
        input_folder (str): Path to the input folder containing txt files
        output_folder (str): Path to output folder for PDFs. If None, uses input folder
    """
    if output_folder is None:
        output_folder = input_folder
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Collect all txt files
    txt_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    
    # Process each file
    for txt_path in tqdm(txt_files, desc="Processing files"):
        try:
            # Get relative path to maintain folder structure
            rel_path = os.path.relpath(txt_path, input_folder)
            
            # Clean filename
            clean_name = clean_filename(os.path.basename(rel_path))
            
            # Create output subfolders if needed
            output_subdir = os.path.dirname(os.path.join(output_folder, rel_path))
            os.makedirs(output_subdir, exist_ok=True)
            
            # Generate output PDF path
            pdf_path = os.path.join(output_subdir, os.path.splitext(clean_name)[0] + '.pdf')
            
            # Convert to PDF
            convert_to_pdf(txt_path, pdf_path)
            
        except Exception as e:
            print(f"Error processing {txt_path}: {str(e)}")
            continue

def get_processed_files(folder: str) -> List[str]:
    """
    Get list of successfully processed PDF files.
    
    Args:
        folder (str): Folder to search in
        
    Returns:
        List[str]: List of PDF file paths
    """
    pdf_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files