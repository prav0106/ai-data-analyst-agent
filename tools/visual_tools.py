"""
Visualization Tools for AI Data Analyst Agent
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from io import BytesIO
from typing import Optional

class VisualTools:
    """Collection of visualization tools"""
    
    def __init__(self):
        self.dataframes = {}
        self.figures = []
    
    def set_dataframes(self, dataframes: dict):
        self.dataframes = dataframes
    
    def create_histogram(self, name: str, column: str, bins: int = 30) -> str:
        """Create a histogram for a numeric column."""
        if name not in self.dataframes:
            return f"Data '{name}' not found."
        
        df = self.dataframes[name]
        
        if column not in df.columns:
            return f"Column '{column}' not found."
        
        fig = px.histogram(df, x=column, nbins=bins, title=f"Distribution of {column}")
        fig.update_layout(xaxis_title=column, yaxis_title="Frequency")
        
        # Save figure
        self.figures.append(("histogram", column, fig))
        
        return f"✅ Created histogram for '{column}' with {bins} bins"
    
    def create_scatter(self, name: str, x_col: str, y_col: str, color_col: Optional[str] = None) -> str:
        """Create a scatter plot."""
        if name not in self.dataframes:
            return f"Data '{name}' not found."
        
        df = self.dataframes[name]
        
        if x_col not in df.columns or y_col not in df.columns:
            return f"Column(s) not found."
        
        if color_col:
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"{x_col} vs {y_col}")
        else:
            fig = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
        
        fig.update_layout(xaxis_title=x_col, yaxis_title=y_col)
        
        self.figures.append(("scatter", f"{x_col}_vs_{y_col}", fig))
        
        return f"✅ Created scatter plot: {x_col} vs {y_col}"
    
    def create_bar_chart(self, name: str, x_col: str, y_col: str, top_n: int = 10) -> str:
        """Create a bar chart."""
        if name not in self.dataframes:
            return f"Data '{name}' not found."
        
        df = self.dataframes[name]
        
        # Group and get top N
        grouped = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(top_n)
        
        fig = px.bar(x=grouped.index, y=grouped.values, title=f"Top {top_n} {x_col} by {y_col}")
        fig.update_layout(xaxis_title=x_col, yaxis_title=y_col)
        
        self.figures.append(("bar", f"{x_col}_by_{y_col}", fig))
        
        return f"✅ Created bar chart: Top {top_n} {x_col}"
    
    def create_line_chart(self, name: str, x_col: str, y_col: str, title: str = None) -> str:
        """Create a line chart for time series data."""
        if name not in self.dataframes:
            return f"Data '{name}' not found."
        
        df = self.dataframes[name]
        
        if x_col not in df.columns or y_col not in df.columns:
            return f"Column(s) not found."
        
        df_sorted = df.sort_values(x_col)
        
        fig = px.line(df_sorted, x=x_col, y=y_col, title=title or f"{y_col} over {x_col}")
        fig.update_layout(xaxis_title=x_col, yaxis_title=y_col)
        
        self.figures.append(("line", f"{y_col}_over_{x_col}", fig))
        
        return f"✅ Created line chart: {y_col} over {x_col}"
    
    def create_correlation_heatmap(self, name: str) -> str:
        """Create a correlation heatmap."""
        if name not in self.dataframes:
            return f"Data '{name}' not found."
        
        df = self.dataframes[name]
        numeric_df = df.select_dtypes(include=['number'])
        
        corr = numeric_df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 8}
        ))
        
        fig.update_layout(title="Correlation Heatmap", width=700, height=700)
        
        self.figures.append(("heatmap", "correlation", fig))
        
        return f"✅ Created correlation heatmap"
    
    def create_box_plot(self, name: str, column: str, group_by: str = None) -> str:
        """Create a box plot."""
        if name not in self.dataframes:
            return f"Data '{name}' not found."
        
        df = self.dataframes[name]
        
        if group_by:
            fig = px.box(df, x=group_by, y=column, title=f"Box Plot: {column} by {group_by}")
        else:
            fig = px.box(df, y=column, title=f"Box Plot: {column}")
        
        self.figures.append(("box", column, fig))
        
        return f"✅ Created box plot for '{column}'"
    
    def get_all_figures(self) -> list:
        """Get all generated figures."""
        return self.figures
    
    def export_html(self, filename: str = "dashboard.html") -> str:
        """Export all figures to a single HTML dashboard."""
        if len(self.figures) == 0:
            return "No figures to export."
        
        # Create dashboard with all figures
        html_parts = ['<html><head><title>AI Data Analyst Dashboard</title>',
                      '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head><body>']
        
        for fig_type, name, fig in self.figures:
            html_parts.append(f'<h2>{name}</h2>')
            html_parts.append(fig.to_html(full_html=False).replace('<script>', '').replace('</script>', ''))
            html_parts.append('<hr>')
        
        html_parts.append('</body></html>')
        
        with open(filename, 'w') as f:
            f.write('\n'.join(html_parts))
        
        return f"✅ Dashboard exported to {filename}"