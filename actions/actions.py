# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import zomatopy
import json

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_search_restaurants'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"b3db63b6e0673d4c8437c62ed4ea2a0f"}
		#config = {'user_key':"455c41499144739a6f131347a8130495"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
        buget = tracker.get_slot('budget')
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		cuisines_dict={'chinese':25,'italian':55,'north indian':50,'south indian':85,'american':1}
		results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 20)
		d = json.loads(results)
		print(f' Budget for 2 ={budget}')
		print(f'Cusisine = {cuisine}') 
		print(f'location = {loc}')
		#result_by_price=[r for r in d['restaurants'] if r['restaurant']['average_cost_for_two'] < budget]
		response=""
		if d['results_found'] == 0:
			response= "no results"
		else:
			for restaurant in d['restaurants']:
				response=response+ "Found "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+"\n"
		
		dispatcher.utter_message("---------"+response)

		return [SlotSet('location',loc)]

class ActionCheckLocation(Action):
	def name(self):
		return 'action_check_location'
		
	def run(self, dispatcher, tracker, domain):
        accepted_cities=['Ahmedabad','Bengaluru','Chennai','Delhi','Hyderabad','Kolkata','Mumbai',
        'Pune','Agra','Ajmer','Aligarh','Amravati','Amritsar','Asansol','Aurangabad','Bareilly','Belgaum',
        'Bhavnagar','Bhiwandi','Bhopal','Bhubaneswar','Bikaner','Bilaspur','Bokaro Steel City','Chandigarh',
        'Coimbatore','Cuttack','Dehradun','Dhanbad','Bhilai','Durgapur','Dindigul','Erode','Faridabad',
        'Firozabad','Ghaziabad','Gorakhpur','Gulbarga','Guntur','Gwalior','Gurgaon','Guwahati','Hamirpur',
        'Hubli–Dharwad','Indore','Jabalpur','Jaipur','Jalandhar','Jammu','Jamnagar','Jamshedpur','Jhansi',
        'Jodhpur','Kakinada','Kannur','Kanpur','Karnal','Kochi','Kolhapur','Kollam','Kozhikode','Kurnool',
        'Ludhiana','Lucknow','Madurai','Malappuram','Mathura','Mangalore','Meerut','Moradabad','Mysore',
        'Nagpur','Nanded','Nashik','Nellore','Noida','Patna','Pondicherry','Purulia','Prayagraj','Raipur',
        'Rajkot','Rajahmundry','Ranchi','Rourkela','Salem','Sangli','Shimla','Siliguri','Solapur','Srinagar',
        'Surat','Thanjavur','Thiruvananthapuram','Thrissur','Tiruchirappalli','Tirunelveli','Ujjain',
        'Bijapur','Vadodara','Varanasi','Vasai-Virar City','Vijayawada','Visakhapatnam','Vellore','Warangal']
		loc = tracker.get_slot('location')
		if loc in accepted_cities:
			SlotSet('check_op',True)
		else:
			SlotSet('check_op',False)
		return True