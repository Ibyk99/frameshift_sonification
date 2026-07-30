ARG UBUNTU_VERSION=noble-20260509.1
FROM ubuntu:${UBUNTU_VERSION}

ARG PYTHON_VERSION=3.12

# Install python3 & associated packages, then create a venv
RUN apt update &&\
    apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv pip &&\
    python3 -m venv /flask_env

# Copy the contents of this repo to the folder /flask_app inside the container
WORKDIR /flask_app
COPY . .
# Install requirements and create some required temp folders
RUN /flask_env/bin/python -m pip install -r requirements.txt &&\
    mkdir -p /flask_app/flask_session && mkdir -p temp

EXPOSE 5001

ENTRYPOINT ["/flask_env/bin/python", "app/flask_app.py"]
