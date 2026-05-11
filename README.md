# 🤖 AI-Powered Data Analyst Agent

An intelligent AI agent that allows users to analyze CSV data using natural language queries. Built using **LangChain** and **Google Gemini**, this system democratizes data analysis by eliminating the need for coding knowledge.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![LangChain](https://img.shields.io/badge/LangChain-0.2.16-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [Future Scope](#-future-scope)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- 💬 **Natural Language Chat** - Ask questions about your data in plain English
- 📊 **Auto Dashboard** - Automatically generates relevant visualizations
- 🔍 **Data Quality Report** - Detects missing values, duplicates, and outliers
- 📈 **Custom Charts** - Create bar, line, scatter, histogram, box, and pie charts
- 🤖 **Multiple AI Models** - Choose between Gemini Flash Lite, Flash, and Pro
- 📄 **Multi-Format Export** - Download reports in PDF, Excel, and JSON
- 💡 **Smart Insights** - AI-generated business insights
- ⚡ **Quick Actions** - One-click common analyses

---

## 🛠️ Tech Stack

**Frontend:**
- Streamlit
- HTML5, CSS3
- JavaScript ES6

**Backend:**
- Python 3.12

**AI/ML:**
- Google Gemini API
- LangChain Framework

**Data Processing:**
- Pandas
- NumPy

**Visualization:**
- Plotly

**Report Generation:**
- FPDF2 (PDF)
- OpenPyXL (Excel)

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Google AI Studio API Key ([Get Free Key](https://aistudio.google.com/app/apikey))

### Steps

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/ai-data-analyst-agent.git
cd ai-data-analyst-agent
```

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**

For Windows:
```bash
venv\Scripts\activate
```

For Mac/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Configure API Key:**
Create `.env` file in root directory:
```
GOOGLE_API_KEY=your_api_key_here
```

6. **Run the application:**
```bash
streamlit run app.py
```

7. **Open browser:**
Navigate to `http://localhost:8501`

---

## 📖 Usage

1. **Enter API Key** in the sidebar
2. **Select AI Model** (Flash Lite recommended)
3. **Click "Initialize Agent"**
4. **Upload CSV file** through the file uploader
5. **Start chatting!** Ask questions like:
   - "What are the top trends in this data?"
   - "Find correlations between variables"
   - "Detect outliers in numeric columns"
   - "Give me a comprehensive summary"
6. **Explore tabs:**
   - 💬 Chat & Upload
   - 📊 Auto Dashboard
   - 🔍 Data Quality
   - 📈 Custom Charts
7. **Export Reports** in PDF, Excel, or JSON format

---

## 📁 Project Structure

```
ai-data-analyst-agent/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (API keys)
├── .gitignore               # Git ignore rules
├── README.md                 # Project documentation
│
├── agent/                    # AI Agent module
│   ├── __init__.py
│   ├── orchestrator.py      # Main agent logic
│   └── prompts.py           # System prompts
│
├── tools/                    # Analysis tools
│   ├── __init__.py
│   ├── data_tools.py        # Data loading
│   ├── analysis_tools.py    # Statistical analysis
│   ├── quality_tools.py     # Data quality
│   └── report_generator.py  # PDF/Excel/JSON export
│
├── static/                   # Static assets
│   ├── css/
│   │   └── styles.css       # Custom styling
│   └── js/
│       └── script.js        # Custom JavaScript
│
└── data/                     # Sample datasets
    └── sample_data.csv
```

---

## 📸 Screenshots

### Welcome Screen
*[Add screenshot here]*

### Chat Interface
*[Add screenshot here]*

### Auto Dashboard
*[Add screenshot here]*

### Data Quality Report
*[Add screenshot here]*

---

## 🔮 Future Scope

- 🔐 Local LLM deployment (Ollama, Llama 3) for privacy
- 🗄️ Direct database connectivity (MySQL, PostgreSQL, MongoDB)
- 👥 Multi-user collaboration features
- 🤖 Advanced ML capabilities (predictive analytics)
- 📱 Mobile application (iOS & Android)
- 🌐 Voice interface integration
- 💰 SaaS commercial deployment

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**[Your Name]**
- GitHub: [@your-username](https://github.com/prav0106)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/pravleen-kaur-0104pb)
- Email: kaurpravleen12@gmail.com

---

## 🙏 Acknowledgments

- Google Gemini API for the LLM capabilities
- LangChain framework for AI agent orchestration
- Streamlit for the amazing web framework
- Department of AI & ML, Chandigarh Engineering College Jhanjeri

---

⭐ **If you found this project useful, please consider giving it a star!** ⭐