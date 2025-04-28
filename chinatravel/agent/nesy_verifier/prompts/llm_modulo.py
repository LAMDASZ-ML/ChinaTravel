INITIAL_PROMPT = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers, train numbers, restaurant names, accommodation names and innercity routes. Note that all the information in your plan should be derived from the provided data. You should give a travel plan in JSON format as shown in the example below. Additionally, all details should align with commonsense. 

Important Reminder: For innercity_transport, duration information (in minutes) is provided. Please infer the appropriate specific start_time and end_time for your plan by the duration. For example, if the provided information indicates that it takes 20 minutes to travel from one location to another by metro, you can utilize this duration information in your planning process. 

***** Example *****
Query: 当前位置北京。我一个人想去南京玩2天，预算3000人民币，尽量多坐地铁，喜欢吃江浙菜，想去南京博物院，请给我一个旅行规划。
Travel Plan:
[{{
    "day": 1,
    "activities": [
        {{
            "start_time": "07:16",
            "end_time": "08:23",
            "start": "北京首都国际机场",
            "end": "南京禄口国际机场",
            "cost": 448.38,
            "FlightID": "FL159",
            "type": "airplane",
            "tickets": 1,
            "transports": "empty"
        }},
        {{
            "position": "明孝陵",
            "type": "attraction",
            "transports": {{"from": "南京禄口国际机场", "to": "明孝陵", "mode": "metro", "start_time": "08:23", "end_time": "09:52", "cost": 7}},
            "cost": 65.0,
            "tickets": 1,
            "start_time": "10:00",
            "end_time": "11:20"
        }},
        {{
            "position": "鲤院(夫子庙店)",
            "type": "lunch",
            "transports": {{"from": "明孝陵", "to": "鲤院(夫子庙店)", "mode": "metro", "start_time": "11:20", "end_time": "11:50", "cost": 3}},
            "cost": 499,
            "start_time": "12:00",
            "end_time": "12:50"
        }},
        {{
            "position": "狮子山景区",
            "type": "attraction",
            "transports": {{"from": "鲤院(夫子庙店)", "to": "狮子山景区", "mode": "metro", "start_time": "12:50", "end_time": "13:30", "cost": 4}},
            "cost": 0.0,
            "tickets": 1,
            "start_time": "13:40",
            "end_time": "15:00"
        }},
        {{
            "position": "秦淮河",
            "type": "attraction",
            "transports": {{"from": "狮子山景区", "to": "秦淮河", "mode": "metro", "start_time": "15:00", "end_time": "15:46", "cost": 4}},
            "cost": 0.0,
            "tickets": 1,
            "start_time": "15:50",
            "end_time": "17:10"
        }},
        {{
            "position": "南京金陵饭店",
            "type": "accommodation",
            "transports": {{"from": "秦淮河", "to": "南京金陵饭店", "mode": "metro", "start_time": "17:10", "end_time": "17:24", "cost": 2}}, 
            "room_type": 2,
            "cost": 680,
            "start_time": "17:30",
            "end_time": "24:00",
            "rooms": 1
        }}
    ]
}},
{{
    "day": 2,
    "activities": [
        {{
            "position": "南京总统府",
            "type": "attraction",
            "transports": {{"from": "南京金陵饭店", "to": "南京总统府", "mode": "metro", "start_time": "08:00", "end_time": "08:12", "cost": 2}}, 
            "cost": 0.0,
            "tickets": 1,
            "start_time": "08:20",
            "end_time": "09:40"
        }},
        {{
            "position": "南京博物院",
            "type": "attraction",
            "transports": {{"from": "南京总统府", "to": "南京博物院", "mode": "metro", "start_time": "09:40", "end_time": "10:05", "cost": 2}}, 
            "cost": 0.0,
            "tickets": 1,
            "start_time": "10:10",
            "end_time": "11:30"
        }},
        {{
            "position": "南京大牌档(老门东店)",
            "type": "lunch",
            "transports": {{"from": "南京博物院", "to": "南京大牌档(老门东店)", "mode": "metro", "start_time": "11:30", "end_time": "11:57", "cost": 3}}, 
            "cost": 78,
            "start_time": "12:00",
            "end_time": "12:50"
        }},
        {{
            "position": "夫子庙",
            "type": "attraction",
            "transports": {{"from": "南京大牌档(老门东店)", "to": "夫子庙", "mode": "metro", "start_time": "12:50", "end_time": "13:07", "cost": 2}}, 
            "cost": 0.0,
            "tickets": 1,
            "start_time": "13:10",
            "end_time": "14:30"
        }},
        {{
            "position": "老门东历史街区",
            "type": "attraction",
            "transports": {{"from": "夫子庙", "to": "老门东历史街区", "mode": "metro", "start_time": "14:30", "end_time": "14:43", "cost": 2}}, 
            "cost": 0.0,
            "tickets": 1,
            "start_time": "14:50",
            "end_time": "16:10"
        }},
        {{
            "position": "老门东历史街区",
            "type": "dinner",
            "transports": {{"from": "夫子庙", "to": "蔣有記(老门东店)", "mode": "walk", "start_time": "16:10", "end_time": "16:21", "cost": 0}}, 
            "cost": 25,
            "start_time": "16:30",
            "end_time": "17:20"
        }},
        {{
            "start": "南京南站",
            "end": "北京南站",
            "start_time": "20:02",
            "end_time": "23:18",
            "TrainID": "G28",
            "type": "train",
            "transports": {{"from": "蔣有記(老门东店)", "to": "南京南站", "mode": "metro", "start_time": "17:20", "end_time": "17:41", "cost": 3}}, 
            "cost": 583.83,
            "tickets": 1
        }}
    ]
}}
]
***** Example Ends *****

Given information:
Transports from origin to destination 
Train
{go_train_info}
Flight
{go_flight_info}

Transports from destination to origin
Train
{back_train_info}
Flight
{back_flight_info}

Attractions in the destination city
{attraction_info}

Restaurants in the destination city
{restaurant_info}

Accommodations in the destination city
{accommodation_info}

Innercity transports in the destination city
{innercity_transport_info}

Query: {query}
Travel Plan (please only output the JSON string without explanatory information):"""


BACK_PROMPT = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers, train numbers, restaurant names, accommodation names and innercity routes. Note that all the information in your plan should be derived from the provided data. You should give a travel plan in JSON format as shown in the example below. Additionally, all details should align with commonsense. 

Important Reminder: 
1. For innercity_transport, duration information (in minutes) is provided. Please infer the appropriate specific start_time and end_time for your plan by the duration. For example, if the provided information indicates that it takes 20 minutes to travel from one location to another by metro, you can utilize this duration information in your planning process. 
2. Note that in the travel plan, the "price" for each event represents the unit price. You need to reasoning the "cost" based on the number of participants and the type of event. 

***** Example *****
Query: 当前位置北京。我一个人想去南京玩2天，预算3000人民币，尽量多坐地铁，喜欢吃江浙菜，想去南京博物院，请给我一个旅行规划。
Travel Plan:
[{{
    "day": 1,
    "activities": [
        {{
            "start_time": "07:16",
            "end_time": "08:23",
            "start": "北京首都国际机场",
            "end": "南京禄口国际机场",
            "price": 448.38,
            "cost": 448.38,
            "FlightID": "FL159",
            "type": "airplane",
            "tickets": 1,
            "transports": "empty"
        }},
        {{
            "position": "明孝陵",
            "type": "attraction",
            "transports": {{"from": "南京禄口国际机场", "to": "明孝陵", "mode": "metro", "start_time": "08:23", "end_time": "09:52", "cost": 7}},
            "price": 65.0,
            "cost": 65.0,
            "tickets": 1,
            "start_time": "10:00",
            "end_time": "11:20"
        }},
        {{
            "position": "鲤院(夫子庙店)",
            "type": "lunch",
            "transports": {{"from": "明孝陵", "to": "鲤院(夫子庙店)", "mode": "metro", "start_time": "11:20", "end_time": "11:50", "cost": 3}},
            "price": 499,
            "cost": 499,
            "start_time": "12:00",
            "end_time": "12:50"
        }},
        {{
            "position": "狮子山景区",
            "type": "attraction",
            "transports": {{"from": "鲤院(夫子庙店)", "to": "狮子山景区", "mode": "metro", "start_time": "12:50", "end_time": "13:30", "cost": 4}},
            "price": 0.0,
            "cost": 0.0,
            "tickets": 1,
            "start_time": "13:40",
            "end_time": "15:00"
        }},
        {{
            "position": "秦淮河",
            "type": "attraction",
            "transports": {{"from": "狮子山景区", "to": "秦淮河", "mode": "metro", "start_time": "15:00", "end_time": "15:46", "cost": 4}},
            "price": 0.0,
            "cost": 0.0,
            "tickets": 1,
            "start_time": "15:50",
            "end_time": "17:10"
        }},
        {{
            "position": "南京金陵饭店",
            "type": "accommodation",
            "transports": {{"from": "秦淮河", "to": "南京金陵饭店", "mode": "metro", "start_time": "17:10", "end_time": "17:24", "cost": 2}}, 
            "room_type": 2,
            "price": 680,
            "cost": 680,
            "start_time": "17:30",
            "end_time": "24:00",
            "rooms": 1
        }}
    ]
}},
{{
    "day": 2,
    "activities": [
        {{
            "position": "南京总统府",
            "type": "attraction",
            "transports": {{"from": "南京金陵饭店", "to": "南京总统府", "mode": "metro", "start_time": "08:00", "end_time": "08:12", "cost": 2}}, 
            "price": 0.0,
            "cost": 0.0,
            "tickets": 1,
            "start_time": "08:20",
            "end_time": "09:40"
        }},
        {{
            "position": "南京博物院",
            "type": "attraction",
            "transports": {{"from": "南京总统府", "to": "南京博物院", "mode": "metro", "start_time": "09:40", "end_time": "10:05", "cost": 2}}, 
            "price": 0.0,
            "cost": 0.0,
            "tickets": 1,
            "start_time": "10:10",
            "end_time": "11:30"
        }},
        {{
            "position": "南京大牌档(老门东店)",
            "type": "lunch",
            "transports": {{"from": "南京博物院", "to": "南京大牌档(老门东店)", "mode": "metro", "start_time": "11:30", "end_time": "11:57", "cost": 3}}, 
            "price": 78,
            "cost": 78,
            "start_time": "12:00",
            "end_time": "12:50"
        }},
        {{
            "position": "夫子庙",
            "type": "attraction",
            "transports": {{"from": "南京大牌档(老门东店)", "to": "夫子庙", "mode": "metro", "start_time": "12:50", "end_time": "13:07", "cost": 2}}, 
            "price": 0.0,
            "cost": 0.0,
            "tickets": 1,
            "start_time": "13:10",
            "end_time": "14:30"
        }},
        {{
            "position": "老门东历史街区",
            "type": "attraction",
            "transports": {{"from": "夫子庙", "to": "老门东历史街区", "mode": "metro", "start_time": "14:30", "end_time": "14:43", "cost": 2}}, 
            "price": 0.0,
            "cost": 0.0,
            "tickets": 1,
            "start_time": "14:50",
            "end_time": "16:10"
        }},
        {{
            "position": "老门东历史街区",
            "type": "dinner",
            "transports": {{"from": "夫子庙", "to": "蔣有記(老门东店)", "mode": "walk", "start_time": "16:10", "end_time": "16:21", "cost": 0}}, 
            "price": 25, 
            "cost": 25,
            "start_time": "16:30",
            "end_time": "17:20"
        }},
        {{
            "start": "南京南站",
            "end": "北京南站",
            "start_time": "20:02",
            "end_time": "23:18",
            "TrainID": "G28",
            "type": "train",
            "transports": {{"from": "蔣有記(老门东店)", "to": "南京南站", "mode": "metro", "start_time": "17:20", "end_time": "17:41", "cost": 3}}, 
            "price": 583.83, 
            "cost": 583.83,
            "tickets": 1
        }}
    ]
}}
]
***** Example Ends *****

Given information:
Transports from origin to destination 
Train
{go_train_info}
Flight
{go_flight_info}

Transports from destination to origin
Train
{back_train_info}
Flight
{back_flight_info}

Attractions in the destination city
{attraction_info}

Restaurants in the destination city
{restaurant_info}

Accommodations in the destination city
{accommodation_info}

Innercity transports in the destination city
{innercity_transport_info}

Query: {query}
Travel Plan:
{plan}

There are some concerns: 
{backprompt}

Fixed Travel Plan (please only output the JSON string without explanatory information):"""