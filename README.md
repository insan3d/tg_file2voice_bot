# `tg_file2voice_bot`: Telegram bot

Converts any message with media (audio file, video, voice message and video message) received into voice message. Done in hour just for fun. Requires `ffmpeg` to be in `PATH`.

Basic usage is:

```bash session
export BOT_TOKEN=<your-api-token>

apt update && apt install ffmpeg
python3 -m venv venv
./venv/bin/python3 -m pip install -r requirements.txt

./venv/bin/python3 tg_file2voice_bot.py
```
Or with Docker:

```bash session
git clone --depth=1 git@github.com:insan3d/tg_file2voice_bot.git
cd tg_file2voice_bot

docker build . --tag tg_file2voice_bot
docker run -d -e BOT_TOKEN=<your-api-token>
```
