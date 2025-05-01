

HOTEL_SELECTION_INSTRUCTION = """
You are a travel planning assistant. 
Your task is to rank all available hotel options based on the user's needs and the provided hotel information. Consider the following factors:
1. User preferences (e.g., comfort, cost, location).
2. Hotel features.
3. Room price per night.
4. Number of beds per room (numbed=2 for double beds, numbed=1 for single beds).
5. Proximity to key attractions or points of interest in the target city.
6. In order to meet the user's needs, provide diverse options from different perspectives such as geographical location, room characteristics, and price.
    
Additionally, keep in mind that the user's budget is allocated across multiple expenses, including intercity transportation and daily meals. Ensure that the hotel recommendations fit within the remaining budget constraints after accounting for these costs. Note that the price provided for each hotel is the cost per night per room. If the user has provided a specific budget requirement, ensure that the total cost of the hotel stay, including intercity transportation and daily meals, does not exceed this budget. Leave sufficient space in the budget for daily meals and other travel expenses.

Please provide a selected list of {required_options} hotel options based on the user's preferences. For each hotel, include the name. 

***** Example *****
The user's requirement are: 当前位置上海。我和女朋友打算去苏州玩两天，预算1300元，希望酒店每晚不超过500元。请给我一个旅行规划。
Selected Hotels: ["苏州东太湖智选假日酒店", "嘉宝酒店(苏州观前街十全街店)", "昆山城东开发区亚朵酒店", "苏州吴江宾馆", "桔子酒店(苏州园区奥体中心店)", "漫际酒店(苏州龙湖东吴天街石湖东路地铁站店)", "苏州泊Hotel", "清能宜尚PLUS酒店(苏州吴江东太湖万宝商业广场店)", "维也纳国际酒店(苏州火车站北广场店)", "锦江之星风尚(苏州园区独墅湖高教区店)"]

***** Example Ends *****
Given information: 
{hotel_info} 

The user's requirements are: {user_requirements}. 
Selected Hotels (please only output the LIST of HOTEL NAME without explanatory information):"""

ATTRACTION_SELECTION_INSTRUCTION = """
You are a travel planning assistant. 
Your task is to select and rank attractions based on the user's needs and the provided attraction information. Consider the following factors:
1. Attraction name
2. Attraction type
3. Location
4. Recommended duration
    
Additionally, keep in mind that the user's budget is allocated across multiple expenses, including intercity transportation and hotel accommodations. Ensure that the attraction recommendations fit within the remaining budget constraints after accounting for the past cost. 
To ensure a comprehensive list, consider a larger pool of candidates and prioritize diversity in attraction type and location.
Please provide a selected list of {required_options} attraction options based on the user's preferences. For each attraction, include the name. 

***** Example *****
The user's requirement are: 当前位置上海。我和女朋友打算去苏州玩两天，预算1300元，希望酒店每晚不超过500元。请给我一个旅行规划。
Selected Attractions: ["拙政园", "寒山寺", "枫桥景区", "狮子林", "虎丘山风景名胜区", "留园", "苏州博物馆", "同里古镇", "山塘街", "平江路历史街区", "金鸡湖", "网师园", "沧浪亭", "木渎古镇", "姑苏水上游", "苏州古运河游船(山塘街白居易码头)", "耦园", "西园寺", "甪直古镇", "天平山", "盘门", "锦溪古镇", "苏州博物馆西馆", "同里国家湿地公园", "观前街", "沙家浜风景区", "苏州古运河", "怡园", "金鸡湖游船", "艺圃", "可园", "苏州太湖国家湿地公园", "诚品书店(诚品生活苏州店)", "苏州湾梦幻水世界", "东太湖生态旅游度假区", "尚湖风景区", "虞山文化旅游度假区", "苏州乐园森林水世界", "上方山森林动物世界", "沙溪古镇", "琵琶语评弹茶馆(苏州平江路店)", "千灯古镇", "双桥", "虞山景区", "太湖", "苏州古运河游船(新市桥码头)", "重元寺", "黎里古镇", "香山景区", "林屋洞"]

***** Example Ends *****
Given information: 
{attraction_info} 

The user's requirements are: {user_requirements}. 
Selected Attractions (please only output the LIST of ATTRACTION NAME without explanatory information):"""

RESTAURANT_SELECTION_INSTRUCTION = """
You are a travel planning assistant. 
Your task is to select and rank restaurants based on the user's needs and the provided restaurant information. Consider the following factors:
1. Restaurant name
2. Cuisine type
3. Price range
4. Recommended food

Additionally, keep in mind that the user's budget needs to cover various expenses throughout the trip, including intercity transportation, hotel accommodations, attractions, and costs related to visiting restaurants. 
As the user has three meals each day, when recommending restaurants, ensure that the total cost of meals, along with other expenses, strictly stays within the budget. Note that the price range provided for each restaurant is the average cost per person per meal.
To ensure a comprehensive list, consider a larger pool of candidates and prioritize diversity in restaurant type and location.
Please provide a selected list of {required_options} restaurant options based on the user's preferences. For each restaurant, include the name. 

***** Example *****
The user's requirement are: 当前位置上海。我和女朋友打算去苏州玩两天，预算1300元，希望酒店每晚不超过500元。请给我一个旅行规划。
Selected Restaurants: ["得月楼(观前店)", "哑巴生煎(临顿路店)", "裕面堂·精品苏式面馆(石路店)", "孙盛兴奥灶面馆(山塘街店)", "吴记小园楼(西北街店)", "珍珠饭店", "鹤园苏帮菜(平江路店)", "平江桃花源记(平江1店)", "鑫震源·苏式大虾生煎(山塘街店)", "同得兴(十全街店)", "朱新年点心店", "乐惠馄饨店(吴趋坊店)", "明月楼·糕团店(三元坊店)"]
***** Example Ends *****
Given information: 
{restaurant_info} 

The user's requirements are: {user_requirements}. 
Selected Restaurants (please only output the LIST of RESTAURANT NAME without explanatory information):"""


TRANSPORT_GO_SELECTION_INSTRUCTION = """
You are a travel planning assistant. 
Now let's plan the journey from the origin city to the destination city. 
Your task is to rank all available intercity transport options based on the user's needs and the provided transport information. Consider the following factors: 
1. User preferences (e.g., type, comfort, cost, speed). 
2. Availability and reliability of the transport options. 

Please provide a selected list of {required_options} transport options based on the user's preferences. 

For each train transport, include the TrainID. 
For each flight transport, include the FlightID. 

***** Example *****
The user's requirement are: 当前位置北京。我和女朋友打算去上海玩两天，预算5300元，希望酒店每晚不超过500元。请给我一个旅行规划。
Selected Transports: ["G159", "FL81", "FL083", "FL090", "FL082", "D7", "G101", "G103", "G115", "Z281"]
***** Example Ends *****
Given information: 

Train Information 
{train_info}

Flight Information 
{flight_info}

The user's requirement are: {user_requirements}
Selected Transports from {origin} to {destination} : (please only output the LIST of TRANSPORT ID without explanatory information):"""



TRANSPORT_BACK_SELECTION_INSTRUCTION = """
You are a travel planning assistant. 
Now let's plan the journey from the destination city to the origin city. 
Your task is to rank all available intercity transport options based on the user's needs and the provided transport information. Consider the following factors: 
1. User preferences (e.g., type, comfort, cost, speed). 
2. Availability and reliability of the transport options. 
3. When users don't specify particular requirements, prioritize transport options with later departure times to allow for more travel time.

Please provide a selected list of {required_options} transport options based on the user's preferences. 

For each train transport, include the TrainID. 
For each flight transport, include the FlightID. 

***** Example *****
The user's requirement are: 当前位置北京。我和女朋友打算去上海玩两天，预算5300元，希望酒店每晚不超过500元。请给我一个旅行规划。
Selected Transports: ["G2", "FL009", "FL007", "FL001", "FL004", "G8", "G18", "G26", "G6", "D6"]
***** Example Ends *****
Given information: 

Train Information 
{train_info}

Flight Information 
{flight_info}

The user's requirement are: {user_requirements}
Selected Transports from {origin} to {destination} : (please only output the LIST of TRANSPORT ID without explanatory information):"""

