
#!/bin/bash

# Start the backend (FastAPI) in the background
python main.py &
until curl --output /dev/null --silent --head --fail http://0.0.0.0:8000/token; do
    echo "Waiting for the backend to be ready..."
    sleep 2
done
# Start the frontend (Streamlit)
streamlit run src/main.py --server.port 8501 --server.address 0.0.0.0
