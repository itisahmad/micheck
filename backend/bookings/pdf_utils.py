from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os
from datetime import datetime
from django.conf import settings
from .models import Booking


def generate_receipt_pdf(bookings, payment_id):
    """
    Generate PDF receipt for successful payment.
    
    Args:
        bookings: QuerySet of Booking objects
        payment_id: Razorpay payment ID
    
    Returns:
        BytesIO object containing PDF data
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#f59e0b')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#1f2937')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.HexColor('#4b5563')
    )
    
    # Header
    elements.append(Paragraph("MicCheck Comedy", title_style))
    elements.append(Paragraph("Comedy Pass Receipt", styles['Heading2']))
    elements.append(Spacer(1, 20))
    
    # Payment Details
    payment_data = [
        ['Payment ID:', payment_id],
        ['Payment Date & Time:', datetime.now().strftime('%d-%m-%Y %I:%M %p')],
        ['Status:', 'PAID'],
        ['Amount Paid:', f"Rs. {sum(float(booking.amount_paid) for booking in bookings):.2f}"]
    ]
    
    payment_table = Table(payment_data, colWidths=[2*inch, 3*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
    ]))
    
    elements.append(payment_table)
    elements.append(Spacer(1, 20))
    
    # Customer Details
    if bookings:
        first_booking = bookings[0]
        customer_data = [
            ['Customer Name:', first_booking.performer_name],
            ['Email:', first_booking.email],
            ['Phone:', first_booking.phone],
            ['Number of Slots:', str(len(bookings))]
        ]
        
        customer_table = Table(customer_data, colWidths=[2*inch, 3*inch])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
        ]))
        
        elements.append(customer_table)
        elements.append(Spacer(1, 20))
    
    # Booking Details
    elements.append(Paragraph("Booking Details", heading_style))
    
    booking_data = [['Show Date', 'Time', 'Type', 'Price']]
    
    for booking in bookings:
        spot = booking.spot
        show_date = spot.show.date.strftime('%d-%m-%Y')
        time = spot.time.strftime('%I:%M %p')
        spot_type = spot.spot_type or 'Open Mic'
        price = f"Rs. {float(booking.amount_paid):.2f}"
        booking_data.append([show_date, time, spot_type, price])
    
    booking_table = Table(booking_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1*inch])
    booking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1f2937')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    
    elements.append(booking_table)
    elements.append(Spacer(1, 20))
    
    # Footer
    elements.append(Paragraph("Thank you for choosing MicCheck Comedy!", normal_style))
    elements.append(Paragraph("Please bring this receipt on the day of the show.", normal_style))
    elements.append(Paragraph("For any queries, contact us at: info@miccheck.com", normal_style))
    elements.append(Spacer(1, 20))
    
    # Terms
    terms_text = """
    <b>Terms & Conditions:</b><br/>
    1. This receipt is proof of payment for MicCheck Comedy shows.<br/>
    2. Please arrive 15 minutes before your scheduled time.<br/>
    3. No refunds will be provided for cancellations made less than 24 hours before the show.<br/>
    4. Management reserves the right to refuse entry or remove patrons for inappropriate behavior.<br/>
    5. This receipt is non-transferable and valid only for the person named above.
    """
    
    elements.append(Paragraph(terms_text, ParagraphStyle(
        'Terms',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=6
    )))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    buffer.seek(0)
    return buffer


def save_receipt_pdf(bookings, payment_id):
    """
    Generate and save PDF receipt to media directory.
    
    Args:
        bookings: QuerySet of Booking objects
        payment_id: Razorpay payment ID
    
    Returns:
        str: Relative path to saved PDF file
    """
    # Generate PDF
    pdf_buffer = generate_receipt_pdf(bookings, payment_id)
    
    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"receipt_{payment_id}_{timestamp}.pdf"
    
    # Create receipts directory if it doesn't exist
    receipts_dir = os.path.join(settings.MEDIA_ROOT, 'receipts')
    os.makedirs(receipts_dir, exist_ok=True)
    
    # Save PDF
    file_path = os.path.join(receipts_dir, filename)
    with open(file_path, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    # Return relative path
    return os.path.join('receipts', filename)
