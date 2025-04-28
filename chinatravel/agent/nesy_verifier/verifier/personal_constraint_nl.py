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

def collect_personal_error(problem, plan, verbose=False):
    
    if not 'hard_logic_nl' in problem:
        print(f"Data id {problem['uid']}, no hard_logic_nl information.")
        return []
    if len(problem["hard_logic_py"]) != len(problem["hard_logic_nl"]):
        print(f"Data id {problem['uid']}, hard_logic_py and hard_logic_nl are not consistent.")
        return []

    error_info = []
    for idx, constraint in enumerate(problem["hard_logic_py"]):
        vars_dict = deepcopy(func_dict)
        vars_dict["plan"] = plan
        # exec(constraint, {"__builtins__": {"set": set, "print": print}}, vars_dict)
        # results.append(vars_dict.get("result", False))
        try:
            # Evaluate the constraint in a safe manner
            exec(
                constraint,
                {
                    "__builtins__": {
                        "set": set,
                    }
                },
                vars_dict,
            )
            res_i = vars_dict.get("result", False)
            # results.append(bool(res_i))
            if not res_i:
                error_info.append(f"用户要求未被满足：{problem['hard_logic_nl'][idx]}")
        except Exception as e:
            if verbose:
                print(f"Error evaluating constraint '{constraint}': {e}")
            error_info.append(f"Raise Error when evaluating constraint {problem['hard_logic_nl'][idx]}")
        # print(results)
    return error_info