FROM python:3.9-slim
FROM gorialis/discord.py

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /usr/src/discord-bot
WORKDIR /usr/src/discord-bot

COPY . .

CMD [ "python3", "main.py" ]