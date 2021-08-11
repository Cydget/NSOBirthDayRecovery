
# import the required libraries
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
from bs4 import BeautifulSoup
import re
import time

# Define the SCOPES. If modifying it, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
import requests
import urllib.parse
def getRecoveryLink():
    # Variable creds will store the user access token.
    # If no valid token found, we will create one.
    creds = None
  
    # The file token.pickle contains the user access token.
    # Check if it exists
    if os.path.exists('token.pickle'):
  
        # Read the token from the file and store it in the variable creds
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
  
    # If credentials are not available or are invalid, ask the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret_GMAIL_API_OATH_STUFF.json', SCOPES)
            creds = flow.run_local_server(port=0)
  
        # Save the access token in token.pickle file for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
  
    # Connect to the Gmail API
    service = build('gmail', 'v1', credentials=creds)
  
    # request a list of all the messages
    result = service.users().messages().list(userId='me').execute()
  
    # We can also pass maxResults to get any number of emails. Like this:
    # result = service.users().messages().list(maxResults=200, userId='me').execute()
    messages = result.get('messages')
  
    # messages is a list of dictionaries where each dictionary contains a message id.
  
    # iterate through all the messages
    for msg in messages:
        # Get the message from its id
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        # Use try-except to avoid any Errors
        try:
            # Get value of 'payload' from dictionary 'txt'
            payload = txt['payload']
            headers = payload['headers']
			# Look for Subject and Sender Email in the headers
            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']
            if "[Nintendo Account] Password change" not in subject:
                continue
            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            #print(payload)
            #parts = payload.get('parts')[0]
            data = payload['body']['data']
            data = data.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(data).decode('utf-8')
            search=re.findall('http[s]:\/\/.*',decoded_data)
  
            # Printing the subject, sender's email and message
            print("Subject: ", subject)
            print("From: ", sender)
            if len(search)!=0:
                print("URL:", search[0].split()[0])
                return search[0].split()[0]
                break
            #print("Message: ", body)

        except:
            pass
userAgentString='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'

def makeNSendReconveryEmail():
    NSOEmail="YOUR EMAIL GOES HERE@gmail.com"
    with requests.Session() as k:
        k.headers = {'User-Agent':userAgentString}
        r=k.get('https://accounts.nintendo.com/password/reset')
        regx = re.findall(r'(?<=csrfToken&quot;:&quot;)(.*)(?!=PasswordResetRedire)',r.text)
        csrfToken=regx[0].split("&quot;")[0] 
        #print("csrfToken",csrfToken)
        r=k.post('https://accounts.nintendo.com/password/reset',data={'address':NSOEmail,'post_password_reset_redirect_uri':'https://accounts.nintendo.com/','csrf_token':csrfToken})
        #print(r.text)
        time.sleep(10)    #wait 10 seconds for N to send email


makeNSendReconveryEmail()
#recoveryLink = getRecoveryLink()
#print(recoveryLink)
def checkBirthDay(day,month,year,endYear):
    recoveryLink = getRecoveryLink()
    failedText='Please enter the date of birth registered to this account'
    with requests.Session() as s:
        while year!=endYear:
            time.sleep(1)
            s.headers = {'User-Agent':userAgentString}
            TMPtoken=urllib.parse.unquote(re.findall(r'(?<==).*',recoveryLink)[0]).split()[0]
            try:
                r=s.get(recoveryLink,timeout=20)
            except:
                print("TimeOUT, retrying")
                makeNSendReconveryEmail()
                checkBirthDay(day,month,year,endYear)
            #print(TMPtoken)
            #print(r.text)
            #print(r.text)
            regx = re.findall(r'(?<=csrfToken&quot;:&quot;)(.*)(?=&quot)',r.text)
            try:
                csrfToken=regx[0]
                #print("page 2 csrfToken",csrfToken)
            except:
                print("Unknown Failure, Recheck Date")
                makeNSendReconveryEmail()
                checkBirthDay(day,month,year,endYear)
                break
            date=str(year)+'-'+str(month).zfill(2)+'-'+str(day).zfill(2)
            r=s.post("https://accounts.nintendo.com/password/reset/authenticate",data={'verification':'birthdate','birth_year':year,'birth_month':month,'birth_day':day,'birthdate':date,'temporary_token':TMPtoken,'csrf_token':csrfToken})
            if failedText in r.text:
                print("Tried Date: ",date)
            elif "Cannot display this page as you do not have access rights" in r.text:
                day=day-1
            else:
                print("Found Date!!!!!",date)
		year=endYear
		break
#                print(r.text)


            day=day+1
            if day==32:
                day=1
                month=month+1
            if month==13:
                month=1
                year=year+1
checkBirthDay(1,1,1990,1991)

    #s.post('https://accounts.nintendo.com/password/reset/authenticate')
