from flask import Flask, render_template, request
import base64
from bs4 import BeautifulSoup

import os
from twilio.rest import Client


os.environ['TWILIO_ACCOUNT_SID'] = "Enter your twilio account sid here"
os.environ['TWILIO_AUTH_TOKEN'] = 'Enter your twilio account auth token here'

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)



app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/decodeData", methods=['GET', 'POST'])
def decodeData():
    if request.method == 'POST':
        data = request.form["data"]

        decoded = base64.urlsafe_b64decode(data)


        return decoded

@app.route("/sendSms", methods=['GET', 'POST'])
def sendSms():
    if request.method == 'POST':
        sms_body = request.form['sms_body']
        
        message = client.messages \
                .create(
                     body=sms_body,
                     from_='Your twilio account phone number',
                     to='Target phone number'
                 )

        return message.sid

if __name__ == "__main__":
    app.run(debug=True, port=8000)