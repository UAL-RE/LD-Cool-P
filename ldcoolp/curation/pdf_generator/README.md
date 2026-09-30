# PDF Generator for Deposit Agreement

An integrated Python module built using `fpdf2` to dynamically generate professionally formatted and branded University of Arizona (UA) ReDATA Deposit Agreement PDFs.

## Overview & Architecture

The module is structured around three core components:

* **`LayoutConfig`**: Manages document dimensions, padding, margins, and standard letter size layouts in points. Dimensions are defined using an inch-based conversion factor (`1 inch = 72 points`), allowing layout styles to easily align with standard Microsoft Word document formatting conventions.
* **`AccessiblePDF`**: Extends `FPDF` to handle custom font loading (Liberation Serif family), full-width brand color banners, embedded logos, and dynamic page numbering headers and footers.
* **`DepositAgreementBuilder`**: Acts as the document orchestrator, processing structured survey question-and-answer dictionaries (including section headers, info text, and form inputs) and filtering embedded metadata blocks into clean, layout-compliant PDF output.

## Customizable HTML Tag Styles

The generator uses `fpdf2`'s HTML rendering capabilities, governed by the module-level `DEFAULT_HTML_TAG_STYLES` dictionary. This configuration maps standard HTML tags to `TextStyle` objects, enabling precise control over typography and spacing:

* **Supported Tags**: Custom styling is pre-configured for inline and block elements including `b`, `i`, `u`, `a`, `ul`, `li`, `h1`, `h2`, and `h3`.
* **Fine-Grained Controls**: Each tag can customize font size (`font_size_pt`), specific styles (`font_style`), text color (`color`), top/bottom margins (`t_margin`, `b_margin`), and left indentation (`l_margin`).

Can be overriden or extended by passing custom style dictionaries into the underlying `pdf.write_html()` calls if specialized formatting is required.

## Requirements & Assets

The generator expects an `assets/` directory containing the following branding and font files:

* **Logos**: `logo-uofa.png`, `logo-redata.png`
* **Fonts**: Liberation Serif font family

## Usage Example

```python
from pathlib import Path
from pdf_gen import DepositAgreementBuilder

# Initialize the document builder
builder = DepositAgreementBuilder()

# Sample structured data payload
data = {
    "merged_qa": {
        "q1": {
            "questionLabel": "SectionHeader", 
            "questionText": "<h2>1. Deposit Terms</h2>"
        },
        "q2": {
            "questionLabel": "Question",
            "questionText": "<b>Do you agree to the deposit terms?</b>",
            "answer": "Yes"
        }
    },
    "embedded_data": {
        "article_id": "123456",
        "curation_id": "789012",
        "recordedDate": "2026-06-01"
    }
}

# Generate and save the PDF
output_path = Path("output/deposit_agreement.pdf")
builder.generate(data, output_path)
```

## Font License

The **"Liberation Fonts"** is licensed under the **SIL Open Font License**,
Version 1.1. See [License](https://github.com/liberationfonts/liberation-fonts?tab=License-1-ov-file) file for details.
