FROM python:3.11-slim

RUN mkdir app
WORKDIR /app

# Install dependencies
COPY requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set environment variables for authentication (replace with your actual path)
# ENV GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/llm-project-52521-798974421649.json"

# Copy the application code
COPY . /app
WORKDIR /app

# Expose the Streamlit port
EXPOSE 8501 

# Run the Streamlit app
# CMD ["streamlit", "run", "claim_analysis.py", "--server.enableCORS"]
CMD ["streamlit", "run", "claim_analysis.py", "--server.enableCORS=true"]
