FROM python:3.9
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY ./views/ ./views/
COPY ./slpk/ ./slpk/
COPY ./quick_slpk_server.py ./quick_slpk_server.py
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8083
ENTRYPOINT ["python3", "quick_slpk_server.py"]