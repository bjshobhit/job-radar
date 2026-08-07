import os
import logging
from typing import Dict

log = logging.getLogger("job-radar")

try:
    from jinja2 import Template
    JINJA_AVAILABLE = True
except ImportError:
    JINJA_AVAILABLE = False

try:
    from weasyprint import HTML
    WEASY_AVAILABLE = True
except ImportError:
    WEASY_AVAILABLE = False


HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(HERE, "..", "resume", "template.html")


def generate_pdf(resume_data: Dict, output_path: str) -> bool:
    """
    Generate ATS-friendly PDF from resume data using HTML template.
    Returns True if PDF was generated successfully, False otherwise.
    """
    if not JINJA_AVAILABLE:
        log.warning("jinja2 not installed — skipping PDF generation")
        return False
    if not WEASY_AVAILABLE:
        log.warning("weasyprint not installed — skipping PDF generation")
        return False

    try:
        with open(TEMPLATE_PATH) as f:
            template_str = f.read()

        template = Template(template_str)
        html_content = template.render(**resume_data)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        HTML(string=html_content).write_pdf(output_path)
        log.info("generated PDF: %s", output_path)
        return True

    except Exception as e:
        log.error("PDF generation failed: %s", e)
        return False
