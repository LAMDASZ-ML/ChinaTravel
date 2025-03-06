import sys
import os

from chinatravel.environment.tools.accommodations.apis import Accommodations
from chinatravel.environment.tools.restaurants.apis import Restaurants
from chinatravel.environment.tools.attractions.apis import Attractions
from chinatravel.environment.tools.intercity_transport.apis import IntercityTransport
from chinatravel.environment.tools.transportation.apis import Transportation

from chinatravel.symbol_verification.concept_func import func_dict
from chinatravel.evaluation.utils import load_json_file

import pandas as pd

from copy import deepcopy

accommodation = Accommodations()
restaurants = Restaurants()
attractions = Attractions()

from .concept_func import *


def evaluate_preference_py(preference_list, plan, verbose=False):


    # time_cost = 0
    # transport_count = 0
    # for activity in allactivities(plan):
    #     transports = activity_transports(activity)
    #     if transports!=[]:
    #         transport_count += 1
    #         time_cost += innercity_transport_time(transports)
    # average_time_cost = time_cost / transport_count if transport_count > 0 else -1

    # print(average_time_cost)

    
    # target_poi = '大足石刻'
    # poi_list = list()
    # total_distance = 0
    # poi_count = 0
    # city = target_city(plan)
    # for activity in allactivities(plan):
    #     if activity_type(activity) in ['breakfast', 'lunch', 'dinner', 'accommodation', 'attraction']:
    #         poi_list.append(activity_position(activity))
    # for poi in poi_list:
    #     total_distance += poi_distance(city, target_poi, poi)
    #     poi_count += 1
    # average_dist_cost = total_distance / poi_count if poi_count > 0 else -1
    # print(average_dist_cost)

    results = []
    # hard_logic_py.append(debug_logic_py)
    for _, preference_concept, preference_code in preference_list:
        vars_dict = deepcopy(func_dict)
        vars_dict["plan"] = plan
        # exec(constraint, {"__builtins__": {"set": set, "print": print}}, vars_dict)
        # results.append(vars_dict.get("result", False))
        try:
            # Evaluate the constraint in a safe manner
            exec(
                preference_code,
                {
                    "__builtins__": {
                        "set": set,
                        "list": list,
                    }
                },
                vars_dict,
            )
            res_i = vars_dict.get(preference_concept, None)
            # if type(res_i) != float:
            #     raise Exception("The result of the constraint must be a float value.")
            # if res_i == -1:
            #     raise Exception("return -1")
            
            results.append(float(res_i))
            # results.append(result)
        except Exception as e:
            if verbose:
                print(f"Error evaluating preference '{preference_code}': {e}")
            results.append(None)
        # print(results)
    return results
