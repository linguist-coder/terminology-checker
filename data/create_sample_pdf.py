"""Generate a sample PDF for testing the terminology checker."""

from fpdf import FPDF

pdf = FPDF()
pdf.set_margins(20, 20, 20)
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Helvetica", size=11)

content = [
    ("B", 16, "Installation Guide"),
    ("", 11, ""),
    ("B", 13, "1. Introduction"),
    ("", 11, (
        "This guide describes how to set up and configure the device. "
        "Make sure you read all instructions prior to starting the installation process. "
        "Due to the fact that the installation requires administrator privileges, "
        "ensure that you have the necessary permissions."
    )),
    ("", 11, ""),
    ("B", 13, "2. Prerequisites"),
    ("", 11, (
        "In order to install the software, you must have the following:"
    )),
    ("", 11, "  - A compatible operating system (e.g., Windows 10 or later)"),
    ("", 11, "  - At least 4 GB of RAM"),
    ("", 11, "  - Administrator account"),
    ("", 11, ""),
    ("B", 13, "3. Installation Steps"),
    ("", 11, (
        "Step 1: Start up the installer by clicking on the setup file. "
        "The installer will utilise the default configuration settings."
    )),
    ("", 11, ""),
    ("", 11, (
        "Step 2: On a regular basis, the installer checks for updates. "
        "If an update is available, it will be installed subsequent to the main installation."
    )),
    ("", 11, ""),
    ("", 11, (
        "Step 3: After the installation is complete, set up the network connection. "
        "Make sure the device is connected to the network prior to proceeding."
    )),
    ("", 11, ""),
    ("B", 13, "4. Troubleshooting"),
    ("", 11, (
        "If the installation fails, shut down the device and restart the the installer. "
        "For additional support, i.e., contacting the help desk, refer to the support section."
    )),
]

page_width = pdf.w - pdf.l_margin - pdf.r_margin
for style, size, text in content:
    pdf.set_font("Helvetica", style=style, size=size)
    if text:
        pdf.multi_cell(page_width, 7, text)
    else:
        pdf.ln(4)

out = "data/sample_document.pdf"
pdf.output(out)
print(f"Created: {out}")
