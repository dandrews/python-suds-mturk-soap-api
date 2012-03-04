#!/usr/bin/env python

# Import libraries
import time
import hmac
import hashlib
import base64
import suds
from suds.client import Client
from suds.transport.https import HttpAuthenticated
from suds.sax.element import Element


# AWS requires user authentication
# see http://docs.amazonwebservices.com/AWSMechTurk/latest/AWSMechanicalTurkRequester/MakingRequests_RequestAuthenticationArticle.html
# Define authentication routines
def generate_timestamp( gmtime ):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)

def generate_signature( service, operation, timestamp, secret_access_key ):
    my_sha_hmac = hmac.new( secret_access_key, service + operation + timestamp, hashlib.sha1 )
    my_b64_hmac_digest = base64.encodestring( my_sha_hmac.digest() ).strip()
    return my_b64_hmac_digest

# authentication constants
AWS_ACCESS_KEY_ID = '[YOUR_AWS_KEY_ID]'
AWS_SECRET_ACCESS_KEY = '[YOUR_SECRET_ACCESS_KEY]'

transport = HttpAuthenticated(username='[YOUR_AWS_LOGIN_USERNAME]',
                              password='[YOUR_AWS_LOGIN_PASSWORD]' )

# create the operation signature
timestamp = generate_timestamp( time.gmtime() )
operation = 'CreateHIT'
signature = generate_signature( 'AWSMechanicalTurkRequester', operation, timestamp, AWS_SECRET_ACCESS_KEY )


# mturk sandbox urls
wsdl='https://mechanicalturk.sandbox.amazonaws.com/AWSMechanicalTurk/2011-10-01/AWSMechanicalTurkRequester.wsdl'
service_url='https://mechanicalturk.sandbox.amazonaws.com/?Service=AWSMechanicalTurkRequester'

# mturk production urls
#wsdl="https://mechanicalturk.amazonaws.com/AWSMechanicalTurk/2011-10-01/AWSMechanicalTurkRequester.wsdl"
#service_url='https://mechanicalturk.amazonaws.com/?Service=AWSMechanicalTurkRequester'


# create the client
client = suds.client.Client( wsdl, location=service_url, transport=transport )


# create CreateHITRequest object
hit_request = client.factory.create( 'CreateHITRequest' )


hit_request.Title = 'Your HIT Title'
hit_request.AssignmentDurationInSeconds = 3600 # 1 hour
hit_request.LifetimeInSeconds = 24 * 3600 # 1 day
hit_request.Keywords = 'your,comma,separated,keywords'
hit_request.Description = 'Your HIT Description'


# begin HITRequest.Question
# see http://docs.amazonwebservices.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QuestionFormDataStructureArticle.html
# see https://fedorahosted.org/suds/wiki/Documentation#CUSTOMSOAPHEADERS

# create your QuestionForm element that will be sent in as encoded xml
xsd_url = 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd'
qfns = ( 'qf', xsd_url ) # question form namespace

# begin QuestionForm
# see https://fedorahosted.org/suds/wiki/TipsAndTricks#IncludingLiteralXML
question_form = Element( 'QuestionForm', ns=qfns )

question_form_question = Element( 'Question', ns=qfns )

question_identifier = Element( 'QuestionIdentifier', ns=qfns).setText( '1' ) # use any numeric sequence
question_form_question.append( question_identifier )

display_name = Element( 'DisplayName', ns=qfns ).setText( 'Question Display Name' )
question_form_question.append( display_name )

is_required = Element( 'IsRequired', ns=qfns ).setText( 'true' )
question_form_question.append( is_required )

question_content = Element( 'QuestionContent', ns=qfns )
question_content_title = Element( 'Title', ns=qfns ).setText( 'Question Title' )
question_content_text = Element( 'Text', ns=qfns ).setText( 'Question Question' )
question_content.append( question_content_title )
question_content.append( question_content_text )
question_form_question.append( question_content )

answer_specification = Element( 'AnswerSpecification', ns=qfns )
free_text_answer = Element( 'FreeTextAnswer', ns=qfns )
constraints = Element( 'Constraints', ns=qfns )
length = Element( 'Length', ns=qfns ) 
length.set( 'minLength', '1' )
length.set( 'maxLength', '50' )
constraints.append( length )
free_text_answer.append( constraints )
answer_specification.append( free_text_answer )
question_form_question.append( answer_specification )

question_form.append( question_form_question )
# end QuestionForm

hit_request.Question = question_form.str() # str() to encode the xml
# end HITRequest.Question


# begin HITRequest.Reward
reward_price = client.factory.create( 'Price' )
reward_price.CurrencyCode = 'USD'
reward_price.Amount = 0.03 # 3 cents

hit_request.Reward = reward_price
# end HITRequest.Reward

# end HITRequest

# make the CreateHIT request
try:
    
    HIT = client.service.CreateHIT(
        AWSAccessKeyId = AWS_ACCESS_KEY_ID,
        Timestamp = timestamp,
        Signature = signature,
        Request = hit_request
        )

    print HIT
    # print client.last_sent() # print the request 
    # print client.last_received() # print the response
    
except suds.WebFault as detail:
    print detail


