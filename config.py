from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

SUMMARY_REPORT_FILENAME = "summary_report.csv"
ERROR_LOG_FILENAME = "errors.log"

STATUS_COLUMN = "status"
DELIVERED_STATUS_VALUE = "Delivered"

CSV_READ_KWARGS = {
    "sep": ",",
    "dtype": "object",
    "keep_default_na": True
}
