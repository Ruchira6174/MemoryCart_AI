import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

docs = {
    "faq.pdf": {
        "title": "MemoryCart AI E-Commerce FAQ",
        "content": """
Account FAQs
Creating and managing your MemoryCart account is designed to be simple and seamless. By having an account, you can track orders, save shipping addresses, view past purchase history, and manage your payment methods all in one place. If you are experiencing trouble logging into your MemoryCart account, the most common issue is an incorrect password. Please use the 'Forgot Password' link on the login page to initiate a password reset. You will receive an email containing a secure link to create a new password. If you do not receive the password reset email within 15 minutes, please check your spam or junk folder. 

Payment FAQs
MemoryCart accepts a wide variety of secure payment methods to accommodate our global customer base. We currently accept all major credit and debit cards, including Visa, MasterCard, American Express, and Discover. Additionally, we support digital wallets such as Apple Pay, Google Pay, and PayPal for faster checkout. For larger purchases, we also offer "Buy Now, Pay Later" options through our partnered financing services. All transactions are securely encrypted and processed through industry-leading payment gateways to ensure your financial data remains safe.

Order FAQs
Placing an order on MemoryCart is straightforward. Browse our catalog, add your desired items to your digital cart, and proceed to checkout. During checkout, you will be prompted to enter your shipping details, select a shipping method, and choose a payment option. Once your order is successfully placed, you will receive an automated email confirmation containing your unique order number and a summary of your purchased items. Orders placed on MemoryCart can be modified or completely canceled within a strict 2-hour window after the order is placed. 

Refund FAQs
If you are not satisfied with your purchase, you may be eligible for a refund. Refunds are typically processed within 5 to 7 business days after we receive and inspect your returned item at our facility. The refunded amount will be credited back to your original method of payment. Please note that shipping charges are non-refundable unless the return is due to an error on our part, such as a defective or incorrect item. If you do not see the refund in your account after 7 business days, we recommend contacting your bank or credit card company.

Support FAQs
Our dedicated customer support team is available 24/7 to assist you with any questions or concerns. The fastest way to get help is through our intelligent MemoryCart AI chat interface, located at the bottom right of your screen. You can also reach us via email at support@memorycart.ai. We strive to respond to all email inquiries within 24 hours. For urgent matters, please use the live chat feature.
        """
    },
    "shipping_policy.pdf": {
        "title": "MemoryCart AI Shipping Policy",
        "content": """
Processing time
At MemoryCart, we pride ourselves on rapid fulfillment. All orders are processed and prepared for shipment within 24 to 48 business hours after payment confirmation. Please be aware that our fulfillment centers operate Monday through Friday. Orders are not processed, shipped, or delivered on weekends or national holidays. During periods of high demand, such as major sales events or the holiday season, order processing may be delayed by an additional 1 to 2 business days. We will notify you via email if there is a significant delay in the processing of your order.

Domestic shipping
We offer several domestic shipping options to suit your needs. Standard domestic shipping is absolutely free for all orders over $50. For orders under the $50 threshold, a flat rate standard shipping fee of $5.99 applies. Standard domestic delivery typically takes 3 to 5 business days. We partner with reliable national carriers to ensure your packages arrive safely and on time. Deliveries are typically made between 8 AM and 8 PM local time.

International shipping
MemoryCart currently ships to a select number of international destinations, including Canada, the United Kingdom, and Australia. International shipping allows our global customers to enjoy our products. Please note that international shipments are subject to customs clearance procedures, which can cause delays beyond our original delivery estimates. Furthermore, international customers are entirely responsible for paying any applicable import duties, taxes, or customs fees levied by their local government. MemoryCart cannot predict or cover these additional costs.

Tracking orders
As soon as your order is packed and leaves our fulfillment center, you will receive a shipping confirmation email containing a unique tracking link. You can click this link to view real-time updates regarding your package's transit status. Additionally, if you have a MemoryCart account, you can log in and view your tracking information directly from the 'My Orders' section of your user dashboard.

Delays
While we strive for punctuality, shipments can occasionally be delayed due to unforeseen circumstances such as extreme weather, natural disasters, or logistical bottlenecks within the carrier's network. If your tracking information has not updated for more than 48 hours past your expected delivery date, please reach out to our customer support team so we can investigate the delay on your behalf.

Lost packages
If your tracking information indicates that your package was delivered, but you cannot locate it, please check your surroundings, porches, and with your neighbors. If the package remains missing after 48 hours from the "delivered" timestamp, contact us immediately. We will launch a formal investigation with the shipping carrier. If the package is officially deemed lost in transit, we will issue a full replacement or a complete refund, depending on your preference and product availability.
        """
    },
    "return_policy.pdf": {
        "title": "MemoryCart AI Return and Refund Policy",
        "content": """
Return eligibility
We want every MemoryCart customer to be fully satisfied with their purchase. If you receive an item that does not meet your expectations, you may be eligible to return it. To qualify for a standard return, the item must be completely unused, unworn, unwashed, and in its original, pristine condition. It must also be securely placed in the original packaging, with all factory seals intact and all original tags still attached. Items that show signs of wear, alteration, or damage caused by the customer will not be accepted for return.

Return window
You have exactly 30 calendar days from the date your package is marked as "Delivered" to initiate a return. Returns requested after this 30-day window has expired will be politely declined. We encourage you to inspect your items immediately upon arrival to ensure they meet your requirements and to contact us promptly if you decide to make a return. Initiating a return is simple. You can log into your MemoryCart account, navigate to 'Order History', select the item you wish to return, and follow the on-screen prompts. 

Refund timeline
Once your returned package arrives at our processing center, it will undergo a thorough inspection by our quality assurance team to verify its condition. This inspection process can take up to 3 business days. If the return is approved, we will immediately initiate a refund. After a refund has been approved and processed on our end, it may take additional time for the funds to appear in your account. Generally, refunds credited to major credit cards take between 5 to 7 business days to post, depending on your bank's specific processing cycles. 

Exchanges
We currently only offer direct exchanges for items that arrive defective, damaged, or if you received an incorrect item due to a fulfillment error on our part. If you simply want a different color, size, or model, you will need to process a standard return for a refund and place a new, separate order for the desired item. For defective item exchanges, please contact our support team within 14 days of delivery with photographic evidence of the defect.

Damaged products
If your product arrives visibly damaged due to mishandling during transit, please take clear photos of both the damaged product and the damaged exterior packaging. Contact customer support within 48 hours of delivery with these photos. We will immediately arrange for a replacement to be sent out to you at no additional cost, or offer a full refund if the item is out of stock.

Non-returnable items
For reasons of hygiene, safety, and digital rights, certain product categories are strictly non-returnable. These include digital gift cards and store credit, downloadable software products, digital keys, and media. Additionally, personalized, engraved, or custom-made items cannot be returned. Perishable goods or intimate apparel are also excluded. Any item heavily discounted and explicitly marked as "Final Sale" at the time of purchase is completely non-returnable.
        """
    }
}

def generate_pdfs(output_dir="documents"):
    os.makedirs(output_dir, exist_ok=True)
    styles = getSampleStyleSheet()

    # Create custom styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], spaceBefore=15, spaceAfter=10)
    body_style = ParagraphStyle('CustomBody', parent=styles['BodyText'], spaceAfter=10, leading=14)

    for filename, data in docs.items():
        filepath = os.path.join(output_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []

        # Add Title
        story.append(Paragraph(data["title"], title_style))

        # Process the content
        blocks = data["content"].strip().split("\n\n")
        for block in blocks:
            lines = block.strip().split("\n", 1)
            # Ensure proper line formatting
            story.append(Paragraph(lines[0], heading_style))
            
            if len(lines) > 1:
                body_text = lines[1].replace("\n", " ")
                story.append(Paragraph(body_text, body_style))

        # Build PDF
        doc.build(story)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    generate_pdfs()
