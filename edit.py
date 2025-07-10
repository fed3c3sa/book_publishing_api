import fitz  # PyMuPDF
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def image_to_pdf_bytes(image_path, page_size=letter):
    img = Image.open(image_path)
    img_width, img_height = img.size

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=page_size)

    # Scale the image to fit the page
    page_width, page_height = page_size
    aspect = img_width / img_height
    if page_width / aspect <= page_height:
        new_width = page_width
        new_height = page_width / aspect
    else:
        new_height = page_height
        new_width = page_height * aspect

    x = (page_width - new_width) / 2
    y = (page_height - new_height) / 2

    c.drawImage(image_path, x, y, width=new_width, height=new_height)
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

def replace_first_page_with_image(pdf_path, image_path, output_path):
    # Load original PDF and delete first page
    doc = fitz.open(pdf_path)
    doc.delete_page(0)

    # Create a PDF page from the image
    image_pdf_buffer = image_to_pdf_bytes(image_path)

    # Load image-PDF as PyMuPDF document
    image_doc = fitz.open("pdf", image_pdf_buffer)

    # Insert the image-page as first page
    doc.insert_pdf(image_doc, start_at=0)

    # Save final output
    doc.save(output_path)
    doc.close()
    image_doc.close()

# Example usage
replace_first_page_with_image("book_2dff0859-1166-4474-ae2f-cf56c86d0399.pdf", "tmp0m1badsd_cover_2cbea7e1-bc25-4c7c-a7c2-633458a678d2.png", "output_fede_anita.pdf")
