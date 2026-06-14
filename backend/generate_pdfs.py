import os
import sys
import subprocess
from pathlib import Path

# Ensure reportlab is installed
try:
    import reportlab
except ImportError:
    print("Installing reportlab...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Define target directories
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "documents"
APP_DOCS_DIR = BASE_DIR / "app" / "documents"

# Ensure directories exist
DOCS_DIR.mkdir(parents=True, exist_ok=True)
APP_DOCS_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    alignment=TA_CENTER,
    fontSize=20,
    leading=24,
    spaceAfter=15,
    textColor="#1e293b" # Dark slate blue
)

heading_style = ParagraphStyle(
    'DocHeading',
    parent=styles['Heading2'],
    fontSize=13,
    leading=16,
    spaceBefore=12,
    spaceAfter=6,
    textColor="#0f172a"
)

body_style = ParagraphStyle(
    'DocBody',
    parent=styles['BodyText'],
    fontSize=10,
    leading=14,
    spaceAfter=8,
    textColor="#334155"
)

bullet_style = ParagraphStyle(
    'DocBullet',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    leftIndent=15,
    firstLineIndent=-10,
    spaceAfter=6,
    textColor="#334155"
)

def create_faq_pdf(filepath):
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    story = []

    story.append(Paragraph("MemoryCart AI - Frequently Asked Questions (FAQ)", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Q1: What is MemoryCart?", heading_style))
    story.append(Paragraph("MemoryCart is a next-generation smart e-commerce platform integrated with local and long-term memory support capabilities. Our built-in AI agent retains context about past support queries, orders, and refund requests, ensuring customers enjoy a cohesive, seamless customer service experience without having to repeat their context.", body_style))

    story.append(Paragraph("Q2: How can I track or check my order status?", heading_style))
    story.append(Paragraph("You can request order status updates directly from the AI chat agent. Simply specify your order number (for example, ORD1001) in your message, and the agent will retrieve the latest shipping status, product name, and expected delivery date for you.", body_style))

    story.append(Paragraph("Q3: How do refund claims work?", heading_style))
    story.append(Paragraph("If you request a refund, our system processes it according to our policy guidelines. Once a refund is initiated, you can track it via the refund reference ID (e.g., REF1001) through the chat console. The agent will retrieve the exact amount and refund status instantly.", body_style))

    story.append(Paragraph("Q4: Can the support agent remember my previous issues?", heading_style))
    story.append(Paragraph("Yes! MemoryCart utilizes Hindsight memory architectures along with a relational database. This allows the AI agent to retrieve and reflect on recent conversations, previous order issues, or refund claims automatically.", body_style))

    doc.build(story)

def create_shipping_policy_pdf(filepath):
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    story = []

    story.append(Paragraph("MemoryCart Shipping Policy", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. Shipping Rates & Delivery Estimates", heading_style))
    story.append(Paragraph("We offer multiple shipping speeds to suit your needs. Shipping charges for your order will be calculated and displayed at checkout:", body_style))
    
    story.append(Paragraph("&bull; <b>Standard Shipping:</b> 3-5 business days delivery. Free of charge for orders total exceeding $50.", bullet_style))
    story.append(Paragraph("&bull; <b>Express Shipping:</b> 1-2 business days delivery. Flat rate of $15.00 applies to all orders.", bullet_style))
    story.append(Paragraph("&bull; <b>Next-Day Delivery:</b> Available in selected metropolitan areas for a flat rate of $25.00.", bullet_style))

    story.append(Paragraph("2. Shipment Confirmation & Order Tracking", heading_style))
    story.append(Paragraph("You will receive a shipment confirmation email once your order has shipped containing your tracking number(s). The tracking number will be active within 24 hours. You can also query our chat agent directly for immediate tracking updates using your order ID.", body_style))

    story.append(Paragraph("3. Damages and Missing Deliveries", heading_style))
    story.append(Paragraph("MemoryCart is not liable for products damaged or lost during shipping. If you received your order damaged, please contact the shipment carrier to file a claim. Please save all packaging materials and damaged goods before filing a claim.", body_style))

    doc.build(story)

def create_return_policy_pdf(filepath):
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    story = []

    story.append(Paragraph("MemoryCart Return & Refund Policy", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. Returns & Eligibility Window", heading_style))
    story.append(Paragraph("We want you to love your purchase. If you are not entirely satisfied, we're here to help:", body_style))
    
    story.append(Paragraph("&bull; <b>Returns Period:</b> You have 30 calendar days to return an item from the date you received it.", bullet_style))
    story.append(Paragraph("&bull; <b>Item Condition:</b> To be eligible for a return, the item must be unused, in its original packaging, and in the same condition that you received it.", bullet_style))
    story.append(Paragraph("&bull; <b>Proof of Purchase:</b> Your return request must include the original receipt or proof of purchase.", bullet_style))

    story.append(Paragraph("2. Refund Evaluation and Statuses", heading_style))
    story.append(Paragraph("Once we receive your item, we will inspect it and notify you that we have received your returned item. We will immediately update the refund status based on our inspection:", body_style))
    story.append(Paragraph("&bull; <b>Approved:</b> The refund will be initiated to your original method of payment.", bullet_style))
    story.append(Paragraph("&bull; <b>Processed:</b> Funds have been sent back to your financial provider. Please allow 5-10 business days for the credit to appear on your statement.", bullet_style))

    story.append(Paragraph("3. Return Shipping Costs", heading_style))
    story.append(Paragraph("You will be responsible for paying for your own shipping costs for returning your item. Return shipping costs are non-refundable. If you receive a refund, the cost of return shipping will be deducted from your total refund amount.", body_style))

    doc.build(story)

def main():
    print("Generating PDF policy documents...")
    
    # Create in backend/documents/
    create_faq_pdf(DOCS_DIR / "faq.pdf")
    create_shipping_policy_pdf(DOCS_DIR / "shipping_policy.pdf")
    create_return_policy_pdf(DOCS_DIR / "return_policy.pdf")
    
    # Also copy to app/documents/ so RAG can access them directly
    create_faq_pdf(APP_DOCS_DIR / "faq.pdf")
    create_shipping_policy_pdf(APP_DOCS_DIR / "shipping_policy.pdf")
    create_return_policy_pdf(APP_DOCS_DIR / "return_policy.pdf")
    
    print("PDF generation completed successfully.")

if __name__ == "__main__":
    main()
