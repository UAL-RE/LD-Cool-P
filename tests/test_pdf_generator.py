import json
from pathlib import Path

from ldcoolp.config import config_default_dict
from ldcoolp.curation.pdf_generator import DepositAgreementBuilder

# Execution: pytest -s ./tests/test_pdf_generator.py


def test_pdf_generator(tmp_path: Path) -> None:
    print("#####  pdf_generator config check  #####")
    for key, value in config_default_dict["pdf_generator"].items():
        print(f"{key}: {value}; type: {type(value)}")

    data_path = Path(__file__).parent / "test_data" / "test_da_metadata.json"

    # Use pytest's tmp_path fixture for isolated, safe file writing
    output_path = tmp_path / "test_deposit_agreement.pdf"

    with open(data_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    # Create an instance of DepositAgreementBuilder
    builder = DepositAgreementBuilder()

    # Generate the PDF
    pdf_path = builder.generate_pdf(test_data, str(output_path))

    assert pdf_path.exists(), "PDF file was not created."
    assert pdf_path.stat().st_size > 0, "PDF file is empty."
