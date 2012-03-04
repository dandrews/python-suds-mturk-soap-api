#!/usr/bin/env python

# Import libraries
import time
import hmac
import hashlib
import base64
import suds
from suds.client import Client
from suds.transport.https import HttpAuthenticated

# AWS requires user authentication
# see http://docs.amazonwebservices.com/AWSMechTurk/latest/AWSMechanicalTurkRequester/MakingRequests_RequestAuthenticationArticle.html
# Define authentication routines
def generate_timestamp(gmtime):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)

def generate_signature(service, operation, timestamp, secret_access_key):
    my_sha_hmac = hmac.new(secret_access_key, service + operation + timestamp, hashlib.sha1)
    my_b64_hmac_digest = base64.encodestring(my_sha_hmac.digest()).strip()
    return my_b64_hmac_digest

# authentication constants
AWS_ACCESS_KEY_ID = '[YOUR_AWS_KEY_ID]'
AWS_SECRET_ACCESS_KEY = '[YOUR_SECRET_ACCESS_KEY]'

transport = HttpAuthenticated(username='[YOUR_AWS_LOGIN_USERNAME]',
                              password='[YOUR_AWS_LOGIN_PASSWORD]' )

# create the operation signature
timestamp = generate_timestamp( time.gmtime() )
operation = 'GetAccountBalance'
signature = generate_signature( 'AWSMechanicalTurkRequester', operation, timestamp, AWS_SECRET_ACCESS_KEY )

# mturk sandbox urls
wsdl='https://mechanicalturk.sandbox.amazonaws.com/AWSMechanicalTurk/2011-10-01/AWSMechanicalTurkRequester.wsdl'
service_url='https://mechanicalturk.sandbox.amazonaws.com/?Service=AWSMechanicalTurkRequester'

# mturk production urls
#wsdl="https://mechanicalturk.amazonaws.com/AWSMechanicalTurk/2011-10-01/AWSMechanicalTurkRequester.wsdl"
#service_url='https://mechanicalturk.amazonaws.com/?Service=AWSMechanicalTurkRequester'


# create the client
client = Client( wsdl, location=service_url, transport=transport ) 

# make the GetAccountBalance request
try:
    
    AccountBalance = client.service.GetAccountBalance(
        AWSAccessKeyId = AWS_ACCESS_KEY_ID,
        Timestamp = timestamp,
        Signature = signature
        )

    print AccountBalance
    # print client.last_sent() # print the request 
    # print client.last_received() # print the response
    
except suds.WebFault as detail:
    print detail



