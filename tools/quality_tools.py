"""
Data Quality Analysis Tools — Clean Output
"""
import pandas as pd
import numpy as np

def generate_data_quality_report(df):
    """Generate comprehensive data quality report"""
    lines = []
    lines.append("Dataset Shape: " + str(df.shape[0]) + " rows × " + str(df.shape[1]) + " columns")
    
    # Missing Values
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]
    lines.append("Missing Values")
    if len(missing_cols) > 0:
        for col, count in missing_cols.items():
            pct = (count / len(df)) * 100
            lines.append(str(col) + ": " + str(count) + " missing (" + str(round(pct,1)) + "%)")
    else:
        lines.append("No missing values found!")
    
    # Duplicates
    lines.append("Duplicate Rows")
    dups = df.duplicated().sum()
    lines.append("Total Duplicates: " + str(dups) + " (" + str(round(dups/len(df)*100,2)) + "%)")
    
    # Outliers
    lines.append("Outlier Analysis (IQR Method)")
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 0:
        for col in num_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            out_count = len(df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)])
            lines.append(str(col) + ": " + str(out_count) + " outliers")
    else:
        lines.append("No numeric columns for outlier detection")
    
    # Data Types
    lines.append("Column Data Types")
    for col, dtype in df.dtypes.items():
        lines.append(str(col) + ": " + str(dtype))
    
    # Memory Usage
    mem = df.memory_usage(deep=True).sum() / 1024
    lines.append("Memory Usage")
    lines.append("Total: " + str(round(mem,2)) + " KB")
    
    # Recommendations
    lines.append("Recommendations")
    if len(missing_cols) > 0:
        lines.append("Impute or drop columns with >40% missing data")
    if dups > 0:
        lines.append("Remove duplicate rows before analysis")
    lines.append("Verify outliers for potential data entry errors")
    lines.append("Check categorical columns for inconsistent labels")
    
    return "\n".join(lines)