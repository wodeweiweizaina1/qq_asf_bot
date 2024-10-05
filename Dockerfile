FROM python:3.12.4
WORKDIR /app
COPY . /app
RUN pip install  -r requirements.txt
ENV NAPCAT_WS_URL="ws://localhost:3001"
ENV TARGET_USER_ID="default_user_id"
ENV ASF_API_URL="http://localhost:1242/Api"
ENV ASF_API_KEY="default_key"
CMD ["python", "main.py"]
