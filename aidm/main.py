from threading import Thread
from flask import Flask

app = Flask('')


@app.route('/')
def home():
  return "Je suis vivant !"


def run():
  app.run(host='0.0.0.0', port=8080)


Thread(target=run).start()

from discord_bot import run_dm_bot

if __name__ == "__main__":
    run_dm_bot()
