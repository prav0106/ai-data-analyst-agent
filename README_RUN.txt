============================================================
 AI Data Analyst Agent - How to Run
============================================================

This file explains how to launch the AI Data Analyst Agent locally.

------------------------------------------------------------
1. PREREQUISITES
------------------------------------------------------------
- Python 3.10 or newer (https://www.python.org/downloads/)
- A free Google AI (Gemini) API key.
  Get one at: https://aistudio.google.com/app/apikey
- (Optional) Git, if you cloned the repository.

------------------------------------------------------------
2. QUICK START - WINDOWS (run.bat)
------------------------------------------------------------
Just double-click run.bat, or open a Command Prompt in the
project folder and run:

    run.bat

The batch file will:
  1. Verify Python is installed.
  2. Create a virtual environment (.venv) the first time.
  3. Install / upgrade all packages from requirements.txt.
  4. Launch the Streamlit UI at http://localhost:8501

Stop the server with Ctrl+C. Close the window to exit.

------------------------------------------------------------
3. MANUAL SETUP (any OS - Windows / macOS / Linux)
------------------------------------------------------------
Open a terminal in the project directory and run:

    # Create a virtual environment
    python -m venv .venv

    # Activate it:
    #   Windows (cmd):     .venv\Scripts\activate.bat
    #   Windows (PowerShell): .venv\Scripts\Activate.ps1
    #   macOS / Linux:     source .venv/bin/activate

    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt

    # Run the app
    streamlit run app.py

The app will open in your browser at http://localhost:8501.

------------------------------------------------------------
4. API KEY SETUP
------------------------------------------------------------
You can provide your Google AI API key in either of two ways:

  Option A (easiest): Paste it into the "Google AI API key"
  field in the app's sidebar and click "Connect Gemini".

  Option B (auto-load): Create a file named .env in the
  project root with the line:

      GOOGLE_API_KEY=your_key_here

  The app will load it automatically on startup via python-dotenv.

The key is kept in-memory for the session only and is never
stored by the app.

------------------------------------------------------------
5. USING THE APP
------------------------------------------------------------
  1. When the app loads, click "Try sample dataset" or upload
     your own CSV file on the Chat tab.
  2. Connect Gemini using your API key (sidebar).
  3. Ask questions in plain English, e.g.:
       - "Give me a comprehensive summary of this dataset"
       - "Find correlations between numeric columns"
       - "Show me outliers in all numeric columns"
  4. Explore the auto-generated Dashboard, Data Quality, and
     Charts tabs.
  5. Export reports as PDF, Excel, or JSON from the sidebar.

------------------------------------------------------------
6. TROUBLESHOOTING
------------------------------------------------------------
- "Python not found": Install Python 3.10+ and make sure
  "Add Python to PATH" is checked during installation.
- "Could not connect" / Gemini error: Double-check your API
  key and that you have internet access. Free-tier quotas
  apply; if you hit a limit, wait a minute and retry, or
  switch to a different model from the sidebar dropdown.
- Port 8501 already in use: pass a different port, e.g.
      streamlit run app.py --server.port 8502
- CSV not loading: Ensure the file is a valid UTF-8 CSV with
  a header row.

------------------------------------------------------------
7. PROJECT FILES
------------------------------------------------------------
  app.py                 - Main Streamlit application
  agent/                 - LLM orchestrator & prompts
  tools/                 - Data, analysis, quality, visual,
                           and report-generation tools
  data/sample_data.csv   - Sample dataset for quick testing
  static/                - CSS / JS / images
  requirements.txt       - Python dependencies
  run.bat                - Windows one-click launcher
  README_RUN.txt         - This file

------------------------------------------------------------
Happy analysing!
============================================================
