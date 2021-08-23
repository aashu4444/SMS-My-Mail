def sendSms(sms_body, client):    
    message = client.messages \
            .create(
                    body=sms_body,
                    from_='Your twilio number',
                    to='target phone number'
                )

    return message.sid