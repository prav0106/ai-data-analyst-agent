"""
Data Tools for AI Data Analyst Agent
"""
import pandas as pd
import numpy as np
from langchain_core.tools import tool

# Global storage for dataframes
_dataframes = {}


class DataTools:
    """Collection of data manipulation tools"""
    
    def __init__(self):
        self.dataframes = _dataframes
    
    def load_csv_direct(self, file_path: str, name: str = "data") -> str:
        """Direct method to load CSV (not a tool)"""
        try:
            df = pd.read_csv(file_path)
            _dataframes[name] = df
            return f"Loaded {name} with {len(df)} rows and {len(df.columns)} columns. Columns: {list(df.columns)}"
        except Exception as e:
            return f"Error loading CSV: {str(e)}"
    
    def get_tools(self):
        """Return all tools"""
        
        @tool
        def get_data_info(name: str = "uploaded_data") -> str:
            """Get basic information about the loaded dataset including columns, types, and missing values."""
            if name not in _dataframes:
                return f"Data '{name}' not found. Available: {list(_dataframes.keys())}"
            
            df = _dataframes[name]
            info = f"📊 Dataset: {name}\n"
            info += f"━━━━━━━━━━━━━━━━━━\n"
            info += f"• Rows: {len(df)}\n"
            info += f"• Columns: {len(df.columns)}\n\n"
            info += f"📋 Column Details:\n"
            
            for col in df.columns:
                dtype = df[col].dtype
                nulls = df[col].isnull().sum()
                unique = df[col].nunique()
                info += f"• {col}: {dtype} (nulls: {nulls}, unique: {unique})\n"
            
            return info
        
        @tool
        def clean_data(name: str = "uploaded_data", strategy: str = "auto") -> str:
            """Clean the dataset by handling missing values. strategy: 'auto' or 'drop'"""
            if name not in _dataframes:
                return f"Data '{name}' not found."
            
            df = _dataframes[name].copy()
            initial_rows = len(df)
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            
            if strategy == "auto":
                for col in numeric_cols:
                    df[col].fillna(df[col].median(), inplace=True)
                for col in categorical_cols:
                    if len(df[col].mode()) > 0:
                        df[col].fillna(df[col].mode()[0], inplace=True)
                    else:
                        df[col].fillna("Unknown", inplace=True)
            elif strategy == "drop":
                df.dropna(inplace=True)
            
            _dataframes[name] = df
            rows_removed = initial_rows - len(df)
            
            return f"✅ Data cleaned!\n• Rows removed: {rows_removed}\n• Remaining rows: {len(df)}"
        
        @tool
        def get_descriptive_stats(name: str = "uploaded_data") -> str:
            """Get descriptive statistics (mean, median, std, min, max) for numeric columns."""
            if name not in _dataframes:
                return f"Data '{name}' not found."
            
            df = _dataframes[name]
            stats = df.describe().round(2)
            return f"📈 Descriptive Statistics:\n```\n{stats.to_string()}\n```"
        
        @tool
        def find_correlations(name: str = "uploaded_data", threshold: float = 0.5) -> str:
            """Find correlations between numeric variables in the dataset."""
            if name not in _dataframes:
                return f"Data '{name}' not found."
            
            df = _dataframes[name]
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.shape[1] < 2:
                return "Need at least 2 numeric columns for correlation analysis."
            
            corr_matrix = numeric_df.corr()
            
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) >= threshold:
                        strong_corr.append({
                            'var1': corr_matrix.columns[i],
                            'var2': corr_matrix.columns[j],
                            'correlation': round(corr_matrix.iloc[i, j], 3)
                        })
            
            result = f"🔗 Correlation Analysis:\n"
            result += f"```\n{corr_matrix.round(3).to_string()}\n```\n"
            
            if strong_corr:
                result += f"\n⚡ Strong Correlations (|r| >= {threshold}):\n"
                for item in sorted(strong_corr, key=lambda x: abs(x['correlation']), reverse=True):
                    result += f"• {item['var1']} ↔ {item['var2']}: {item['correlation']}\n"
            
            return result
        
        return [get_data_info, clean_data, get_descriptive_stats, find_correlations]