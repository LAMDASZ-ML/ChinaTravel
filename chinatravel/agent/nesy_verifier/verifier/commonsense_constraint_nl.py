
import sys


from chinatravel.environment.tools.accommodations.apis import Accommodations
from chinatravel.environment.tools.restaurants.apis import Restaurants
from chinatravel.environment.tools.attractions.apis import Attractions
from chinatravel.environment.tools.intercity_transport.apis import IntercityTransport
from chinatravel.environment.tools.transportation.apis import Transportation
# from env.tools.transportation.apis import GoTo
# from envs import goto
import json
import os
import sys
from tqdm import tqdm
import math
from chinatravel.evaluation.utils import load_json_file
    
import pandas as pd

accommodation = Accommodations()
restaurants = Restaurants()
attractions = Attractions()
intercity_transport=IntercityTransport()
innercity_transport=Transportation()


'''
Constraints:
Available
1. Intercity transport information exsits and is objective: ID, time, startpos and endpos need to be correct.
2. Attractions
3. Hotels
4. Restaurants
5. transportation
6. Times
7. space
'''

def return_info_debug(flag, info):
    return flag, info


def return_info_test(flag, info):
    return flag



def collect_intercity_transport_error(symbolic_input, plan_json, verbose=False):
    
    error_info = []

    if not isinstance(plan_json, dict):
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info
    try:
        plan_json["itinerary"]
    except:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info
    if type(plan_json["itinerary"])!= list:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info

    
    first_day_plan=plan_json["itinerary"][0]
    last_day_plan=plan_json["itinerary"][-1]

    target_city=symbolic_input['target_city']
    start_pos=symbolic_input['start_city']

    # must contain intecity transport
    if len(first_day_plan["activities"])==0 or len(last_day_plan["activities"])==0: 
        error_info = ["The plan does not provide the intecity transport at the first and last day."]
        return error_info
    
    go_intercity_transport_plan=first_day_plan["activities"][0]
    back_intercity_transport_plan=last_day_plan["activities"][-1]
    if("FlightID" not in go_intercity_transport_plan.keys()) and ("TrainID" not in go_intercity_transport_plan.keys()): 
        error_info = ["The first activity should be an intercity transport."]
        return error_info
    
    if("FlightID" not in back_intercity_transport_plan.keys()) and ("TrainID" not in back_intercity_transport_plan.keys()): 
        error_info = ["The last activity should be an intercity transport."]
        return error_info


    go_type=go_intercity_transport_plan['type']
    if go_type!='airplane' and go_type!='train':
        error_info = ["Intercity transport type should be airplane or train."]
        return error_info
    
    back_type=back_intercity_transport_plan['type']
    if back_type!='airplane' and back_type!='train':
        error_info = ["Intercity transport type should be airplane or train."]
        return error_info
    

    go_df=intercity_transport.select(start_pos,target_city,go_type)

    if not ("start" in go_intercity_transport_plan and "end" in go_intercity_transport_plan):
        error_info.append("Intercity-transport from origin to destination should provide start and end position.")
    
    if not ("start" in back_intercity_transport_plan and "end" in back_intercity_transport_plan):
        error_info.append("Intercity-transport from destination to origin should provide start and end position.")

    if len(error_info) > 0:
        return error_info    

    go_flag=0
    for _, row in go_df.iterrows():
        if go_type=='airplane':
            try: 
                go_intercity_transport_plan['FlightID']
            except: 
                error_info.append("Intercity airplane from origin to destination should provide the valid FlightID.")
                break

            if go_intercity_transport_plan['FlightID']==row['FlightID'] and go_intercity_transport_plan['start']==row['From'] and go_intercity_transport_plan['end']==row['To']:
                go_flag=1
                try: 
                    go_intercity_transport_plan['start_time']
                    go_intercity_transport_plan['end_time']
                    if row['BeginTime'] == go_intercity_transport_plan['start_time'] and row['EndTime'] == go_intercity_transport_plan['end_time']:
                        pass
                    else:
                        error_info.append(f"Incorrect duration information of given intercity transport from origin to destination {go_intercity_transport_plan['FlightID']} [start_time -> end_time].")
                except: 
                    error_info.append(f"Intercity transport from origin to destination {go_intercity_transport_plan['FlightID']} should provide the duration information.")
                
                try: 
                    go_intercity_transport_plan['price']
                    if row['Cost']==go_intercity_transport_plan['price']:
                        pass                    
                    else:
                        error_info.append(f"Incorrect price information of given intercity transport from origin to destination {go_intercity_transport_plan['FlightID']}.")
                except: 
                    error_info.append(f"Intercity transport from origin to destination {go_intercity_transport_plan['FlightID']} should provide the price information.")
                
                try: 
                    go_intercity_transport_plan['cost']
                    go_intercity_transport_plan['tickets']
                    if abs(go_intercity_transport_plan['price'] * go_intercity_transport_plan['tickets'] - go_intercity_transport_plan['cost']) > .1:
                        error_info.append(f"Incorrect cost information of given intercity transport from origin to destination {go_intercity_transport_plan['FlightID']} [cost = price * tickets].")
                except: 
                    error_info.append(f"Intercity transport from origin to destination {go_intercity_transport_plan['FlightID']} should provide the tickets and cost information. [cost = price * tickets].")

                break
        if go_type=='train':
            try: 
                go_intercity_transport_plan['TrainID']
            except: 
                error_info.append("Intercity train from origin to destination should provide the valid TrainID.")
                break

            if go_intercity_transport_plan['TrainID']==row['TrainID']  and go_intercity_transport_plan['start']==row['From'] and go_intercity_transport_plan['end']==row['To']:
                go_flag=1
                try: 
                    go_intercity_transport_plan['start_time']
                    go_intercity_transport_plan['end_time']
                    if row['BeginTime'] == go_intercity_transport_plan['start_time'] and row['EndTime'] == go_intercity_transport_plan['end_time']:
                        pass
                    else:
                        error_info.append(f"Incorrect duration information of given intercity transport from origin to destination {go_intercity_transport_plan['TrainID']} [start_time -> end_time].")
                except: 
                    error_info.append(f"Intercity transport from origin to destination {go_intercity_transport_plan['TrainID']} should provide the duration information.")
                
                try: 
                    go_intercity_transport_plan['price']
                    if row['Cost']==go_intercity_transport_plan['price']:
                        pass                    
                    else:
                        error_info.append(f"Incorrect price information of given intercity transport from origin to destination {go_intercity_transport_plan['TrainID']}.")
                except: 
                    error_info.append(f"Intercity from origin to destination {go_intercity_transport_plan['TrainID']} should provide the price information.")
                try: 
                    go_intercity_transport_plan['cost']
                    go_intercity_transport_plan['tickets']
                    if abs(go_intercity_transport_plan['price'] * go_intercity_transport_plan['tickets'] - go_intercity_transport_plan['cost']) > .1:
                        error_info.append(f"Incorrect cost information of given intercity transport from origin to destination {go_intercity_transport_plan['TrainID']} [cost = price * tickets].")
                except: 
                    error_info.append(f"Intercity transport from origin to destination {go_intercity_transport_plan['TrainID']} should provide the tickets and cost information. [cost = price * tickets].")

                break

    if go_flag==0:
        error_info.append("No information found given intercity transport ID from origin to destination.")

    
    back_df=intercity_transport.select(target_city,start_pos,back_type)

    back_flag=0
    
    for _, row in back_df.iterrows():
        if back_type=='airplane':
            try: 
                back_intercity_transport_plan['FlightID']
            except: 
                error_info.append("Intercity airplane from destination to origin should provide the valid FlightID.")
                break
            if back_intercity_transport_plan['FlightID']==row['FlightID'] and back_intercity_transport_plan['start']==row['From'] and back_intercity_transport_plan['end']==row['To']:
                back_flag=1
                try: 
                    back_intercity_transport_plan['start_time']
                    back_intercity_transport_plan['end_time']
                    if row['BeginTime'] == back_intercity_transport_plan['start_time'] and row['EndTime'] == back_intercity_transport_plan['end_time']:
                        pass
                    else:
                        error_info.append(f"Incorrect duration information of given intercity transport from destination to origin {back_intercity_transport_plan['FlightID']} [start_time -> end_time].")
                except: 
                    error_info.append(f"Intercity transport from destination to origin {back_intercity_transport_plan['FlightID']} should provide the duration information.")
                
                try: 
                    back_intercity_transport_plan['price']
                    if row['Cost']==back_intercity_transport_plan['price']:
                        pass                    
                    else:
                        error_info.append(f"Incorrect price information of given intercity transport from destination to origin {back_intercity_transport_plan['FlightID']}.")
                except: 
                    error_info.append(f"Intercity transport from destination to origin {back_intercity_transport_plan['FlightID']} should provide the price information.")
                
                
                try: 
                    back_intercity_transport_plan['tickets']
                    back_intercity_transport_plan['cost']
                    if abs(back_intercity_transport_plan['price'] * back_intercity_transport_plan['tickets'] - back_intercity_transport_plan['cost']) > .1:
                        error_info.append(f"Incorrect cost information of given intercity transport from destination to origin {back_intercity_transport_plan['FlightID']} [cost = price * tickets].")
                except: 
                    error_info.append(f"Intercity transport from destination to origin {back_intercity_transport_plan['FlightID']} should provide the tickets and cost information. [cost = price * tickets].")

                break

        if back_type=='train':
            try: 
                back_intercity_transport_plan['TrainID']
            except: 
                error_info.append(f"Intercity train from destination to origin {back_intercity_transport_plan['TrainID']} should provide the valid TrainID.")
                break
                
            
            if back_intercity_transport_plan['TrainID']==row['TrainID'] and back_intercity_transport_plan['start']==row['From'] and back_intercity_transport_plan['end']==row['To']:
                back_flag=1
                try: 
                    back_intercity_transport_plan['start_time']
                    back_intercity_transport_plan['end_time']
                    if row['BeginTime'] == back_intercity_transport_plan['start_time'] and row['EndTime'] == back_intercity_transport_plan['end_time']:
                        pass
                    else:
                        error_info.append(f"Incorrect duration information of given intercity transport from destination to origin {back_intercity_transport_plan['TrainID']} [start_time -> end_time].")
                except: 
                    error_info.append(f"Intercity transport from destination to origin {back_intercity_transport_plan['TrainID']} should provide the duration information.")
                
                try: 
                    back_intercity_transport_plan['price']
                    if row['Cost']==back_intercity_transport_plan['price']:
                        pass                    
                    else:
                        error_info.append(f"Incorrect price information of given intercity transport from destination to origin {back_intercity_transport_plan['TrainID']}.")
                except: 
                    error_info.append(f"Intercity transport from destination to origin {back_intercity_transport_plan['TrainID']} should provide the price information.")
                
                
                try: 
                    back_intercity_transport_plan['tickets']
                    back_intercity_transport_plan['cost']
                    if abs(back_intercity_transport_plan['price'] * back_intercity_transport_plan['tickets'] - back_intercity_transport_plan['cost']) > .1:
                        error_info.append("Incorrect cost information of given intercity transport from destination to origin [cost = price * tickets].")
                except: 
                    error_info.append(f"Intercity transport from destination to origin {back_intercity_transport_plan['TrainID']} should provide the tickets and cost information [cost = price * tickets].")

                break
    
    if back_flag==0:
        error_info.append("No information found given intercity transport ID from destination to origin.")

    if verbose:
        if len(error_info) == 0:
            print("Intercity_transport passed!")
        else:
            print(error_info)
    return error_info


def collect_attractions_error(symbolic_input, plan_json, verbose=False):
    
    
    target_city = symbolic_input["target_city"]

    error_info = []    
    try: 
        plan_json["itinerary"]
    except:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info

    if type(plan_json["itinerary"])!= list:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info

    plan = plan_json["itinerary"]
    
    attraction_list = []

    for day_i, day_plan_i in enumerate(plan):
        for activity_i in day_plan_i["activities"]:
            try: 
                activity_i["type"]
            except: 
                continue
            if activity_i["type"] != "attraction":
                continue
            
            try: activity_i['position']
            except: 
                error_info.append(f"No position information in attraction activity, day {day_i+1}.")
                continue
            
            select_attraction=attractions.select(target_city,key='name',func=lambda x:x==activity_i['position'])

            if select_attraction.empty:
                error_info.append(f"Attraction activity, {activity_i['position']}, in day {day_i+1} is not valid in the provided information.")
                continue

            else:
                attraction_list.append(activity_i['position'])
            
            # 开放时间
            opentime, endtime = select_attraction["opentime"].values[0],  select_attraction["endtime"].values[0]
            if time_compare_if_earlier_equal(endtime, opentime):
                endtime = str(int(endtime.split(":")[0]) + 24) + ":" + endtime.split(":")[1]
            try: 
                activity_i["start_time"]
                activity_i["end_time"]

                # if time_compare_if_earlier_equal(endtime, activity_i["start_time"]) or time_compare_if_earlier_equal(activity_i["end_time"], opentime): 
                if not (time_compare_if_earlier_equal(opentime, activity_i["start_time"]) and time_compare_if_earlier_equal(activity_i["end_time"], endtime)):
                    error_info.append(f"The attraction, {activity_i['position']} in day {day_i+1}, is closed when you visiting. Its open time is [{opentime} -- {endtime}]")
                
            except:
                error_info.append(f"The attraction activity, {activity_i['position']} in day {day_i+1}, shoud provide the visiting time.")

            # 返回信息保证一致: price
            try: 
                activity_i["price"]
                if int(activity_i["price"]) != int(select_attraction["price"].values[0]):
                    error_info.append(f"Incorrect price infomation of attraction ,{activity_i['position']} in day {day_i+1}.")

            except: 
                # table_statistics.loc[0,  'Incorrect price Information of attraction'] = 1
                error_info.append(f"The attraction activity, {activity_i['position']} in day {day_i+1}, shoud provide the price information.")

            try: 
                activity_i["tickets"]
                activity_i["cost"]
                if abs(activity_i["price"] * activity_i["tickets"] - activity_i["cost"]) > .1:
                    error_info.append(f"Incorrect cost information of attraction activity, {activity_i['position']} in day {day_i+1}, [cost = price * tickets].")
                        
            except: 
                error_info.append(f"Incorrect cost information of attraction activity, {activity_i['position']} in day {day_i+1}, [cost = price * tickets].")



    if len(set(attraction_list)) != len(attraction_list):
        error_info.append("Attraction choices should not be repeated throughout the trip.")

    if verbose:
        if len(error_info) == 0: 
            print("Attractions passed!")
        else:
            print(error_info)
            # print(table_statistics)
    return error_info
    

def collect_hotels_error(symbolic_input, plan_json, verbose=False): 

    target_city = symbolic_input["target_city"]
    error_info = []    
    try: 
        plan_json["itinerary"]
    except:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info
    
    if type(plan_json["itinerary"])!= list:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info

    plan = plan_json["itinerary"]
    
    hotel_list = []
 
    for day_i, day_plan_i in enumerate(plan):
        for activity_i in day_plan_i["activities"]:

            try: activity_i["type"]
            except: 
                continue
            if activity_i["type"] != "accommodation":
                continue

            # print(activity_i)
            
            try: activity_i['position']
            except: 
                error_info.append(f"No position information in accommodation activity, day {day_i+1}.")
                continue
            
            select_hotel=accommodation.select(target_city,key='name',func=lambda x:x==activity_i['position'])

            if select_hotel.empty:
                error_info.append(f"Accommodation activity, {activity_i['position']}, in day {day_i+1} is not valid in the provided information.")
                continue

            else:
                hotel_list.append(activity_i['position'])

            # 返回信息保证一致: price
            try: 
                activity_i["price"]
                if activity_i["price"] != select_hotel["price"].values[0]:
                    error_info.append(f"Incorrect price infomation of accommodation ,{activity_i['position']} in day {day_i+1}.")
            except: 
                error_info.append(f"The accommodation activity, {activity_i['position']} in day {day_i+1}, shoud provide the price information.")
                    
            try: 
                activity_i["room_type"]
                if type(activity_i["room_type"]) != int:
                    error_info.append(f"Incorrect room_type infomation of accommodation activity, {activity_i['position']} in day {day_i+1}. The room type should be an integer, equaling to the num_bed information of the selected accommodation.")
                if activity_i["room_type"] != select_hotel["numbed"].values[0]:
                    error_info.append(f"Incorrect room_type infomation of accommodation activity, {activity_i['position']} in day {day_i+1}. The room type should be an integer, equaling to the num_bed information of the selected accommodation.")
                
            except: 
                error_info.append(f"The accommodation activity, {activity_i['position']} in day {day_i+1}, shoud provide the room_type information. The room type should be an integer, equaling to the num_bed information of the selected accommodation.")

            
            try:
                activity_i["rooms"]
                if abs(activity_i["rooms"] * activity_i["price"] - activity_i["cost"]) > .1:
                    error_info.append("Incorrect cost information of accommodation. [cost = price * rooms]")
            except: 
                table_statistics.loc[0,  'Incorrect cost Information of Accommodation'] = 1
                error_info.append("Cost and rooms information should be provided. [cost = price * rooms]")
            

    if len(set(hotel_list)) > 1:
        error_info.append("Accommodation should be unique during the trip.")
    
    if len(plan_json["itinerary"]) > 1 and len(hotel_list) == 0:
        error_info.append("We need a hotel for a trip more than one day.")
        
    if verbose:
        if len(error_info) == 0:
            print("Hotels passed!")
        else:
            print(error_info)
    return error_info

def collect_restaurants_error(symbolic_input, plan_json, verbose=False): 
    
    target_city = symbolic_input["target_city"]
    # table_statistics = pd.DataFrame(columns=['Unavailable Restruants', 'Visiting Restruants in their closed time', 'Repeated Restruants Choices', 'Incorrect price Information of Restruants', 'Inappropriate Meal Times'])

    error_info = []    
    try: 
        plan_json["itinerary"]
    except:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info
    
    if type(plan_json["itinerary"])!= list:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info

    # table_statistics.loc[0] = [0, 0, 0, 0, 0]

    plan = plan_json["itinerary"]
    
    restaurants_list = []
    restaurants_time_list = []

    for day_i, day_plan_i in enumerate(plan):
        for activity_i in day_plan_i["activities"]:
            try: activity_i["type"]
            except: continue
            if not activity_i["type"] in ["breakfast", "lunch", "dinner"]:
                continue
            
            # print(activity_i)
            try: activity_i['position']
            except: 
                error_info.append(f"No position information in restaurant activity, day {day_i+1}.")
                continue
            

            select_restaurant=restaurants.select(target_city,key='name',func=lambda x:x==activity_i['position'])

            # print(select_restaurant)

            if activity_i["type"] == "breakfast" and select_restaurant.empty:

                select_hotel=accommodation.select(target_city,key='name',func=lambda x:x==activity_i['position'])
    
                if select_hotel.empty:
                    error_info.append(f"Breakfast activity, {activity_i['position']}, in day {day_i+1} is not valid in the provided information.")
                    continue
                try:
                    activity_i["price"]
                    if activity_i["price"] != 0:
                        table_statistics.loc[0,  'Incorrect price Information of Restruants'] = 1
                        error_info.append(f"Have breakfast at hotel in day {day_i+1}, price should be 0")
                except: 
                    error_info.append(f"The breakfast activity, {activity_i['position']} in day {day_i+1}, shoud provide the price information. If you have breakfast at hotel, the price is 0.")

                try:
                    activity_i["start_time"]
                    activity_i["end_time"]

                    if time_compare_if_earlier_equal("09:00", activity_i["start_time"]):
                        error_info.append(f"The start_time of breakfast activity, {activity_i['position']} in day {day_i+1}, cannot be later than 09:00.")
                        
                    if time_compare_if_earlier_equal(activity_i["end_time"], "06:00"):
                        error_info.append(f"The end_time of breakfast activity, {activity_i['position']} in day {day_i+1}, cannot be earlier than 06:00.")

                except:
                    error_info.append(f"The start_time and end_time of breakfast activity, {activity_i['position']} in day {day_i+1}, should be provided")

                try:
                    activity_i["cost"]
                    if abs(symbolic_input["people_number"] * activity_i["price"] - activity_i["cost"]) > .1:
                        error_info.append("Incorrect cost information of Restruants Events [cost = price * people_number].")
                except:
                    error_info.append("The Restruants Events should provide cost information")

                continue
            
            if select_restaurant.empty:
                # return return_info(False, "No information found given restaurant [{}]".format(activity_i['position']))
                # error_info.append("No information found given restaurant [{}]".format(activity_i['position']))
                error_info.append(f"Breakfast activity, {activity_i['position']}, in day {day_i+1} is not valid in the provided information.")
                continue
            
            try:
                activity_i["price"]
                if activity_i["price"] != select_restaurant["price"].values[0]:
                    error_info.append(f"Incorrect price infomation of restaurant activity, {activity_i['position']}] in day {day_i+1}")
            except:
                # table_statistics.loc[0,  'Incorrect price Information of Restruants'] = 1
                # error_info.append("price of Restruants should be provided")
                error_info.append(f"The restaurant activity, {activity_i['position']} in day {day_i+1}, shoud provide the price information.")

            
            try:
                activity_i["start_time"]
                activity_i["end_time"]
                if activity_i["type"] == "lunch":
                    if time_compare_if_earlier_equal("14:00", activity_i["start_time"]):
                        error_info.append(f"The start_time of lunch activity, {activity_i['position']} in day {day_i+1}, cannot be later than 14:00.")
                    
                    if time_compare_if_earlier_equal(activity_i["end_time"], "11:00"):
                        error_info.append(f"The end_time of lunch activity, {activity_i['position']} in day {day_i+1}, cannot be earlier than 11:00.")

                if activity_i["type"] == "dinner":
                    if time_compare_if_earlier_equal("20:00", activity_i["start_time"]):
                        error_info.append(f"The start_time of dinner activity, {activity_i['position']} in day {day_i+1}, cannot be later than 20:00.")
                    
                    if time_compare_if_earlier_equal(activity_i["end_time"], "17:00"):
                        error_info.append(f"The end_time of dinner activity, {activity_i['position']} in day {day_i+1}, cannot be earlier than 17:00.")

            except:
                error_info.append(f"The restruant activity, {activity_i['position']} in day {day_i+1}, shoud provide the start_time and end_time.")
            
            try:
                activity_i["cost"]
                if abs(symbolic_input["people_number"] * activity_i["price"] - activity_i["cost"]) > .1:
                    error_info.append("Incorrect cost information of Restruants Events [cost = price * people_number].")
            except:
                error_info.append("The Restruants Events should provide cost information")
            
            # 开放时间
            opentime, endtime = select_restaurant["opentime"].values[0],  select_restaurant["endtime"].values[0]
            if time_compare_if_earlier_equal(endtime, opentime):
                endtime = str(int(endtime.split(":")[0]) + 24) + ":" + endtime.split(":")[1]
            try:
                activity_i["start_time"]
                activity_i["end_time"]
                # if time_compare_if_earlier_equal(endtime, activity_i["start_time"]) or time_compare_if_earlier_equal(activity_i["end_time"], opentime): 
                if not (time_compare_if_earlier_equal(opentime, activity_i["start_time"]) and time_compare_if_earlier_equal(activity_i["end_time"], endtime)):
                    # table_statistics.loc[0,  'Visiting Restruants in their closed time'] = 1
                    error_info.append(f"The restaurant, {activity_i['position']} in day {day_i+1}, is closed when you visiting. Its open time is [{opentime} -- {endtime}]")
                
            except:
                # table_statistics.loc[0,  'Visiting Restruants in their closed time'] = 1
                # error_info.append("Schedule of Restruants should be provided")
                error_info.append(f"The restruant activity, {activity_i['position']} in day {day_i+1}, shoud provide the start_time and end_time.")

            restaurants_list.append(activity_i['position'])
            # restaurants_time_list.append(activity_i["start_time"])

    if len(set(restaurants_list)) != len(restaurants_list):

        # table_statistics.loc[0,  'Repeated Restruants Choices'] = 1
        error_info.append("Restaurants choices should not be repeated throughout the trip.")
        
    # print(restaurants_list)
    # print(restaurants_time_list)

    if verbose:
        # if table_statistics.loc[0].sum() == 0:
        if len(error_info) == 0:
            print("Restaurants passed!")
        else:
            print(error_info)
            # print(table_statistics)
    return error_info


def collect_transport_error(symbolic_input, plan_json, verbose=False): 
    

    target_city = symbolic_input["target_city"]

    error_info = []    
    try: 
        plan_json["itinerary"]
    except:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info
    
    if type(plan_json["itinerary"])!= list:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info

    plan = plan_json["itinerary"]
    for day_i, day_plan_i in enumerate(plan):
        for activity_i in day_plan_i["activities"]:

            if "transports" in activity_i:
                
                transport_i = activity_i["transports"]

                if (transport_i) == 'empty':
                    continue
                # print(transport_i)

                try:
                    transport_i["from"]
                    transport_i["to"]
                    transport_i['mode']
                    transport_i["start_time"]
                    transport_i["end_time"]
                except:
                    # table_statistics.loc[0] = [1, 1, 1, 1]
                    # error_info.append("Key Error: [start, end, start_time, end_time]")
                    error_info.append("Innercity transport should provide the information, 'from', 'to', 'mode', 'start_time', and 'end_time'. ")

                source_poi = transport_i["from"]
                target_poi = transport_i["to"]
                start_time = transport_i["start_time"]
                end_time = transport_i["end_time"]

                
                if transport_i['mode'] == "metro":
                    try:
                        tools_return = innercity_transport.goto(city=target_city, start=source_poi, end=target_poi, start_time=start_time, transport_type="metro", verbose=False)
                    except:
                        error_info.append(f"Unavailable Inner-City Transport information in {day_i+1}, from {source_poi} to {target_poi}, start_time {start_time}, transport_type metro")
                        continue
    
                    total_price = 0
                    for item in tools_return:
                        total_price += item["cost"]
                    if abs(transport_i["cost"] - total_price * symbolic_input["people_number"]) > .1:
                        error_info.append(f"Incorrect cost infomation of innercity transport in day {day_i+1}, from {source_poi} to {target_poi}, metro. [cost = price * people_number]")
                else:
                    try:
                        tools_return = innercity_transport.goto(city=target_city, start=source_poi, end=target_poi, start_time=start_time, transport_type=transport_i['mode'], verbose=False)
                    except:
                        error_info.append(f"Unavailable Inner-City Transport information in {day_i+1}, from {source_poi} to {target_poi}, start_time {start_time}, transport_type {transport_i['mode']}")
                        continue
                    if transport_i['mode'] == "taxi":
                        real_cost = tools_return[0]["cost"] * math.ceil(symbolic_input["people_number"]/4)
                    else:
                        real_cost = 0
                    if abs(transport_i["cost"] - real_cost) > .1:
                        error_info.append(f"Incorrect cost infomation of innercity transport in day {day_i+1}, from {source_poi} to {target_poi}, {transport_i['mode']}. [cost = price * math.ceil(people_number/4)]")
                
                # print("passed")

    if verbose:
        if len(error_info) == 0:
            print("Innercity transport  passed!")
        else:
            print(error_info)
            # print(table_statistics)
    return error_info

def time_compare_if_earlier_equal(time_1, time_2):

    time1 = float(time_1.split(":")[0])*60 + float(time_1.split(":")[1])
    time2 = float(time_2.split(":")[0])*60 + float(time_2.split(":")[1])
    
    
    return time1 <= time2

def time2real(time_str):
    time_str = time_str.split("次日")[-1]
    return float(time_str.split(":")[0])*60 + float(time_str.split(":")[1])

def collect_time_error(symbolic_input, plan_json, verbose=False): 
    

        
    target_city = symbolic_input["target_city"]


    # table_statistics = pd.DataFrame(columns=['Chronological Order'])

    error_info = []    
    try: 
        plan_json["itinerary"]
    except:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info
    
    if type(plan_json["itinerary"])!= list:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info

    # table_statistics.loc[0] = [0]

    plan = plan_json["itinerary"]
    for day_i, day_plan_i in enumerate(plan):
        for activity_i in day_plan_i["activities"]:
            
            # print(activity_i)
            try: activity_i["start_time"] and activity_i["end_time"]
            except: 
                error_info.append("Any Activity should provide start_time and end_time")
                continue
    
            activity_st_time = activity_i["start_time"]
            activity_ed_time = activity_i["end_time"]

            if time2real(activity_st_time) >= time2real(activity_ed_time) and (not activity_i["type"] in ["train", "airplane"]): # 可能出现次日到达
                error_info.append("Activities must cost time, the end_time should be later than the start_time.")
            

            if not "transports" in activity_i:
                continue

            if activity_i["transports"]!='empty':
                transport_st_time = activity_i["transports"]["start_time"]
                transport_ed_time = activity_i["transports"]["end_time"]
            
                if time2real(activity_st_time) < time2real(transport_ed_time):
                    
                    error_info.append(f"Must arrive at the location, {activity_i['position']} in day {day_i+1}, before starting the activity at {activity_st_time}.")

            

    if verbose:
        if len(error_info) == 0:
            print("Time passed!")
        else:
            print(error_info)
            # print(table_statistics)
    return error_info



def collect_space_error(symbolic_input, plan_json, verbose=False): 
    
    
    target_city = symbolic_input["target_city"]


    # table_statistics = pd.DataFrame(columns=['Transport information across positions'])

    error_info = []    
    try: 
        plan_json["itinerary"]
    except:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info
    
    if type(plan_json["itinerary"])!= list:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info

    # table_statistics.loc[0] = [0]

    plan = plan_json["itinerary"]
    
    position_list = []

    for day_i, day_plan_i in enumerate(plan):
        for activity_i in day_plan_i["activities"]:
            
            if "position" not in activity_i:

                try:
                    if activity_i["type"] in ["airplane", "train"]:
                        current_position = activity_i["start"]
                    else:
                        raise Exception("All activities except intercity transport activities need to provide position information.")
                
                except:
                    error_info.append("All activities except intercity transport activities need to provide position information.")
                    return error_info

            else:
                current_position = activity_i['position']
                
            if "transports" not in activity_i:
                # print(activity_i)
                # table_statistics.loc[0] = [1]
                # error_info.append("Need trasnports: ".format(activity_i))
                
                error_info.append(f"There should be an innercity-transport to {activity_i['position']}, in day {day_i+1}.")


            # try: activity_i['position'] and activity_i["transports"]
            # except: return False
            
            
            
            position_i = current_position

            if (len(position_list) > 0) and position_i != position_list[-1]:

                if not "transports" in activity_i:
                    # table_statistics.loc[0] = [1]
                    error_info.append(f"There must be an innercity transport from {position_list[-1]} to {position_i}, in day {day_i+1}.")
                    position_list.append(position_i)
                    continue

                if (activity_i["transports"]=='empty'):
                    error_info.append(f"There must be an innercity transport from {position_list[-1]} to {position_i}, in day {day_i+1}.")
                    position_list.append(position_i)
                    continue

                if "from" in activity_i["transports"] and activity_i["transports"]["from"] != position_list[-1]:
                    error_info.append(f"The origin of the innercity-transport to {position_i} must be equal to the position of the previous activity {position_list[-1]}")
                
                if "to" in activity_i["transports"] and activity_i["transports"]["to"] != position_i:
                    error_info.append(f"The destination of the innercity-transport to {position_i} must be equal to the position of the current activity {position_i}.")
                
            
                

            if "position" in activity_i:
                position_list.append(activity_i['position'])
            else:
                try:
                    if activity_i["type"] in ["airplane", "train"]:
                        position_list.append(activity_i["end"])
                except:
                    error_info.append("All activities except intercity transport activities need to provide position information.")
                    return error_info
        
        if day_i < len(plan) - 1 and day_plan_i["activities"][-1]['type'] != 'accommodation':
            error_info.append(f"The type of the last activity on day {day_i+1} should be accommodation. Except for the last day of the trip, the last activity at night on other days should be returning to the hotel in the plan. ")

                


    # print("position_list: ", position_list)


    if verbose:
        if len(error_info) == 0:
            print("Space passed!")
        else:
            print(error_info)
            # print(table_statistics)
    return error_info



def collect_type_error(symbolic_input, plan_json, verbose=False): 
    
    
    target_city = symbolic_input["target_city"]


    # table_statistics = pd.DataFrame(columns=['Transport information across positions'])

    error_info = []    
    try: 
        plan_json["itinerary"]
    except:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info
    
    if type(plan_json["itinerary"])!= list:
        error_info = ["Format Error. Please strictly follow the instructions in the prompt."]
        return error_info

    # table_statistics.loc[0] = [0]

    plan = plan_json["itinerary"]
    
    error_info = []
    for day_i, day_plan_i in enumerate(plan):
        for activity_i in day_plan_i["activities"]:
            try:
                activity_i['type']
            except:
                error_info.append("Format Error. Please strictly follow the instructions in the prompt.")
                continue
            if not activity_i['type'] in ['airplane','attraction','lunch','dinner','breakfast','accommodation','train']:
                error_info.append("The type of any given activity should be one of the following: 'airplane' , 'attraction' , 'lunch' , 'dinner' , 'breakfast' , 'accommodation' , or 'train' .")


    # print("position_list: ", position_list)


    if verbose:
        if len(error_info) == 0:
            print("Activity Type passed!")
        else:
            print(error_info)
            # print(table_statistics)
    return error_info



def collect_commonsense_constraints_error(symbolic_input, plan_json, verbose=False):
    

    func_list = [collect_type_error, collect_intercity_transport_error, collect_attractions_error, collect_hotels_error, collect_restaurants_error, collect_transport_error, collect_time_error, collect_space_error]
    
    succ_flag = True
    error_list = []
    for func in func_list:
        try: 
            error_info = func(symbolic_input, plan_json, verbose=verbose)
            # print(error_info)
        except Exception as e:
            error_info = [f"Raise error in symoblic commonsense feedback, {str(func)}: {str(e)}"]

        if len(error_info) > 0:
            succ_flag = False
        for ee in error_info:
            error_list.append(ee)
            
            
        # except Exception:
            
        #     print(Exception)
    
    if not succ_flag:
        print("Commonsense constraints failed!")
        # for err_info in error_list:
        #     print(err_info)
    else:
        print("Commonsense constraints passed!")


    return error_list            
    
    
    
def evaluate_commonsense_constraints(data_index, symbolic_input_dict, plan_json_dict, verbose=False):
    # assert len(symbolic_input_list)==len(plan_json_list)

    func_list = [Is_intercity_transport_correct, Is_attractions_correct, Is_hotels_correct, Is_restaurants_correct, Is_transport_correct, Is_time_correct, Is_space_correct]
    total_correct = 0

    individual_results = []
    results_per_sample=[]


    result_agg = pd.DataFrame(columns=['data_id'])
    result_agg['data_id'] = data_index

    individual_succ = 0

    for ii, idx in tqdm(enumerate(data_index), total=len(data_index)):
    # for i,(symbolic_input,plan_json) in enumerate(zip(symbolic_input_list,plan_json_list)):
        


        symbolic_input, plan_json = symbolic_input_dict[idx], plan_json_dict[idx]  
        
        if verbose:
            print(symbolic_input)
            print(plan_json)
        
        for func in func_list:

            table_res, error_info = func(symbolic_input, plan_json, verbose=verbose)
            for colum_i in table_res.columns:
                if colum_i not in result_agg.columns:
                    result_agg[colum_i] = 0

                result_agg.loc[ii, colum_i] = table_res[colum_i].loc[0]

            # print(info)
        if result_agg.loc[ii][1:].sum() == 0:
            individual_succ += 1
                            

    total_count=len(data_index)
    micro_accuracy = 1. - result_agg.drop("data_id", axis=1).sum().sum() / (total_count * (result_agg.shape[1] - 1))
    
    macro_accuracy = individual_succ / total_count

    return macro_accuracy*100, micro_accuracy*100, result_agg

if __name__ == "__main__":
    
    
    
    # test_example=load_json_file("./example/query_53.json")
    # test_plan=load_json_file("./example/plan_53.json")
    # evaluate_commonsense_constraints([test_example], [test_plan])
    
    # exit(0)
    
    symbolic_input_list=[]
    plan_json_list=[]

    for i in range(1):
        test_plan_path='./example/a_result.json'.format(i+1)
        test_example_path='./example/a_query.json'.format(i+1)
        test_example=load_json_file(test_example_path)
        test_plan=load_json_file(test_plan_path)
        symbolic_input_list.append(test_example)
        plan_json_list.append(test_plan)
    macro_accuracy, micro_accuracy, _ =evaluate_commonsense_constraints(symbolic_input_list,plan_json_list)
    print('macro: {}%, micro: {}%'.format(macro_accuracy,micro_accuracy))

    # test_plan_path='./example/plan_4.json'
    # test_example_path='./example/query_4.json'
    # test_example=load_json_file(test_example_path)
    # test_plan=load_json_file(test_plan_path)

    # print(Is_intercity_transport_correct(test_example,test_plan))
    # print(Is_attractions_correct(test_example,test_plan))
    # print(Is_hotels_correct(test_example,test_plan))
    # print(Is_restaurants_correct(test_example,test_plan))
    # print(Is_transport_correct(test_example,test_plan))
    # print(Is_time_correct(test_example,test_plan))
    # print(Is_space_correct(test_example,test_plan))

    
    # pass_flag = True

    

    # info_list = []
    # for func_i in func_list:
    #     flag, info = func_i(test_example,test_plan)

    #     print(info)

    #     pass_flag = pass_flag and flag
    #     info_list.append(info)

    # print("final result: ", pass_flag)
    
    # for item in info_list:
    #     print(item)
    # print(info_list)

