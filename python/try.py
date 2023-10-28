import PyPDF2

# List of PDF files to combine (replace with your file paths)
pdf_files = ["./cover.pdf", "../table.pdf"]

# Output PDF file
output_pdf = "final.pdf"

# Create a PDF merger
pdf_merger = PyPDF2.PdfMerger()

# Add each PDF file to the merger
for pdf_file in pdf_files:
    pdf_merger.append(pdf_file)

# Write the merged PDF to the output file
with open(output_pdf, "wb") as output_file:
    pdf_merger.write(output_file)

# Close the merger
pdf_merger.close()

print(f"PDFs combined and saved as '{output_pdf}'")
