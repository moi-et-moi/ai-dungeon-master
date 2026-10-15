from threading import Thread
from flask import Flask

app = Flask('')


@app.route('/')
def home():
  return "Je suis vivant !"


def run():
  app.run(host='0.0.0.0', port=8080)


Thread(target=run).start()

from aidm.discord_bot import run_dm_bot, DEFAULT_PROMPT_PATH

if __name__ == "__main__":
    run_dm_bot(system_prompt_path=DEFAULT_PROMPT_PATH)
