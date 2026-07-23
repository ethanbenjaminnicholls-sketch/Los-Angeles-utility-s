from flask import Flask
from threading import Thread
app=Flask(__name__)
@app.get("/")
def home(): return "Online"
def keep_alive():
    Thread(target=lambda: app.run(host="0.0.0.0",port=8080),daemon=True).start()
