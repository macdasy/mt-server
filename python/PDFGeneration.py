from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import PyPDF2, sys, os

footer_text = "This is the footer text"

# Define a custom style for the footer text
styles = getSampleStyleSheet()
footer_style = styles["Normal"]
footer_style.alignment = 1
footer_style.textColor = colors.black
footer_paragraph = Paragraph(footer_text, footer_style)

footer_elements = []
footer_elements.append(footer_paragraph)

# Define your data
# data = [
#     ["Date", "Description", "Amount", "Reason"],
#     ["2023-10-19", "Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1", "$50.00", "Groceries"],
#     ["2023-10-19", "Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1", "$50.00", "Groceries"],
#     ["2023-10-19", "Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1", "$50.00", "Groceries"],
#     ["2023-10-19", "Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1", "$50.00", "Groceries"],
#     ["2023-10-19", "Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1Expense 1", "$50.00", "Groceries"],
#     ["2023-10-20", "Expense 2", "$30.00", "Dining out"],
#     ["2023-10-21", "Expense 3", "$25.00", "Transportation"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 5", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
#     ["2023-10-22", "Expense 4", "$40.00", "Entertainment"],
# ]
elements = []

def create(data):
    print(data)
    # Create a PDF
    pdf_path = sys.path[0] + '/table.pdf'
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)

    for d in data:
        table_data = []
        table_data.append([Paragraph(cell, getSampleStyleSheet()['Normal']) for cell in d[0]])
        for row in d[1:]:
            table_data.append([Paragraph(cell, getSampleStyleSheet()['Normal']) for cell in row])

        # Define a custom style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C79FE4')),  # Header background color
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

        table = Table(table_data,  colWidths=['18%', '32%', '18%', '32%'])
        table.setStyle(style)

        elements.append(table)
        elements.append(PageBreak())

    # Function to add page numbers
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = "macrotouch.in ________________________________________________ %d" % (page_num + 1)
        # text = "macrotouch.in ------------------------------------------------------------------------------ %d" % (page_num + 1)
        canvas.drawString(130, 50, text)

    # Build the PDF
    pdf.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    # print(sys.path)
    pdf_files = [ sys.path[0] + '/cover.pdf', pdf_path]

    report_dir  = 'Reports'
    os.makedirs(report_dir, exist_ok=True)

    report_path = 'report.pdf'
    output_pdf =  os.path.join(report_dir + '/' + report_path)

    pdf_merger = PyPDF2.PdfMerger()

    for pdf_file in pdf_files: 
        pdf_merger.append(pdf_file)

    with open(output_pdf, "wb") as output_file: 
        pdf_merger.write(output_file)

    pdf_merger.close()


if __name__ == "__main__":
    create()