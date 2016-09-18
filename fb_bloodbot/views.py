import json, requests, random, re, time
from pprint import pprint

from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import *

# Create your views here.
VERIFY_TOKEN = 'vamshi29292'
PAGE_ACCESS_TOKEN = 'EAALZAPdM3on8BAPFknD76ZAN6qJ6sPUmnfdI24NZAOjSD0w0XAQQXzJdcFjp1to5lCP4Xib2WdXZBbJI0WrawihkLUWla5zD51YaAA5BiLHjoKsvecsVQYYc7GwMI5vPU3swLIltfktfp5Sv6u6KZB6BtCXMz0yBoDeJUySQ0RwZDZD'


class BloodbotView(generic.View):
	def get(self, request, *args, **kwargs):
		if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
			return HttpResponse(self.request.GET['hub.challenge'])
		else:
			return HttpResponse('Error, invalid token')


	@method_decorator(csrf_exempt)


	def dispatch(self, request, *args, **kwargs):
		return generic.View.dispatch(self, request, *args, **kwargs)

	# Post function to handle Facebook messages
	def post(self, request, *args, **kwargs):
		incoming_message = json.loads(self.request.body.decode('utf-8'))
		for entry in incoming_message['entry']:
			for message in entry['messaging']: 
				if 'message' in message:
					pprint (message)
					handle_message(message)
				elif 'postback' in message:
					handle_postback(message)
				elif 'read' in message:
					continue
				elif 'delivery' in message:
					continue
		return HttpResponse()


def post_facebook_message(fbid, message):           
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN 
	response_msg = json.dumps({"recipient":{"id":fbid}, "message":message})
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
	pprint(status.json())


def handle_postback(message):
	if message['postback']['payload'] == 'First_Time_User':
		user_signup(message['sender']['id'])
	elif message['postback']['payload'] == 'Upload':
		user = User.objects.get(fbId=message['sender']['id'])
	elif message['postback']['payload'] == 'request':
		create_request(message['sender']['id'])


def handle_message(message):
	sender_id = message['sender']['id']
	try:
		user = User.objects.get(fbId=sender_id)
		if user.status == 'preliminary_signup_done':
			get_bloodGroup(sender_id)
		elif user.status == 'bloodGroup_requested':
			update_bloodGroup(sender_id, message)
		elif user.status == 'bloodGroup_received':
			get_rhesusFactor(sender_id)
		elif user.status == 'rhesusFactor_requested':
			update_rhesusFactor(sender_id, message)
		elif user.status == 'rhesusFactor_received':
			get_lastDonation(sender_id)
		elif user.status == 'lastDonation_requested':
			update_lastDonation(sender_id, message)
		elif user.status == 'lastDonation_received':
			get_locations(sender_id)
		elif user.status == 'locations_requested':
			update_locations(sender_id, message)
		elif user.status == 'Signup_complete':
			signup_complete(sender_id)
		elif user.status == 'Recipient':
			get_req_bloodGroup(sender_id)
		elif user.status == 'Recipient_bloodGroup_requested':
			update_req_bloodGroup(sender_id, message)
		elif user.status == 'Recipient_bloodGroup_received':
			get_req_rhesusFactor(sender_id)
		elif user.status == 'Recipient_rhesusFactor_requested':
			update_req_rhesusFactor(sender_id, message)
		elif user.status == 'Recipient_rhesusFactor_received':
			get_req_phone(sender_id)
		elif user.status == 'Recipient_phone_requested':
			update_req_phone(sender_id, message)
		elif user.status == 'Recipient_phone_received':
			get_req_location(sender_id)
		elif user.status == 'Recipient_location_requested':
			update_req_location(sender_id, message)
		elif user.status == 'Recipient_location_received':
			connect_req_donor(sender_id)
		elif user.status == 'Recipient_connected':
			call_status(sender_id, message)
		elif 'Recipient' in user.status:
			close_reqeust(sender_id,message)

	except:
		user_signup(sender_id)


def get_user_details(id):
	user_details_url = "https://graph.facebook.com/v2.6/%s"%id
	user_details_params = {'fields':'first_name,last_name,gender', 'access_token':PAGE_ACCESS_TOKEN}
	user_details = requests.get(user_details_url, user_details_params).json()
	return user_details


def user_signup(fid):
	user_details = get_user_details(fid)
	new_user = User(name = '%s %s'%(user_details['first_name'],user_details['last_name']),
					gender = user_details['gender'],
					fbId = fid,
					status= "preliminary_signup_done",
					bloodGroup_id=5,
					rhesusFactor_id=1)
	new_user.save()
	get_bloodGroup(fid)


def get_bloodGroup(fid):
	message_to_send = {
		"text": "Select your blood group",
		"quick_replies": [
			{
				"content_type":"text",
				"title":"O",
				"payload":"1"
			},
			{
				"content_type":"text",
				"title":"A",
				"payload":"2"
			},
			{
				"content_type":"text",
				"title":"B",
				"payload":"3"
			},
			{
				"content_type":"text",
				"title":"AB",
				"payload":"4"
			}
		]
	}
	post_facebook_message(fid,message_to_send)
	user = User.objects.get(fbId=fid)
	user.status = "bloodGroup_requested"
	user.save()


def update_bloodGroup(fid,message):
	user = User.objects.get(fbId=fid)
	if 'quick_reply' in message['message']:
		BG = int(message['message']['quick_reply']['payload'])
		user.bloodGroup_id = BG
		user.status = "Recipient_bloodGroup_received"
		user.save()
		get_rhesusFactor(fid)
	else:
		get_bloodGroup(fid)


def get_rhesusFactor(fid):
	message_to_send = {
		"text": "Select your rhesus factor",
		"quick_replies": [
			{
				"content_type":"text",
				"title":"positive(+)",
				"payload":"1"
			},
			{
				"content_type":"text",
				"title":"negative(-)",
				"payload":"2"
			}
		]
	}
	post_facebook_message(fid, message_to_send)
	user = User.objects.get(fbId=fid)
	user.status = 'rhesusFactor_requested'
	user.save()


def update_rhesusFactor(fid, message):
	user = User.objects.get(fbId=fid)
	if 'quick_reply' in message['message']:
		RH = int(message['message']['quick_reply']['payload'])
		user.rhesusFactor_id = RH
		user.status = "rhesusFactor_received"
		user.save()
		get_lastDonation(fid)
	else:
		get_rhesusFactor(fid)


def get_lastDonation(fid):
	message_to_send = {
		"text": "Enter the date you last donated blood in 'dd<space>mm<space>yyyy' format. Click 'None' if you don't remember.",
		"quick_replies": [
			{
				'content_type':'text',
				'title':'None',
				'payload':'None'
			}
		]
	}
	post_facebook_message(fid,message_to_send)
	user = User.objects.get(fbId = fid)
	user.status = 'lastDonation_requested'
	user.save()


def update_lastDonation(fid, message):
	user = User.objects.get(fbId=fid)
	if 'quick_reply' in message['message']:
		user.last_donation = None
		user.status = "lastDonation_received"
		user.save()
		get_locations(fid)
	elif 'text' in message['message']:
		date = message['message']['text'].split()
		if len(date) == 3:
			if len(date[0]) == 2 and len(date[1])==2 and len(date[2])==4:
				user.last_donation = "%s-%s-%s"%(date[2],date[1],date[0])
				user.status = "lastDonation_received"
				user.save()
				get_locations(fid)
			else:
				get_lastDonation(fid)
	else:
		get_lastDonation(fid)
	

def get_locations(fid):
	message_to_send = {
		"text":"Share the locations where you're willing to donate blood. Send 'Done' when you've finished adding locations.\nPlease don't be too specific when adding locations. Try to search for broader areas like 'Koramangala, Bengaluru' or 'Indiranagar, Bengaluru' and send",
		"quick_replies": [
			{
				 "content_type":"location",
			},
			{
				"content_type":"text",
				'title':'Done',
				'payload':'Done'
			}
		]
	}
	post_facebook_message(fid, message_to_send)
	user = User.objects.get(fbId=fid)
	user.status = "locations_requested"
	user.save()


def update_locations(fid, message):
	user = User.objects.get(fbId=fid)
	if 'attachments' in message['message']:
		if message['message']['attachments'][0]['type'] == 'location':
			location_data = message['message']['attachments'][0]
			try:
				location = Location.objects.get(name=location_data['title'])
			except:
				location = Location(name=location_data['title'], lat=location_data['payload']['coordinates']['lat'], lon=location_data['payload']['coordinates']['long'])
				location.save()
			location.users.add(user)
			get_locations(fid)
	elif 'quick_reply' in message['message']:
		if message['message']['quick_reply']['payload'] == "Done":
			if Location.objects.filter(users=user).count() >= 1:
				user.status = "Signup_complete"
				user.save()
				signup_complete(fid)
			else:
				message_to_send = {"text": "Please add atleast one location"}
				post_facebook_message(fid, message_to_send)
				get_locations(fid)
	else:
		get_locations(fid)


def signup_complete(fid):
	user = User.objects.get(fbId=fid)
	user.status = 'Available'
	user.save()
	message_to_send_1 = {'text':"Thank You %s for registering. Your status is now 'Available' for donations. We will broadcast any requests for blood in your preferred locations"%user.name}
	message_to_send_2 = {'text':"Meanwhile select options from the menu to update your info and availability status or make a request for blood donors"}
	post_facebook_message(fid,message_to_send_1)
	post_facebook_message(fid,message_to_send_2)


def create_request(fid):
	user = User.objects.get(fbId=fid)
	if 'Recipient' not in user.status:
		user.status = 'Recipient'
		user.save()
		new_req = Request(recipient_id=fid,
						  location_id=1,
						  bloodGroup_id=5,
						  rhesusFactor_id=1,
						  status='Open')
		new_req.save()
		get_req_bloodGroup(fid)
	else:
		message_to_send = {'text':'Please close any previous requests before you make a new request'}
		post_facebook_message(fid,message_to_send)


def get_req_bloodGroup(fid):
	message_to_send = {
		'text':'Select the Blood group required',
		"quick_replies": [
			{
				"content_type":"text",
				"title":"O",
				"payload":"1"
			},
			{
				"content_type":"text",
				"title":"A",
				"payload":"2"
			},
			{
				"content_type":"text",
				"title":"B",
				"payload":"3"
			},
			{
				"content_type":"text",
				"title":"AB",
				"payload":"4"
			}
		]
	}
	post_facebook_message(fid, message_to_send)
	user = User.objects.get(fbId=fid)
	user.status = "Recipient_bloodGroup_requested"
	user.save()

def update_req_bloodGroup(fid, message):
	user = User.objects.get(fbId=fid)
	print user
	print message['message']['quick_reply']
	if 'quick_reply' in message['message']:
		request = Request.objects.filter(recipient_id=fid, status="Open")[0]
		BG = message['message']['quick_reply']['payload']
		request.bloodGroup_id = BG
		request.save()
		user.status = "Recipient_bloodGroup_received"
		user.save()
		get_req_rhesusFactor(fid)
	else:
		get_req_bloodGroup(fid)


def get_req_rhesusFactor(fid):
	message_to_send = {
		'text':'Select the rhesus factor required',
		'quick_replies': [
			{
				'content_type':'text',
				'title':'positive(+)',
				'payload':'1'
			},
			{
				'content_type':'text',
				'title': 'negative(-)',
				'payload':'2'
			}
		]
	}
	user = User.objects.get(fbId=fid)
	post_facebook_message(fid, message_to_send)
	user.status = 'Recipient_rhesusFactor_requested'
	user.save()


def update_req_rhesusFactor(fid, message):
	user = User.objects.get(fbId=fid)
	if 'quick_reply' in message['message']:
		RH = message['message']['quick_reply']['payload']
		request = Request.objects.filter(recipient_id=fid, status="Open")[0]
		request.rhesusFactor_id = RH
		request.save()
		user.status = 'Recipient_rhesusFactor_received'
		user.save()
		get_req_phone(fid)
	else:
		get_req_rhesusFactor(fid)


def get_req_phone(fid):
	message_to_send = {'text':"Please enter your 10 digit phone number(don't include 0)"}
	post_facebook_message(fid, message_to_send)
	user = User.objects.get(fbId=fid)
	user.status = 'Recipient_phone_requested'
	user.save()


def update_req_phone(fid, message):
	print len(message['message']['text'])
	user = User.objects.get(fbId=fid)
	request = Request.objects.filter(recipient_id=fid, status="Open")[0]
	if len(message['message']['text']) == 10:
		request.recipient_ph_no = '+91'+message['message']['text']
		request.save()
		user.status = 'Recipient_phone_received'
		get_req_location(fid)
	else:
		get_req_phone(fid)


def get_req_location(fid):
	user = User.objects.get(fbId=fid)
	message_to_send = {
		'text':"Where is blood required? Please don't be very specific with the location. Search for a very broad area like 'Koramangala, Bengaluru' or 'Indiranagar, Bengaluru' and send it",
		'quick_replies': [
			{
				'content_type': 'location'
			}
		]
	}
	post_facebook_message(fid, message_to_send)
	user.status = 'Recipient_location_requested'
	user.save()


def update_req_location(fid, message):
	user = User.objects.get(fbId=fid)
	if 'attachments' in message['message']:
		if message['message']['attachments'][0]['type'] == 'location':
			location_data = message['message']['attachments'][0]
			request = Request.objects.filter(recipient_id=fid, status="Open")[0]
			try:
				location = Location.objects.get(name=location_data['title'])
				request.location_id = location.id
				request.save()
				user.status = 'Recipient_location_received'
				user.save()
				connect_req_donor(fid)
			except:
				message_to_send = {'text':"No users found for the given location. Modify the location name slightly and try again"}
				post_facebook_message(fid, message_to_send)
	else:
		get_req_location(fid)

def connect_req_donor(fid):
	user = User.objects.get(fbId=fid)
	reqeust = Request.objects.filter(recipient_id=fid, status="Open")[0]
	donors = random.shuffle(User.objects.filter(location=request.location_id))
	message_to_donors = [
		{'text':'%s %s blood needed in %s.'%(reqeust.bloodGroup, reqeust.rhesusFactor, request.location)},
		{
			"message":{
				"attachment":{
					"type":"template",
					"payload":{
						"template_type":"button",
						"text":"Please contact %s?"%request.recipient,
						"buttons":[
							{
								"type":"phone_number",
								"title":"Call",
								"payload":"%s"%request.recipient_ph_no
							}
						]
					}
				}
			}
		}
	]	
	for donor in donors:
		post_facebook_message(donor.fbId, message_to_donors[0])
		post_facebook_message(donor.fbId, message_to_donors[1])
	message_to_send = {
		'text': "Your number has been shared with prospective donors. Have you received a call from any? (Please update as No if you didn't receive any call in 30 minutes",
		'quick_replies': [
			{
				'content_type': 'text',
				'title': 'Yes',
				'payload': 'Yes'
			},
			{
				'content_type': 'text',
				'title': 'No',
				'payload': 'No'
			}
		]
	}
	post_facebook_message(fid, message_to_send)
	user.status = 'Recipient_connected'
	user.save()

def call_status(fid):
	user = User.objects.get(fbId=fid)
	request = Request.objects.filter(recipient_id=fid, status="Open")[0]
	if message['message']['quick_reply']['payload'] == 'Yes':
		close_reqeust(fid)
	elif message['message']['quick_reply']['payload'] == 'No':
		connect_req_donor(fid)


def close_reqeust(fid):
	user = User.objects.get(fbId=fid)
	request = Request.objects.filter(recipient_id=fid, status="Open")[0]
	user.status = 'Available'
	reqeust.status = 'Closed'
	user.save()
	request.save()