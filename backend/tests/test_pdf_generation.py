import unittest
import os
import PyPDF2
from datetime import datetime
from generate_test_docs import create_employment_contract, create_nda, create_lease_agreement, create_directory

class TestPDFGeneration(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.test_data_dir = 'test_data'
        create_directory()  # Ensure the directory exists
        
    def tearDown(self):
        """Clean up test files after each test"""
        files_to_delete = [
            'employment_contract.pdf',
            'nda_agreement.pdf',
            'lease_agreement.pdf'
        ]
        for file in files_to_delete:
            file_path = os.path.join(self.test_data_dir, file)
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_file_creation(self):
        """Test if PDF files are created successfully"""
        # Generate all documents
        create_employment_contract()
        create_nda()
        create_lease_agreement()
        
        # Check if files exist
        expected_files = [
            'employment_contract.pdf',
            'nda_agreement.pdf',
            'lease_agreement.pdf'
        ]
        
        for file in expected_files:
            file_path = os.path.join(self.test_data_dir, file)
            self.assertTrue(os.path.exists(file_path), f"File {file} was not created")
            self.assertGreater(os.path.getsize(file_path), 0, f"File {file} is empty")
    
    def test_pdf_content(self):
        """Test if PDFs contain expected content"""
        # Generate documents
        create_employment_contract()
        create_nda()
        create_lease_agreement()
        
        # Test employment contract
        with open(os.path.join(self.test_data_dir, 'employment_contract.pdf'), 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = reader.pages[0].extract_text()
            self.assertIn("EMPLOYMENT AGREEMENT", text)
            self.assertIn("EMPLOYER CORPORATION INC.", text)
            self.assertIn("JOHN DOE", text)
        
        # Test NDA
        with open(os.path.join(self.test_data_dir, 'nda_agreement.pdf'), 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = reader.pages[0].extract_text()
            self.assertIn("NON-DISCLOSURE AGREEMENT", text)
            self.assertIn("COMPANY XYZ CORP.", text)
            self.assertIn("ACME CONSULTING LLC", text)
        
        # Test lease agreement
        with open(os.path.join(self.test_data_dir, 'lease_agreement.pdf'), 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = reader.pages[0].extract_text()
            self.assertIn("RESIDENTIAL LEASE AGREEMENT", text)
            self.assertIn("Smith Property Management LLC", text)
            self.assertIn("Jane Smith", text)
    
    def test_pdf_structure(self):
        """Test if generated PDFs have valid PDF structure"""
        create_employment_contract()
        create_nda()
        create_lease_agreement()
        
        files_to_test = [
            'employment_contract.pdf',
            'nda_agreement.pdf',
            'lease_agreement.pdf'
        ]
        
        for file in files_to_test:
            file_path = os.path.join(self.test_data_dir, file)
            with open(file_path, 'rb') as pdf_file:
                # This will raise an exception if the PDF is invalid
                reader = PyPDF2.PdfReader(pdf_file)
                self.assertGreater(len(reader.pages), 0, f"PDF {file} has no pages")
                # Check if first page can be read
                self.assertIsNotNone(reader.pages[0].extract_text())

if __name__ == '__main__':
    unittest.main() 