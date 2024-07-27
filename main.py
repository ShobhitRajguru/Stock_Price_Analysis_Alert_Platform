import os
import requests
import smtplib
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

MY_EMAIL = os.getenv("MY_EMAIL")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
API_KEY = os.getenv("API_KEY")
SYMBOL = 'TSLA'
TO_PHONE = os.getenv("TO_PHONE")
TO_EMAIL = os.getenv("TO_EMAIL")
FROM_PHONE = os.getenv("FROM_PHONE")

def get_stock_data(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    return response.json()

def send_sms(body, to_phone, from_phone, account_sid, auth_token):
    client = Client(account_sid, auth_token)
    message = client.messages.create(body=body, from_=from_phone, to=to_phone)
    return message.sid

def send_email(subject, body, to_email, from_email, password):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=from_email, password=password)
        message = f"Subject:{subject}\n\n{body}"
        connection.sendmail(from_addr=from_email, to_addrs=to_email, msg=message)

data = get_stock_data(SYMBOL, API_KEY)

if 'Global Quote' in data:
    price = data['Global Quote']['05. price']
    change_pct = data['Global Quote']['10. change percent']
    value_float = float(change_pct.replace('%', ''))
    print(f'{SYMBOL}: Price = {price}, Change = {change_pct}')
    
    if value_float > 0:
        body = f"Tesla Stock is up by 📈 {change_pct}. It's time to sell them!"
    else:
        body = f"Tesla Stock is down by 📉 {change_pct}. It's time to buy them!"
        
    try:
        sms_sid = send_sms(body, TO_PHONE, FROM_PHONE, ACCOUNT_SID, AUTH_TOKEN)
        print(f'SMS sent with SID: {sms_sid}')
    except Exception as e:
        print(f'Error sending SMS: {e}')
    
    try:
        send_email("Tesla Stock Alert", body, TO_EMAIL, MY_EMAIL, PASSWORD)
        print('Email sent successfully.')
    except Exception as e:
        print(f'Error sending email: {e}')
else:
    print(f'Error fetching data for {SYMBOL}')
