import os
import json
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import base64
import io
from PIL import Image as PILImage

def generate_pdf_from_conversation(json_file: str, output_pdf: Optional[str] = None) -> str:
    """Generate a PDF from the processed conversation JSON file"""
    # Load the conversation data
    with open(json_file, 'r', encoding='utf-8') as f:
        conversation = json.load(f)
    
    # Set output filename if not provided
    if not output_pdf:
        output_dir = os.path.dirname(json_file)
        output_pdf = os.path.join(output_dir, 'conversation.pdf')
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Message',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Sender1',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.blue,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='Sender2',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.green,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='DateTime',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray
    ))
    
    # Build the PDF content
    elements = []
    
    # Add title
    title = Paragraph("WhatsApp Conversation", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.25*inch))
    
    # Add generation date
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_text = Paragraph(f"Generated on: {now}", styles['Normal'])
    elements.append(date_text)
    elements.append(Spacer(1, 0.5*inch))
    
    # Process each message
    sender_ids = {}
    for message in conversation:
        # Get sender info
        sender = message.get('Name', 'Unknown')
        sender_id = message.get('ID', 0)
        
        if sender_id not in sender_ids:
            sender_ids[sender_id] = len(sender_ids) + 1
        
        # Choose style based on sender
        style_name = f'Sender{1 if sender_ids[sender_id] % 2 == 1 else 2}'
        
        # Format date and time
        date = message.get('Date', '')
        time = message.get('Time', '')
        datetime_text = f"{date} {time}"
        
        # Add sender and datetime
        sender_para = Paragraph(f"{sender}:", styles[style_name])
        elements.append(sender_para)
        datetime_para = Paragraph(datetime_text, styles['DateTime'])
        elements.append(datetime_para)
        
        # Add message content
        msg_text = message.get('Message', '')
        if msg_text:
            msg_para = Paragraph(msg_text, styles['Message'])
            elements.append(msg_para)
        
        # Handle file attachments
        file_attached = message.get('FileAttached', False)
        if file_attached and file_attached.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                # Try to add the image if it exists
                img_path = os.path.join(os.path.dirname(json_file), file_attached)
                if os.path.exists(img_path):
                    img = Image(img_path, width=4*inch, height=3*inch)
                    elements.append(img)
            except Exception as e:
                print(f"Error adding image {file_attached}: {str(e)}")
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Build the PDF
    doc.build(elements)
    
    print(f"PDF generated successfully: {output_pdf}")
    return output_pdf

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        output_pdf = sys.argv[2] if len(sys.argv) > 2 else None
        generate_pdf_from_conversation(json_file, output_pdf)
    else:
        print("Usage: python pdf_generator.py conversation.json [output.pdf]")
