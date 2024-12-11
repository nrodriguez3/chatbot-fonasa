import os
from fpdf import FPDF
from tqdm import tqdm

def combine_txt_files(input_folder: str, output_file: str) -> None:
    """
    Combines all txt files from input folder into a single PDF file.
    Adds headers for each file and maintains folder structure in the content.
    
    Args:
        input_folder (str): Path to folder containing txt files
        output_file (str): Path for output PDF file
    """
    # Create PDF object
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set fonts for different elements
    pdf.set_font("Arial", "B", 16)  # Bold for main titles
    
    # Get all txt files
    txt_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.txt'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, input_folder)
                txt_files.append((full_path, relative_path))
    
    # Sort files by path to maintain structure
    txt_files.sort(key=lambda x: x[1])
    
    # Process each file
    for file_path, relative_path in tqdm(txt_files, desc="Combining files"):
        try:
            # Add file header
            pdf.set_font("Arial", "B", 14)
            # Clean up the filename for display
            display_name = os.path.splitext(relative_path)[0].replace('_', ' ').title()
            pdf.cell(0, 10, f"\n{display_name}", ln=True)
            pdf.ln(5)
            
            # Add file content
            pdf.set_font("Arial", "", 12)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Handle potential encoding issues
                content = content.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, content)
            
            # Add spacing between files
            pdf.ln(10)
            
            # Add a page break if we're not at the end
            pdf.add_page()
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue
    
    # Save the combined PDF
    try:
        print(f"Saving combined PDF to {output_file}...")
        pdf.output(output_file)
        print("Successfully created combined PDF!")
    except Exception as e:
        print(f"Error saving PDF: {str(e)}")
