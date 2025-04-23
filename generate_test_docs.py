import os
from fpdf import FPDF
from datetime import datetime, timedelta

def create_pdf(filename, content):
    """Create a PDF file with the given content."""
    pdf = FPDF(format='A4')  # Use A4 format
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)  # Use Helvetica instead of Arial
    pdf.set_margins(20, 20, 20)  # Set reasonable margins
    
    # Calculate effective width (A4 width is 210mm)
    effective_width = 210 - 2 * 20  # Page width minus left and right margins
    
    # Split content into lines and add to PDF
    for line in content.split('\n'):
        pdf.multi_cell(effective_width, 10, text=line, align='L')  # Use specific width
    
    # Create test_data directory if it doesn't exist
    os.makedirs('test_data', exist_ok=True)
    pdf.output(os.path.join('test_data', filename))

def generate_simple_timeline():
    """Generate a simple timeline case with sequential events"""
    content = """Simple Employment Case Timeline
    
January 15, 2024: Employee John Doe was hired by ABC Corp.
February 1, 2024: Employee completed initial training program.
March 1, 2024: Employee received first performance review.
March 15, 2024: Employee filed complaint about working conditions.
April 1, 2024: Management conducted investigation.
April 15, 2024: Employee was terminated."""

    create_pdf('simple_timeline.pdf', content)

def generate_complex_multiparty():
    """Generate a complex case with multiple parties and overlapping events"""
    content = """Complex Multi-Party Contract Dispute
    
March 1, 2024: Company A and Company B entered into negotiations for software development project.
March 5, 2024: Company C submitted competing proposal.
March 7, 2024: Company B withdrew from negotiations citing resource constraints.
March 10, 2024: Company A began preliminary discussions with Company C.
March 15, 2024: Company D (subsidiary of Company B) claimed intellectual property rights.
March 20, 2024: Company A signed preliminary agreement with Company C.
March 25, 2024: Company B filed injunction through Company D.
April 1, 2024: Court granted temporary restraining order.
April 15, 2024: Mediation began between all parties."""

    create_pdf('complex_multiparty.pdf', content)

def generate_large_document():
    """Generate a large document with many events to test performance"""
    content = "Large Case with Multiple Events\n\n"
    
    # Generate 100 events with random dates
    base_date = datetime(2024, 1, 1)
    events = []
    for i in range(100):
        date = base_date + timedelta(days=i)
        event = f"{date.strftime('%B %d, %Y')}: Event {i+1} occurred involving multiple parties and detailed description of actions taken.\n"
        events.append(event)
    
    content += "\n".join(events)
    create_pdf('large_document.pdf', content)

def generate_mixed_format_dates():
    """Generate a document with various date formats to test date parsing"""
    content = """Document with Mixed Date Formats
    
01/15/2024: Event occurred in MM/DD/YYYY format
2024-03-20: Event occurred in YYYY-MM-DD format
March 25, 2024: Event occurred in Month DD, YYYY format
25th March 2024: Event occurred in DDth Month YYYY format
2024.04.01: Event occurred in YYYY.MM.DD format
Apr 15 2024: Event occurred in MMM DD YYYY format"""

    create_pdf('mixed_date_formats.pdf', content)

def generate_nested_events():
    """Generate a document with nested and related events"""
    content = """Document with Nested and Related Events
    
January 1, 2024: Main contract signed
    January 2, 2024: Subcontract A initiated
        January 3, 2024: Vendor 1 selected
        January 4, 2024: Vendor 2 selected
    January 5, 2024: Subcontract B initiated
        January 6, 2024: Consultant 1 hired
        January 7, 2024: Consultant 2 hired
January 10, 2024: Project kickoff meeting
    January 11, 2024: Team A started work
    January 12, 2024: Team B started work"""

    create_pdf('nested_events.pdf', content)

if __name__ == "__main__":
    # Generate all test documents
    generate_simple_timeline()
    generate_complex_multiparty()
    generate_large_document()
    generate_mixed_format_dates()
    generate_nested_events()
    print("Test documents generated successfully in test_data directory.") 