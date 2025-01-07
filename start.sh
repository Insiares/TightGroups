
#!/bin/bash

# Start the backend (FastAPI) in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start the frontend (Streamlit)
streamlit run src/main.py --server.port 8501 --server.address 0.0.0.0
