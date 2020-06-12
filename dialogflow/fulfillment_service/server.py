from flask import Flask, request
from main import webhook

app = Flask(__name__)
@app.route('/dialogflow/webhook', methods=['POST'])
def do_webhook():
    return webhook(request)

if __name__ == '__main__':
    app.run()
