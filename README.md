# Day 3 — Statistical Analysis Toolkit

A Python project for exploring agent deposit and transaction data in `data/agent_deposits.csv`. The analysis covers central tendency, variability, data validation, and possible outliers.

## Analysis approach

The analysis reads a selected CSV column as numeric data, excludes values that cannot be trusted as numbers, and calculates descriptive statistics over the remaining values. It uses plain Python for the statistical calculations; NumPy is intended only as an independent verification tool.

The current analysis notebook is [`stats_toolkit.ipynb`](stats_toolkit.ipynb). Open it in Jupyter Notebook, JupyterLab, or VS Code and choose **Run All** (or run the cells from top to bottom) to see the current calculations. The dataset is [`data/agent_deposits.csv`](data/agent_deposits.csv); the notebook currently demonstrates the `transactions` column. [`expected_report.txt`](expected_report.txt) is a layout reference. There is not currently a command that writes the requested `output/stats_report.txt`; the notebook is the available way to run the calculations.

## Run the tests

From the project root, run the unittest module with the Python interpreter used for the project:

```bash
python -m unittest -v test_stats_toolkit
```

The test module uses Python's built-in `unittest` framework. Its current test cases are TODO placeholders marked as skipped, so the command runs the test file but does not yet verify the requested calculations.

## Statistical choices

- **Mean and median:** The mean is the arithmetic average. The median is the middle sorted value, or the average of the two middle values for an even number of observations.
- **Mode:** Return all values tied for the highest frequency. If every value occurs once, return an empty list (`[]`) to indicate there is no mode worth reporting.
- **Variance and standard deviation:** Report sample statistics by default, using `n - 1` as the variance denominator. The recorded agent-days cover a limited time period and are treated as observations from a wider process, rather than the complete population of all agent-days of interest. Use the population form (denominator `n`) when the data represents the entire population being described.
- **Quartiles and IQR:** Use Tukey's median-of-halves method: sort the values, take the median as Q2, and find Q1 and Q3 as the medians of the lower and upper halves. For odd-sized data, exclude the central median from both halves. The IQR is `Q3 - Q1`; the conventional outlier fences are `Q1 - 1.5 × IQR` and `Q3 + 1.5 × IQR`. Any NumPy comparison should use the same quartile convention.

## Data validation and assumptions

- The CSV's first row contains column names; reported row numbers refer to physical CSV lines, with the header on row 1.
- Values are accepted only when they can be parsed as finite numbers. Blank cells, malformed text, and non-finite numbers such as `NaN` or infinity are invalid and should be rejected with their original value and a reason.
- Invalid or missing values are not imputed or inferred. In particular, ambiguous strings such as `12,40O` are not corrected automatically.
- IQR outliers are statistical flags for review, not proof of an error or misconduct. Keep valid flagged values in the original-data summary; compare them with an outliers-removed summary separately.
- The sample/population choice depends on the question being asked. This project uses sample statistics as its default assumption, while retaining population formulas for cases where the data is the complete population.

## Project files

- `starter.py` — starter definitions for the analysis functions and analyzer.
- `class_analyzer.py` — class-based analysis implementation.
- `src/day3_stats_toolkit/` — package entry point.
- `stats_toolkit.ipynb` — notebook analysis.
- `test_stats_toolkit.py` — unittest module with TODO test placeholders.
- `test_analyzer.ipynb` — notebook-based analyzer tests.
- `expected_report.txt` — reference layout for a text report.
