from pathlib import Path
import pandas as pd
import numpy as np
import os

# =========================
# CONFIG
# =========================
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"

FILES = {
    "df_input": DATA_DIR / "input_metrics_processed.csv",
    "df_orders": DATA_DIR / "orders_metrics_processed.csv",
}

# =========================
# DATA LOADER
# =========================
class DataLoader:
    def __init__(self, paths: dict):
        self.paths = paths

    def load(self):
        df_input = pd.read_csv(self.paths["df_input"])
        df_orders = pd.read_csv(self.paths["df_orders"])
        return df_input, df_orders

# =========================
# PREPROCESSOR
# =========================
class Preprocessor:
    def __init__(self, df_input: pd.DataFrame, df_orders: pd.DataFrame):
        self.df_input = df_input.copy()
        self.df_orders = df_orders.copy()

    def process(self):
        # Standardize column names
        self.df_input.columns = [c.upper() for c in self.df_input.columns]
        self.df_orders.columns = [c.upper() for c in self.df_orders.columns]

        # Fill nulls
        self.df_input = self.df_input.fillna(0)
        self.df_orders = self.df_orders.fillna(0)

        return self.df_input, self.df_orders

# =========================
# INSIGHT DETECTORS
# =========================
class AnomalyDetector:
    def detect(self, df: pd.DataFrame):
        insights = []

        grouped = df.sort_values("NW_AGO").groupby(["CITY", "METRIC"])

        for (city, metric), group in grouped:
            group = group.sort_values("NW_AGO")
            values = group["MVALUE"].values

            for i in range(1, len(values)):
                change = (values[i] - values[i-1]) / (values[i-1] + 1e-6)
                if abs(change) > 0.10:
                    insights.append(f"Anomaly in {city} - {metric}: {change:.2%}")

        return insights


class TrendDetector:
    def detect(self, df: pd.DataFrame):
        insights = []

        grouped = df.sort_values("NW_AGO").groupby(["CITY", "METRIC"])

        for (city, metric), group in grouped:
            group = group.sort_values("NW_AGO")
            values = group["MVALUE"].values

            declines = 0
            for i in range(1, len(values)):
                if values[i] < values[i-1]:
                    declines += 1
                    if declines >= 3:
                        insights.append(f"Downward trend in {city} - {metric}")
                        break
                else:
                    declines = 0

        return insights


class BenchmarkDetector:
    def detect(self, df: pd.DataFrame):
        insights = []

        if "COUNTRY" not in df.columns:
            return insights

        grouped = df.groupby(["COUNTRY", "METRIC"])

        for (country, metric), group in grouped:
            mean_val = group["MVALUE"].mean()

            for _, row in group.iterrows():
                if abs(row["MVALUE"] - mean_val) / (mean_val + 1e-6) > 0.15:
                    insights.append(
                        f"Benchmark deviation in {row['CITY']} ({country}) - {metric}"
                    )

        return insights


class CorrelationDetector:
    def detect(self, df: pd.DataFrame):
        insights = []

        pivot = df.pivot_table(
            index=["CITY", "NW_AGO"],
            columns="METRIC",
            values="MVALUE"
        ).fillna(0)

        corr = pivot.corr()

        for col1 in corr.columns:
            for col2 in corr.columns:
                if col1 != col2:
                    val = corr.loc[col1, col2]
                    if abs(val) > 0.7:
                        insights.append(f"High correlation between {col1} and {col2}: {val:.2f}")

        return list(set(insights))


class OpportunityDetector:
    def detect(self, df: pd.DataFrame):
        insights = []

        grouped = df.groupby(["CITY", "METRIC"])

        for (city, metric), group in grouped:
            avg = group["MVALUE"].mean()
            if avg < group["MVALUE"].quantile(0.25):
                insights.append(f"Opportunity in {city} - {metric}: below performance")

        return insights


# =========================
# REPORT GENERATOR
# =========================
class ReportGenerator:
    def generate(self, insights_dict: dict, filename: str = None, directory: str = None):
        report = []

        for category, insights in insights_dict.items():
            report.append(f"\n=== {category.upper()} ===")
            if insights:
                report.extend(insights)
            else:
                report.append("No insights found")

        report_text = "\n".join(report)

        # Save to file if filename is provided
        if filename:
            # If directory is provided, join it with filename
            if directory:
                os.makedirs(directory, exist_ok=True)  # create folder if it doesn't exist
                filepath = os.path.join(directory, filename)
            else:
                filepath = filename

            with open(filepath, "w", encoding="utf-8") as file:
                file.write(report_text)

        return report_text


# =========================
# MAIN PIPELINE
# =========================
class InsightPipeline:
    def __init__(self, paths):
        self.loader = DataLoader(paths)

    def run(self):
        df_input, df_orders = self.loader.load()

        pre = Preprocessor(df_input, df_orders)
        df_input, df_orders = pre.process()

        detectors = {
            "anomalies": AnomalyDetector(),
            "trends": TrendDetector(),
            "benchmark": BenchmarkDetector(),
            "correlations": CorrelationDetector(),
            "opportunities": OpportunityDetector(),
        }

        insights = {}

        for name, detector in detectors.items():
            insights[name] = detector.detect(df_input)

        report = ReportGenerator().generate(
            insights_dict=insights,
            filename="report.txt",
            directory="reports/output"
)

        print(report)


if __name__ == "__main__":
    pipeline = InsightPipeline(FILES)
    pipeline.run()
