from config import (
    DATA_DIR,
    REPORTS_DIR,
    LOGS_DIR,
    SUMMARY_REPORT_FILENAME,
    ERROR_LOG_FILENAME,
    STATUS_COLUMN,
    DELIVERED_STATUS_VALUE,
    CSV_READ_KWARGS,
)

from src.analyzer import OrderAnalyzer


def main() -> None:
    analyzer = OrderAnalyzer(
        data_dir=DATA_DIR,
        reports_dir=REPORTS_DIR,
        logs_dir=LOGS_DIR,
        summary_report_filename=SUMMARY_REPORT_FILENAME,
        error_log_filename=ERROR_LOG_FILENAME,
        status_column=STATUS_COLUMN,
        delivered_status_value=DELIVERED_STATUS_VALUE,
        csv_read_kwargs=CSV_READ_KWARGS,
    )

    stats = analyzer.process_all_files()

    print(f"Processed files: {stats['processed_count']}")
    print(f"Files with errors: {stats['error_count']}")
    print("Done. Check reports/summary_report.csv and logs/errors.log (if any errors).")


if __name__ == "__main__":
    main()
