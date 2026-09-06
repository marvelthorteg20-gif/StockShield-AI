import json
import os
import tempfile

from utils.export_report import export_reports


def test_export_pdf_csv_json():
    payload = {"symbol": "AAPL", "action": "BUY", "score": 69, "levels": [{"name": "Pivot P", "price": 100}]}
    with tempfile.TemporaryDirectory() as tmp_path:
        paths = export_reports(payload, tmp_path, symbol="AAPL")
        assert os.path.isfile(paths["json"])
        assert os.path.isfile(paths["csv"])
        assert os.path.isfile(paths["pdf"])
        with open(paths["json"], encoding="utf-8") as handle:
            data = json.load(handle)
        assert data["symbol"] == "AAPL"
        with open(paths["csv"], encoding="utf-8") as handle:
            content = handle.read()
        assert "symbol" in content
        with open(paths["pdf"], "rb") as handle:
            pdf = handle.read()
        assert pdf.startswith(b"%PDF")
        assert b"%%EOF" in pdf
