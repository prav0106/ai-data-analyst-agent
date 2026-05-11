"""
Analysis Tools for AI Data Analyst Agent
"""
import pandas as pd
import numpy as np
from langchain_core.tools import tool
from tools.data_tools import _dataframes


class AnalysisTools:
    """Collection of analysis tools"""
    
    def __init__(self):
        pass
    
    def set_dataframes(self, dataframes):
        pass  # Using global _dataframes now
    
    def get_tools(self):
        """Return all analysis tools"""
        
        @tool
        def analyze_trends(column: str, time_column: str, name: str = "uploaded_data") -> str:
            """Analyze trends of a column over time. Provide column name and time_column name."""
            if name not in _dataframes:
                return f"Data '{name}' not found."
            
            df = _dataframes[name]
            
            if time_column not in df.columns or column not in df.columns:
                return f"Column(s) not found. Available: {list(df.columns)}"
            
            df_sorted = df.sort_values(time_column)
            result = f"📈 Trend Analysis: {column} over {time_column}\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            result += f"• First Value: {df_sorted[column].iloc[0]}\n"
            result += f"• Last Value: {df_sorted[column].iloc[-1]}\n"
            
            try:
                change = ((df_sorted[column].iloc[-1] - df_sorted[column].iloc[0]) / df_sorted[column].iloc[0] * 100)
                result += f"• Change: {change:.2f}%\n"
            except:
                pass
            
            result += f"• Max: {df_sorted[column].max()}\n"
            result += f"• Min: {df_sorted[column].min()}\n"
            result += f"• Average: {df_sorted[column].mean():.2f}\n"
            
            return result
        
        @tool
        def group_analysis(group_by: str, agg_column: str, agg_func: str = "mean", name: str = "uploaded_data") -> str:
            """Group data by a column and aggregate another column. agg_func: mean, sum, count, min, max."""
            if name not in _dataframes:
                return f"Data '{name}' not found."
            
            df = _dataframes[name]
            
            if group_by not in df.columns or agg_column not in df.columns:
                return f"Column(s) not found. Available: {list(df.columns)}"
            
            grouped = df.groupby(group_by)[agg_column].agg(agg_func).sort_values(ascending=False)
            
            result = f"📊 Group Analysis: {agg_column} by {group_by}\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            result += f"• Groups: {len(grouped)}\n"
            result += f"• Top 10 groups:\n"
            result += f"```\n{grouped.head(10).to_string()}\n```\n"
            
            return result
        
        @tool
        def detect_outliers(column: str, name: str = "uploaded_data") -> str:
            """Detect outliers in a numeric column using IQR method."""
            if name not in _dataframes:
                return f"Data '{name}' not found."
            
            df = _dataframes[name]
            
            if column not in df.columns:
                return f"Column '{column}' not found."
            
            col_data = df[column].dropna()
            
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            
            result = f"🔍 Outlier Detection: {column}\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            result += f"• Lower Bound: {lower_bound:.2f}\n"
            result += f"• Upper Bound: {upper_bound:.2f}\n"
            result += f"• Outliers Found: {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)\n"
            
            return result
        
        @tool
        def generate_insights(name: str = "uploaded_data") -> str:
            """Automatically generate key insights from the dataset."""
            if name not in _dataframes:
                return f"Data '{name}' not found."
            
            df = _dataframes[name]
            
            insights = ["🧠 **Automated Insights:**\n", "━━━━━━━━━━━━━━━━━━━━━\n"]
            insights.append(f"• Dataset has {len(df)} rows and {len(df.columns)} columns\n")
            
            missing = df.isnull().sum()
            missing_cols = missing[missing > 0]
            if len(missing_cols) > 0:
                insights.append(f"⚠️ Columns with missing values: {', '.join(missing_cols.index.tolist())}\n")
            else:
                insights.append("✅ No missing values in dataset\n")
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                insights.append(f"\n📊 Numeric columns ({len(numeric_cols)}): {', '.join(numeric_cols.tolist())}\n")
            
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(cat_cols) > 0:
                insights.append(f"\n🏷️ Categorical columns ({len(cat_cols)}): {', '.join(cat_cols.tolist())}\n")
            
            return "".join(insights)
        
        return [analyze_trends, group_analysis, detect_outliers, generate_insights]