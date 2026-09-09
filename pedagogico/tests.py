#import pdfkit into your class
import pdfkit

# Generate PDF from a web URL (maybe only from your project)
pdfkit.from_url('http://google.com', 'out.pdf')
# Generate PDF from a html file.
pdfkit.from_file('file.html', 'out.pdf')
# Generate PDF from a plain html string.
pdfkit.from_string('Hello!', 'out.pdf')

# Save the PDF in a variable
myPdf = pdfkit.from_url('http://google.com', False)