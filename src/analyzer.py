from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import pandas as pd


@dataclass
class FileResult:
    file_name: str
    total_revenue: float
    avg_check: float
    orders_count: int


class OrderAnalyzer:
    def __init__(
        self,
        data_dir: Path,
        reports_dir: Path,
        logs_dir: Path,
        summary_report_filename: str,
        error_log_filename: str,
        status_column: str,
        delivered_status_value: str,
        csv_read_kwargs: Optional[Dict[str, Any]] = None,
    ):
        self.data_dir = Path(data_dir)
        self.reports_dir = Path(reports_dir)
        self.logs_dir = Path(logs_dir)

        self.summary_report_path = self.reports_dir / summary_report_filename
        self.error_log_path = self.logs_dir / error_log_filename

        self.status_column = status_column
        self.delivered_status_value = delivered_status_value
        self.csv_read_kwargs = csv_read_kwargs or {}

        self._setup_logger()

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _setup_logger(self) -> None:
        self.logger = logging.getLogger("order_analysis_logger")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

            file_handler = logging.FileHandler(self.error_log_path, encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(fmt)

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.WARNING)
            stream_handler.setFormatter(fmt)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(stream_handler)

    def load_csv(self, file_path: Path) -> pd.DataFrame:
        if file_path.stat().st_size == 0:
            raise ValueError("CSV file is empty.")

        df = pd.read_csv(file_path, **self.csv_read_kwargs)

        required_cols = {self.status_column, "total_amount"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        return df

    def filter_delivered(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df[self.status_column] == self.delivered_status_value].copy()

    def calculate_metrics(self, delivered_df: pd.DataFrame) -> Tuple[float, float, int]:
        orders_count = len(delivered_df)

        total_amount_numeric = pd.to_numeric(delivered_df["total_amount"], errors="coerce")
        total_revenue = float(total_amount_numeric.sum(skipna=True))
        avg_check = float(total_amount_numeric.mean(skipna=True)) if orders_count > 0 else 0.0

        if pd.isna(avg_check):
            avg_check = 0.0

        return total_revenue, avg_check, orders_count

    def process_one_file(self, file_path: Path) -> FileResult:
        df = self.load_csv(file_path)
        delivered = self.filter_delivered(df)
        total_revenue, avg_check, orders_count = self.calculate_metrics(delivered)

        return FileResult(
            file_name=file_path.name,
            total_revenue=total_revenue,
            avg_check=avg_check,
            orders_count=orders_count,
        )

    def process_all_files(self) -> Dict[str, int]:
        csv_files: List[Path] = sorted(self.data_dir.glob("*.csv"))
        processed_results: List[FileResult] = []

        processed_count = 0
        error_count = 0

        for file_path in csv_files:
            try:
                result = self.process_one_file(file_path)
                processed_results.append(result)
                processed_count += 1
            except Exception as e:
                error_count += 1
                self.logger.info(f"SKIP file '{file_path.name}': {type(e).__name__}: {e}")

        rows = []
        for r in processed_results:
            rows.append({
                "file_name": r.file_name,
                "total_revenue": r.total_revenue,
                "avg_check": r.avg_check,
                "orders_count": r.orders_count,
            })

        out_df = pd.DataFrame(rows, columns=["file_name", "total_revenue", "avg_check", "orders_count"])
        out_df.to_csv(self.summary_report_path, index=False, encoding="utf-8")

        return {"processed_count": processed_count, "error_count": error_count}
