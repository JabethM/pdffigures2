# Use Ubuntu as base
FROM ubuntu:22.04

# Set environment variables to avoid interaction
ENV DEBIAN_FRONTEND=noninteractive


# Install dependencies
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install basic tools
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    git \
    unzip \
    python3 \
    python3-pip \
    openjdk-11-jdk \
    scala \
    && apt-get clean

# Add the sbt repo and install sbt correctly

RUN curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | gpg --dearmor -o /usr/share/keyrings/sbt.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/sbt.gpg] https://repo.scala-sbt.org/scalasbt/debian all main" > /etc/apt/sources.list.d/sbt.list && \
    apt-get update && \
    apt-get install -y sbt && \
    apt-get clean



# Install FastAPI + Uvicorn
RUN pip3 install fastapi uvicorn python-multipart

# Create app directory
WORKDIR /app

# Clone pdffigures2 and build it
COPY ./pdffigures2 /app/pdffigures2

RUN cd /app/pdffigures2 && \
    sbt assembly


# Make a directory for uploads and outputs
RUN mkdir -p /app/input /app/output

# Expose FastAPI on port 8000
EXPOSE 8001

# Run the API
CMD ["uvicorn", "pdffigures2.app:app", "--host", "0.0.0.0", "--port", "8001"]
