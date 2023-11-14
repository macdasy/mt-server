from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import PyPDF2, sys, os
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.lib.colors import black, white, blueviolet, darkcyan
from reportlab.graphics.charts.textlabels import Label


# Define a custom style for the footer text
styles = getSampleStyleSheet()
footer_style = styles["Normal"]
footer_style.fontSize = 15
footer_style.spaceAfter = 10

elements = []

# Line Chart
def line_chart(data):
    print(data)

    footer_style.textColor = black
    label = Paragraph("------ Outflow", footer_style)
    elements.append(label)

    footer_style.textColor = darkcyan
    label = Paragraph("------ Inflow", footer_style)
    elements.append(label)
    

    dr_values = [month_data['DR'] for month_data in data[0].values()]
    cr_values = [month_data['CR'] for month_data in data[0].values()]
    values = [ dr_values, cr_values ]
    print(values)

    labels = [[str(value) for value in row] for row in values]

    min_value = min(dr_values) if min(dr_values) < min(cr_values) else min(cr_values)
    max_value = max(dr_values) if max(dr_values) > max(cr_values) else max(cr_values)

    drawing = Drawing(400, 200)

    lc = HorizontalLineChart()
    lc.x = 50
    lc.y = -70
    lc.height = 200
    lc.width = 400
    lc.data = values
    lc.joinedLines = 1
    lc.fillColor = blueviolet
    lc.categoryAxis.categoryNames = data[1]
    lc.categoryAxis.labels.boxAnchor = 'n'
    lc.valueAxis.valueMin = min_value
    lc.valueAxis.valueMax = max_value + 100
    lc.lines[0].strokeColor = black
    lc.lines[1].strokeColor = darkcyan
    lc.lines[0].strokeWidth = 2
    lc.lines[1].strokeWidth = 1.5

    # lc.lineLabelArray = labels
    # lc.lineLabelFormat = 'values'
    drawing.add(lc)

    return drawing

# Create a pie chart
def create_pie_chart(data, total_income, total_outcome):

    if len(data) > 1:
        # Calculate total for percentage calculation
        # total = sum(data[1:])
        total = total_income if data[0] == 'Debit' else total_outcome

        data = data[1:]
        data.append( total - sum(data) )

        # Calculate percentages
        # percentages = [value / total * 100 for value in data if value > 0]

        # Create a drawing
        drawing = Drawing(width=200, height=200)

        # Create a pie chart
        pie_chart = Pie()
        pie_chart.x = 125
        pie_chart.y = -35
        pie_chart.width = 200
        pie_chart.height = 200
        pie_chart.data = data
        pie_chart.labels = [f'Rs. {d:.2f}' for d in data]
        pie_chart.sideLabels = True
        pie_chart.sideLabelsOffset = 0.3

        # Add the pie chart to the drawing
        drawing.add(pie_chart)


    return drawing


def create(data, table_headings, chart_data, total_income, total_outcome, line_chart_data, min_amount, max_amount):
    pdf_path = sys.path[0] + '/table.pdf'
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
    heading_index = 0

    for d in data:

        head_and_table = []
        print(table_headings[heading_index])

        heading_text = table_headings[heading_index].upper()
        heading =  Paragraph(heading_text, getSampleStyleSheet()['Heading1'])
        elements.append(heading)

        table_data = []
        table_data.append([Paragraph(cell, getSampleStyleSheet()['Normal']) for cell in d[0]])
        
        for row in d[1:]:
            table_data.append([Paragraph(str(cell), getSampleStyleSheet()['Normal']) for cell in row])

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
        elements.append( Spacer(1, 50) )

        # elements.append(PageBreak())
        heading_index = heading_index + 1

    

    elements.append(PageBreak())
    heading_text = 'Chart Analysis'
    heading = Paragraph(heading_text, getSampleStyleSheet()['Heading1'])
    elements.append(heading)

    # Pie Chart
    for ch in chart_data: 
        # print(ch)
        heading_text = '> Overall Cash Inflow' if ch[0] == 'Credit' else '> Overall Cash Outflow'
        heading = Paragraph(heading_text, getSampleStyleSheet()['Title'])
        elements.append(heading)

        elements.append(create_pie_chart(ch, total_income, total_outcome))
        # elements.append(PageBreak())
        elements.append( Spacer(1, 80) )

    heading_text = "Monthly Analytics"
    heading = Paragraph(heading_text, getSampleStyleSheet()['Heading1'])
    elements.append(heading)
    
    # Line Chart
    line_ch = line_chart(line_chart_data)
    elements.append(line_ch)
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
    pdf_files = [ sys.path[0] + '/cover.pdf', pdf_path ]

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
    os.remove(pdf_path)


if __name__ == "__main__":
    create()