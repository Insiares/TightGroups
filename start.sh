
#!/bin/bash

# Start the backend (FastAPI) in the background
python main.py &
sleep 15
# Start the frontend (Streamlit)
streamlit run src/main.py --server.port 8501 --server.address 0.0.0.0
