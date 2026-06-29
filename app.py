import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Re-export everything from streamlit_app
exec(open(os.path.join(os.path.dirname(__file__), "ui", "streamlit_app.py")).read())
