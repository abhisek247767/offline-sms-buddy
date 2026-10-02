import sys
from pathlib import Path
def main() -> None:
    """Start the Streamlit app (same as `streamlit run app.py`)."""
    from streamlit.web import cli as stcli

    app_path = Path(__file__).with_name("app.py")
    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(stcli.main())
