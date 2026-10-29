import csv
import math
from pathlib import Path


class StatisticsAnalyzer:
    """Descriptive statistics for one numeric CSV column.

    Quartile method: median-of-halves (Tukey's hinges). Q2 is the median;
    Q1 and Q3 are the medians of the lower and upper halves. For odd n the
    median itself is excluded from both halves.
    Variance and standard deviation default to the sample (n - 1) form.
    Empty data returns 0.0 / [] for every statistic.
    """

    def __init__(self, values: list[float],
                 errors: list[tuple[int, str]] | None = None) -> None:
        self.values = list(values)
        self.errors = list(errors) if errors is not None else []
        self._sorted_values = sorted(self.values)
        self._n = len(self._sorted_values)

    @classmethod
    def from_csv(cls, path: Path, column: str) -> "StatisticsAnalyzer":
        valid_floats: list[float] = []
        errors: list[tuple[int, str]] = []

        with open(path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None or column not in reader.fieldnames:
                raise KeyError(f"Column '{column}' not found in {Path(path).name}")

            for row_idx, row in enumerate(reader, start=2):
                raw_value = row.get(column)
                if raw_value is None or raw_value.strip() == "":
                    errors.append((row_idx, "Missing value"))
                    continue

                clean_value = raw_value.split(":", 1)[-1].strip()
                try:
                    number = float(clean_value)
                except ValueError:
                    errors.append((row_idx, f"Could not convert '{clean_value}' to float"))
                    continue
                if not math.isfinite(number):
                    errors.append((row_idx, f"Non-finite value: '{clean_value}'"))
                    continue
                valid_floats.append(number)

        return cls(valid_floats, errors)

    # --- Core statistics ---
    def mean(self) -> float:
        return sum(self._sorted_values) / self._n if self._n else 0.0

    @staticmethod
    def _median_of(sorted_data: list[float]) -> float:
        if not sorted_data:
            return 0.0
        mid = len(sorted_data) // 2
        if len(sorted_data) % 2 == 1:
            return sorted_data[mid]
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2.0

    def median(self) -> float:
        return self._median_of(self._sorted_values)

    def mode(self) -> list[float]:
        """Return all most-frequent values (sorted), or [] if none repeat."""
        if self._n == 0:
            return []
        counts: dict[float, int] = {}
        for num in self._sorted_values:
            counts[num] = counts.get(num, 0) + 1
        max_freq = max(counts.values())
        if max_freq == 1:
            return []
        return [num for num, count in counts.items() if count == max_freq]

    def variance(self, sample: bool = True) -> float:
        """Sample (n-1) or population (n) variance; 0.0 if undefined."""
        if self._n < (2 if sample else 1):
            return 0.0
        avg = self.mean()
        total = sum((x - avg) ** 2 for x in self._sorted_values)
        return total / (self._n - 1 if sample else self._n)

    def std_dev(self, sample: bool = True) -> float:
        return self.variance(sample=sample) ** 0.5

    def quartiles(self) -> tuple[float, float, float]:
        """Return (Q1, Q2, Q3) using the median-of-halves method."""
        if self._n == 0:
            return 0.0, 0.0, 0.0
        if self._n == 1:
            v = self._sorted_values[0]
            return v, v, v

        mid_idx = self._n // 2
        lower_half = self._sorted_values[:mid_idx]
        upper_half = self._sorted_values[mid_idx + (self._n % 2):]
        return (self._median_of(lower_half), self.median(),
                self._median_of(upper_half))

    def iqr_outliers(self, k: float = 1.5) -> dict:
        q1, _, q3 = self.quartiles()
        iqr_val = q3 - q1
        lower_fence = q1 - k * iqr_val
        upper_fence = q3 + k * iqr_val
        return {
            "iqr": iqr_val,
            "lower_fence": lower_fence,
            "upper_fence": upper_fence,
            "lower_outliers": [x for x in self.values if x < lower_fence],
            "upper_outliers": [x for x in self.values if x > upper_fence],
        }

    # --- Pipeline methods ---
    def summary(self, k: float = 1.5) -> dict:
        q1, q2, q3 = self.quartiles()
        out = self.iqr_outliers(k)
        return {
            "count": self._n,
            "mean": self.mean(),
            "median": q2,
            "mode": self.mode(),
            "variance_sample": self.variance(sample=True),
            "std_dev_sample": self.std_dev(sample=True),
            "q1": q1,
            "q3": q3,
            "iqr": out["iqr"],
            "lower_fence": out["lower_fence"],
            "upper_fence": out["upper_fence"],
            "lower_outliers": out["lower_outliers"],
            "upper_outliers": out["upper_outliers"],
            "error_count": len(self.errors),
        }

    def without_outliers(self, k: float = 1.5) -> "StatisticsAnalyzer":
        out = self.iqr_outliers(k)
        lo, hi = out["lower_fence"], out["upper_fence"]
        clean_values = [x for x in self.values if lo <= x <= hi]
        return StatisticsAnalyzer(clean_values, errors=self.errors)

    def report(self, k: float = 1.5) -> None:
        s = self.summary(k)

        def fmt(x: float) -> str:
            return "n/a" if math.isnan(x) else f"{x:.4f}"

        print("=" * 45)
        print("          STATISTICAL METRICS REPORT         ")
        print("=" * 45)
        print(f"Total Elements Scored : {s['count']}")
        print(f"Arithmetic Mean       : {fmt(s['mean'])}")
        print(f"Median Value (Q2)     : {fmt(s['median'])}")
        print(f"Dataset Mode(s)       : {s['mode'] if s['mode'] else 'None Worth Reporting'}")
        print("-" * 45)
        print(f"Sample Variance       : {fmt(s['variance_sample'])}")
        print(f"Sample Std Deviation  : {fmt(s['std_dev_sample'])}")
        print("-" * 45)
        print(f"Quartile 1 (25th)     : {fmt(s['q1'])}")
        print(f"Quartile 3 (75th)     : {fmt(s['q3'])}")
        print(f"Interquartile Range   : {fmt(s['iqr'])}")
        print(f"Fences (k={k})      : [{fmt(s['lower_fence'])}, {fmt(s['upper_fence'])}]")
        print("-" * 45)
        print(f"Low Boundary Outliers : Count: {len(s['lower_outliers'])} {s['lower_outliers']}")
        print(f"High Boundary Outliers: Count: {len(s['upper_outliers'])} {s['upper_outliers']}")
        print(f"Parsing Fault Logs    : {s['error_count']} rows skipped.")
        print("=" * 45)


rpt = StatisticsAnalyzer.from_csv(DATA_PATH, "transactions")
print(rpt)



