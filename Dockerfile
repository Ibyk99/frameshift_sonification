# FROM redhat/ubi9:9.8
FROM ubuntu:noble-20260509.1


COPY ./ /flask_app

RUN apt update &&\
    apt install python3.12 -y &&\
    apt install python3.12-venv -y &&\
    apt install pip -y &&\
    python3 -m venv /flask_env &&\
    /flask_env/bin/python -m pip install -r /flask_app/requirements.txt &&\
    mkdir -p /flask_app/flask_session && mkdir -p temp

EXPOSE 5000

ENTRYPOINT ["/flask_env/bin/python", "/flask_app/app/flask_app.py"]
