# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="${PATH}:/root/.local/bin"

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Set the environment variable for the port
ENV PORT 8080

# Create a shell script to run Streamlit
RUN echo '#!/bin/bash\n\
streamlit run 00_🏠_Hjem.py --server.port=8501 --server.address=0.0.0.0 &\n\
socat TCP-LISTEN:${PORT},fork TCP:127.0.0.1:8501' > /app/run.sh \
    && chmod +x /app/run.sh

# Install socat
RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

# Run the shell script
CMD ["/app/run.sh"]