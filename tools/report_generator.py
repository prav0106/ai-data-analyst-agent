"""
Report Generator - PDF, Excel, JSON Export
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import json
import os
from datetime import datetime
from io import BytesIO


class ReportGenerator:
    def __init__(self, df):
        self.df = df
        self.temp_dir = "temp_report_assets"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _save_chart(self, fig, filename):
        """Save plotly chart as image"""
        path = os.path.join(self.temp_dir, filename)
        try:
            fig.write_image(path, scale=2, width=800, height=500)
            return path
        except Exception:
            return None
    
    def generate_auto_charts(self):
        """Generate charts for PDF report"""
        charts = []
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        # Correlation heatmap
        if len(numeric_cols) >= 2:
            corr = self.df[numeric_cols].corr()
            fig = go.Figure(data=go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.columns,
                colorscale='RdBu', zmid=0, text=corr.round(2).values,
                texttemplate='%{text}', textfont={"size": 10}
            ))
            fig.update_layout(title="Correlation Heatmap", height=500)
            path = self._save_chart(fig, "correlation.png")
            if path:
                charts.append(path)
        
        # Histogram for first numeric
        if numeric_cols:
            fig = px.histogram(self.df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
            fig.update_layout(height=500)
            path = self._save_chart(fig, "histogram.png")
            if path:
                charts.append(path)
        
        # Bar chart for first categorical
        if cat_cols:
            vc = self.df[cat_cols[0]].value_counts().head(10)
            fig = px.bar(x=vc.index, y=vc.values, title=f"Top {cat_cols[0]} Categories")
            fig.update_layout(height=500)
            path = self._save_chart(fig, "bar.png")
            if path:
                charts.append(path)
        
        return charts
    
    def generate_pdf(self, insights_text, quality_text):
        """Generate comprehensive PDF report"""
        output = BytesIO()
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Page 1: Title
        pdf.add_page()
        pdf.set_font("Arial", 'B', 22)
        pdf.cell(0, 12, "AI Data Analysis Report", ln=True, align='C')
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}", ln=True, align='C')
        pdf.ln(8)
        
        # Overview
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "1. Dataset Overview", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 7, f"Rows: {len(self.df)}\nColumns: {len(self.df.columns)}\n"
                              f"Missing Values: {self.df.isnull().sum().sum()}\n"
                              f"Duplicate Rows: {self.df.duplicated().sum()}")
        pdf.ln(3)
        
        # Quality Report
        if quality_text:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "2. Data Quality Assessment", ln=True)
            pdf.set_font("Arial", '', 10)
            clean_q = quality_text.replace('•', '-').replace('📋', '').replace('🔍', '').replace('✅', 'OK:').replace('⚠️', 'WARN:').replace('💡', 'TIP:')
            pdf.multi_cell(0, 6, clean_q)
            pdf.ln(3)
        
        # Insights
        if insights_text:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "3. Smart Insights & Recommendations", ln=True)
            pdf.set_font("Arial", '', 10)
            clean_i = insights_text.replace('•', '-').replace('📈', '').replace('🔗', '').replace('💡', '').replace('🎯', '')
            pdf.multi_cell(0, 6, clean_i)
            pdf.ln(3)
        
        # Charts Page
        chart_paths = self.generate_auto_charts()
        if chart_paths:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "4. Visualizations", ln=True)
            pdf.ln(2)
            for path in chart_paths[:4]:
                pdf.image(path, x=15, w=180)
                pdf.ln(5)
        
        pdf.output(output)
        self.cleanup()
        output.seek(0)
        return output
    
    def generate_excel(self):
        """Export data + stats to Excel"""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            self.df.to_excel(writer, sheet_name='Raw Data', index=False)
            self.df.describe().to_excel(writer, sheet_name='Statistics')
            # Missing values sheet
            missing = self.df.isnull().sum().to_frame('Missing Count')
            missing['Missing %'] = (missing['Missing Count'] / len(self.df) * 100).round(2)
            missing.to_excel(writer, sheet_name='Missing Values')
        output.seek(0)
        return output
    
    def generate_json(self):
        """Export report as JSON"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "dtypes": {k: str(v) for k, v in self.df.dtypes.items()},
            "statistics": self.df.describe().to_dict(),
            "missing_values": self.df.isnull().sum().to_dict(),
            "sample_data": self.df.head(5).to_dict(orient='records')
        }
        output = BytesIO()
        output.write(json.dumps(report, indent=2, default=str).encode('utf-8'))
        output.seek(0)
        return output
    
    def cleanup(self):
        for f in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, f))
            except:
                pass