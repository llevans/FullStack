from twilio.rest import TwilioRestClient
 
# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "AC7ee9bc61d229f2d85e31a60956e61a71"
auth_token  = "5c5393305b11e50d60bbee4dc36e446a"
client = TwilioRestClient(account_sid, auth_token)
 
message = client.messages.create(body="Hello via Twilio",
    to="+19852469620",    # Replace with your phone number
    from_="+14158141829") # Replace with your Twilio number
print message.sid
