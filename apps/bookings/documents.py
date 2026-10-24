"""PDF document generation for tour bookings.
Builds invoices using saved booking prices and a font supporting Māori macrons.
"""

from datetime import timezone as datetime_timezone
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FONT_NAME = "KiwiLato"
FONT_PATH = Path(__file__).resolve().parent / "fonts" / "Lato-Regular.ttf"

if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


def build_booking_invoice(booking):
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=f"Invoice {booking.booking_reference}",
        author="Kiwi Trails",
    )

    body_style = ParagraphStyle(
        name="InvoiceBody",
        fontName=FONT_NAME,
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#24332D"),
    )
    title_style = ParagraphStyle(
        name="InvoiceTitle",
        parent=body_style,
        fontSize=24,
        leading=30,
        spaceAfter=8 * mm,
    )
    heading_style = ParagraphStyle(
        name="InvoiceHeading",
        parent=body_style,
        fontSize=14,
        leading=20,
        spaceAfter=4 * mm,
    )
    amount_style = ParagraphStyle(
        name="InvoiceAmount",
        parent=body_style,
        alignment=TA_RIGHT,
    )

    def paragraph(value, style=body_style):
        return Paragraph(escape(str(value)), style)

    departure_time = booking.departure.start_datetime.astimezone(datetime_timezone.utc).strftime(
        "%d %b %Y, %H:%M UTC"
    )
    booking_date = booking.created_at.astimezone(datetime_timezone.utc).strftime("%d %b %Y")

    story = [
        paragraph("Kiwi Trails", title_style),
        paragraph("Booking Invoice", heading_style),
    ]

    details = [
        ("Booking reference", booking.booking_reference),
        ("Booking date", booking_date),
        ("Booking status", booking.get_status_display().capitalize()),
        ("Customer", booking.user.full_name),
        ("Email", booking.user.email),
        ("Tour", booking.departure.tour.title),
        ("Location", booking.departure.tour.location),
        ("Departure", departure_time),
        ("Travellers", booking.traveller_count),
    ]

    details_table = Table(
        [[paragraph(label), paragraph(value)] for label, value in details],
        colWidths=[45 * mm, 125 * mm],
        hAlign="LEFT",
    )
    details_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend(
        [
            details_table,
            Spacer(1, 10 * mm),
            paragraph("Price summary (NZD)", heading_style),
        ]
    )

    prices = [
        ("Price per traveller", booking.price_per_person),
        ("Subtotal", booking.subtotal),
        ("Discount", booking.discount_amount),
        ("Total", booking.total_price),
    ]
    price_table = Table(
        [
            [
                paragraph(label),
                paragraph(f"NZD {amount:,.2f}", amount_style),
            ]
            for label, amount in prices
        ],
        colWidths=[110 * mm, 60 * mm],
        hAlign="LEFT",
    )
    price_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, -2), colors.HexColor("#F5F8F6")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DDEEE4")),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#26734D")),
            ]
        )
    )
    story.extend(
        [
            price_table,
            Spacer(1, 8 * mm),
            paragraph("All amounts are in New Zealand dollars (NZD)."),
            paragraph("This invoice records the booking value and is not proof of payment."),
        ]
    )

    document.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
