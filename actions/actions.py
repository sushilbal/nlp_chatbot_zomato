
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk.interfaces import Action
from rasa_sdk.events import SlotSet
import json
import requests
import ast
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'

    def run(self, dispatcher, tracker, domain):
        config = {"user_key": "b3db63b6e0673d4c8437c62ed4ea2a0f"}
        zomato = Zomato(config)
        loc = tracker.get_slot('location')
        budget = tracker.get_slot('budget')
        cuisine = tracker.get_slot('cuisine')
        location_detail = zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat = d1["location_suggestions"][0]["latitude"]
        lon = d1["location_suggestions"][0]["longitude"]
        cuisines_dict = {'chinese': 25, 'italian': 55,
                         'north indian': 50, 'south indian': 85, 'american': 1}
        results = zomato.restaurant_search(
            "", lat, lon, str(cuisines_dict.get(cuisine)), 20)
        d = json.loads(results)
        #result_by_price=[r for r in d['restaurants'] if r['restaurant']['average_cost_for_two'] < budget]
        print(f' Budget for 2 ={budget}')
        print(f'Cusisine = {cuisine}')
        print(f'location = {loc}')
        response = ""
        if d['results_found'] == 0:
            response = "no results"
        else:
            for restaurant in d['restaurants']:
                response = response + "Found " + \
                    restaurant['restaurant']['name'] + " in " + \
                    restaurant['restaurant']['location']['address']+"\n"

        dispatcher.utter_message(response)
        return [SlotSet('response', response)]


class ActionSendEmail(Action):
    def name(self):
        return "action_send_email"

    def run(self, dispatcher, tracker, domain):
        mail_content = tracker.get_slot('response')
        sender_address = 'sushil.dml15@iiitb.net'
        send_to = tracker.get_slot('emailid')
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = send_to
        message['Subject'] = 'Top Restaurants in your area.'
        message.attach(MIMEText(mail_content, 'plain'))
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(sender_address, 'rasa_chat_oct_2020')
        text = message.as_string()
        session.sendmail(sender_address, send_to, text)
        session.quit()
        print('mail send')
        dispatcher.utter_message('Email Sent. Bon Apetite !!')


class ActionCheckLocation(Action):
    def name(self):
        return 'action_check_location'

    def run(self, dispatcher, tracker, domain):
        cities = ['Ahmedabad', 'Bengaluru', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai', 'Pune', 'Agra', 'Ajmer',
                  'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly', 'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal',
                  'Bhubaneswar', 'Bikaner', 'Bilaspur', 'Bokaro Steel City', 'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun',
                  'Dhanbad', 'Bhilai', 'Durgapur', 'Dindigul', 'Erode', 'Faridabad', 'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga',
                  'Guntur', 'Gwalior', 'Gurgaon', 'Guwahati', 'Hamirpur', 'Hubli–Dharwad', 'Indore', 'Jabalpur', 'Jaipur', 'Jalandhar',
                  'Jammu', 'Jamnagar', 'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kakinada', 'Kannur', 'Kanpur', 'Karnal', 'Kochi', 'Kolhapur',
                  'Kollam', 'Kozhikode', 'Kurnool', 'Ludhiana', 'Lucknow', 'Madurai', 'Malappuram', 'Mathura', 'Mangalore', 'Meerut',
                  'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Patna', 'Pondicherry', 'Purulia',
                  'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Salem', 'Sangli', 'Shimla', 'Siliguri',
                  'Solapur', 'Srinagar', 'Surat', 'Thanjavur', 'Thiruvananthapuram', 'Thrissur', 'Tiruchirappalli', 'Tirunelveli',
                  'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vasai-Virar City', 'Vijayawada', 'Visakhapatnam', 'Vellore',
                  'Warangal']
        loc = tracker.get_slot('location')
        if loc in cities:
            if tracker.get_slot('cuisine') is None:
                dispatcher.utter_message("utter_ask_cuisine",tracker)
            elif tracker.get_slot('budger') is None:
                dispatcher.utter_message("utter_ask_budget",tracker)
            else:
                dispatcher.utter_message("action_search_restaurants",tracker)
        else:
            dispatcher.utter_message("Not a valid city.",tracker)
        


base_url = "https://developers.zomato.com/api/v2.1/"


class Zomato:
    def __init__(self, config):
        self.user_key = config["user_key"]

    def get_categories(self):
        """
        Takes no input.
        Returns a dictionary of IDs and their respective category names.
        """
        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "categories",
                          headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)

        self.is_key_invalid(a)
        self.is_rate_exceeded(a)

        categories = {}
        for category in a['categories']:
            categories.update(
                {category['categories']['id']: category['categories']['name']})

        return categories

    def get_city_ID(self, city_name):
        """
        Takes City Name as input.
        Returns the ID for the city given as input.
        """
        if city_name.isalpha() == False:
            raise ValueError('InvalidCityName')
        city_name = city_name.split(' ')
        city_name = '%20'.join(city_name)
        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "cities?q=" + city_name,
                          headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)

        self.is_key_invalid(a)
        self.is_rate_exceeded(a)

        if len(a['location_suggestions']) == 0:
            raise Exception('invalid_city_name')
        elif 'name' in a['location_suggestions'][0]:
            city_name = city_name.replace('%20', ' ')
            if str(a['location_suggestions'][0]['name']).lower() == str(city_name).lower():
                return a['location_suggestions'][0]['id']
            else:
                raise ValueError('InvalidCityId')

    def get_city_name(self, city_ID):
        """
        Takes City ID as input.
        Returns the name of the city ID given as input.
        """
        self.is_valid_city_id(city_ID)

        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "cities?city_ids=" +
                          str(city_ID), headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)

        self.is_key_invalid(a)
        self.is_rate_exceeded(a)

        if a['location_suggestions'][0]['country_name'] == "":
            raise ValueError('InvalidCityId')
        else:
            temp_city_ID = a['location_suggestions'][0]['id']
            if temp_city_ID == str(city_ID):
                return a['location_suggestions'][0]['name']

    def get_collections(self, city_ID, limit=None):
        """
        Takes City ID as input. limit parameter is optional.
        Returns dictionary of Zomato restaurant collections in a city and their respective URLs.
        """
        # self.is_valid_city_id(city_ID)

        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        if limit == None:
            r = (requests.get(base_url + "collections?city_id=" +
                              str(city_ID), headers=headers).content).decode("utf-8")
        else:
            if str(limit).isalpha() == True:
                raise ValueError('LimitNotInteger')
            else:
                r = (requests.get(base_url + "collections?city_id=" + str(city_ID) +
                                  "&count=" + str(limit), headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)

        self.is_key_invalid(a)
        self.is_rate_exceeded(a)

        collections = {}
        for collection in a['collections']:
            collections.update(
                {collection['collection']['title']: collection['collection']['url']})

        return collections


    def get_cuisines(self, city_ID):
        """
        Takes City ID as input.
        Returns a sorted dictionary of all cuisine IDs and their respective cuisine names.
        """
        self.is_valid_city_id(city_ID)

        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "cuisines?city_id=" +
                          str(city_ID), headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)

        self.is_key_invalid(a)
        self.is_rate_exceeded(a)

        if len(a['cuisines']) == 0:
            raise ValueError('InvalidCityId')
        temp_cuisines = {}
        cuisines = {}
        for cuisine in a['cuisines']:
            temp_cuisines.update(
                {cuisine['cuisine']['cuisine_id']: cuisine['cuisine']['cuisine_name']})

        for cuisine in sorted(temp_cuisines):
            cuisines.update({cuisine: temp_cuisines[cuisine]})

        return cuisines


    def get_establishment_types(self, city_ID):
        """
        Takes City ID as input.
        Returns a sorted dictionary of all establishment type IDs and their respective establishment type names.
        """
        self.is_valid_city_id(city_ID)

        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "establishments?city_id=" +
                          str(city_ID), headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)

        self.is_key_invalid(a)
        self.is_rate_exceeded(a)

        temp_establishment_types = {}
        establishment_types = {}
        if 'establishments' in a:
            for establishment_type in a['establishments']:
                temp_establishment_types.update(
                    {establishment_type['establishment']['id']: establishment_type['establishment']['name']})

            for establishment_type in sorted(temp_establishment_types):
                establishment_types.update(
                    {establishment_type: temp_establishment_types[establishment_type]})

            return establishment_types
        else:
            raise ValueError('InvalidCityId')


    def get_nearby_restaurants(self, latitude, longitude):
        """
        Takes the latitude and longitude as inputs.
        Returns a dictionary of Restaurant IDs and their corresponding Zomato URLs.
        """
        try:
            float(latitude)
            float(longitude)
        except ValueError:
            raise ValueError('InvalidLatitudeOrLongitude')

        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "geocode?lat=" + str(latitude) +
                          "&lon=" + str(longitude), headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)

        nearby_restaurants = {}
        for nearby_restaurant in a['nearby_restaurants']:
            nearby_restaurants.update(
                {nearby_restaurant['restaurant']['id']: nearby_restaurant['restaurant']['url']})

        return nearby_restaurants


    def get_restaurant(self, restaurant_ID):
        """
        Takes Restaurant ID as input.
        Returns a dictionary of restaurant details.
        """
        self.is_valid_restaurant_id(restaurant_ID)

        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "restaurant?res_id=" +
                          str(restaurant_ID), headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)

        if 'code' in a:
            if a['code'] == 404:
                raise('InvalidRestaurantId')

        restaurant_details = {}
        restaurant_details.update({"name": a['name']})
        restaurant_details.update({"url": a['url']})
        restaurant_details.update({"location": a['location']['address']})
        restaurant_details.update({"city": a['location']['city']})
        restaurant_details.update({"city_ID": a['location']['city_id']})
        restaurant_details.update(
            {"user_rating": a['user_rating']['aggregate_rating']})

        restaurant_details = DotDict(restaurant_details)
        return restaurant_details

    def restaurant_search(self, query="", latitude="", longitude="", cuisines="", limit=5):
        """
        Takes either query, latitude and longitude or cuisine as input.
        Returns a list of Restaurant IDs.
        """
        cuisines = "%2C".join(cuisines.split(","))
        if str(limit).isalpha() == True:
            raise ValueError('LimitNotInteger')
        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "search?q=" + str(query) + "&count=" + str(limit) + "&lat=" + str(latitude) + "&lon=" +
                          str(longitude) + "&cuisines=" + str(cuisines)+"&sort=rating&order=desc", headers=headers).content).decode("utf-8")
        return r  # a = ast.literal_eval(r)

    def get_location(self, query="", limit=5):
        """
        Takes either query, latitude and longitude or cuisine as input.
        Returns a list of Restaurant IDs.
        """
        if str(limit).isalpha() == True:
            raise ValueError('LimitNotInteger')
        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "locations?query=" + str(query) +
                          "&count=" + str(limit), headers=headers).content).decode("utf-8")
        return r

    def restaurant_search_by_keyword(self, query="", cuisines="", limit=5):
        """
        Takes either query, latitude and longitude or cuisine as input.
        Returns a list of Restaurant IDs.
        """
        cuisines = "%2C".join(cuisines.split(","))
        if str(limit).isalpha() == True:
            raise ValueError('LimitNotInteger')
        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "search?q=" + str(query) + "&count=" + str(limit) +
                          "&cuisines=" + str(cuisines), headers=headers).content).decode("utf-8")
        return r


    def is_valid_restaurant_id(self, restaurant_ID):
        """
        Checks if the Restaurant ID is valid or invalid.
        If invalid, throws a InvalidRestaurantId Exception.
        """
        restaurant_ID = str(restaurant_ID)
        if restaurant_ID.isnumeric() == False:
            raise ValueError('InvalidRestaurantId')

    def is_valid_city_id(self, city_ID):
        """
        Checks if the City ID is valid or invalid.
        If invalid, throws a InvalidCityId Exception.
        """
        city_ID = str(city_ID)
        if city_ID.isnumeric() == False:
            return True  # raise ValueError('InvalidCityId')


    def is_key_invalid(self, a):
        """
        Checks if the API key provided is valid or invalid.
        If invalid, throws a InvalidKey Exception.
        """
        if 'code' in a:
            if a['code'] == 403:
                raise ValueError('InvalidKey')

    def is_rate_exceeded(self, a):
        """
        Checks if the request limit for the API key is exceeded or not.
        If exceeded, throws a ApiLimitExceeded Exception.
        """
        if 'code' in a:
            if a['code'] == 440:
                raise Exception('ApiLimitExceeded')


class DotDict(dict):
    """
    Dot notation access to dictionary attributes
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
