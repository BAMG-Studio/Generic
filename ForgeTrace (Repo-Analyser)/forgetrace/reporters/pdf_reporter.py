"""PDF Reporter - Author: Peter"""
from pathlib import Path

class PDFReporter:
    def __init__(self, findings, output_dir, config):
        self.findings = findings
        self.output_dir = Path(output_dir)
        self.config = config
        
    def generate(self):
        try:
            from weasyprint import HTML
            html_file = self.output_dir / "report.html"
            pdf_file = self.output_dir / "report.pdf"
            
            if html_file.exists():
                HTML(filename=str(html_file)).write_pdf(str(pdf_file))
        except ImportError:
            print("WeasyPrint not available. Skipping PDF generation.")
        except Exception as e:
            print(f"PDF generation failed: {e}")
