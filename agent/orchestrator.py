"""
Main Agent Orchestrator for AI Data Analyst
"""
import os
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

from tools.data_tools import DataTools, _dataframes
from tools.analysis_tools import AnalysisTools
from tools.quality_tools import generate_data_quality_report
from tools.report_generator import ReportGenerator


class DataAnalystAgent:
    """AI Data Analyst Agent - Advanced Version"""
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash-lite"):
        self.data_tools = DataTools()
        self.analysis_tools = AnalysisTools()
        
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key or os.getenv("GOOGLE_API_KEY"),
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        self.chat_history = []
        self.current_insights = ""
        self.current_quality = ""
    
    def process_file(self, file_path: str, file_name: str = "uploaded_data") -> str:
        result = self.data_tools.load_csv_direct(file_path, file_name)
        df = self.get_dataframe(file_name)
        if df is not None:
            self.current_quality = generate_data_quality_report(df)
        return result
    
    def _get_data_context(self) -> str:
        if "uploaded_data" not in _dataframes:
            return "No data loaded yet."
        
        df = _dataframes["uploaded_data"]
        context = f"""
DATASET SUMMARY:
• Rows: {len(df)} | Columns: {len(df.columns)}
• Columns: {', '.join(df.columns)}
• Missing Values: {df.isnull().sum().sum()}
• Duplicate Rows: {df.duplicated().sum()}

FIRST 5 ROWS:
{df.head().to_string()}

STATISTICS:
{df.describe().round(2).to_string()}

CATEGORICAL SUMMARIES:
"""
        for col in df.select_dtypes(include=['object']).columns[:3]:
            context += f"\n{col}:\n{df[col].value_counts().head(5).to_string()}\n"
        
        return context
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        try:
            data_context = self._get_data_context()
            
            full_prompt = f"""You are an expert AI Data Analyst. Analyze the following data and answer the user's question professionally.

{data_context}

USER QUESTION: {user_input}

Instructions:
- Provide clear, actionable insights
- Use bullet points and formatting
- Mention specific numbers and trends
- Suggest business recommendations where applicable
- Keep response concise but comprehensive"""
            
            messages = []
            for msg in self.chat_history[-6:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            messages.append(HumanMessage(content=full_prompt))
            response = self.llm.invoke(messages)
            
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": response.content})
            self.current_insights = response.content
            
            return {"success": True, "output": response.content}
            
        except Exception as e:
            return {"success": False, "output": f"Error: {str(e)}"}
    
    def generate_smart_insights(self) -> str:
        """Generate deep business insights using AI"""
        df = self.get_dataframe("uploaded_data")
        if df is None:
            return "No data loaded."
        
        context = self._get_data_context()
        prompt = f"""Based on this dataset, generate 6-8 deep business insights and actionable recommendations.

{context}

Format:
• Insight 1: [Pattern/Trend] → Recommendation
• Insight 2: [Anomaly] → Action
• Include correlation insights
• Include business growth suggestions
• Mention data quality red flags if any"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        self.current_insights = response.content
        return response.content
    
    def suggest_questions(self) -> List[str]:
        """AI-powered suggested follow-up questions"""
        df = self.get_dataframe("uploaded_data")
        if df is None:
            return []
        
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        suggestions = [
            "Generate a comprehensive data quality report",
            "What are the top 3 business insights from this data?",
            "Show me descriptive statistics for all numeric columns"
        ]
        
        if len(num_cols) >= 2:
            suggestions.append(f"Find correlation between {num_cols[0]} and {num_cols[1]}")
            suggestions.append(f"Detect outliers in {num_cols[0]}")
        if cat_cols and num_cols:
            suggestions.append(f"Compare {num_cols[0]} across different {cat_cols[0]}")
        if 'date' in df.columns or 'time' in str(df.columns).lower():
            suggestions.append("Analyze trends over time")
        
        return suggestions[:5]
    
    def get_dataframe(self, name: str = "uploaded_data"):
        return _dataframes.get(name)
    
    def clear_history(self):
        self.chat_history = []
    
    def get_report_generator(self):
        df = self.get_dataframe("uploaded_data")
        if df is not None:
            return ReportGenerator(df)
        return None