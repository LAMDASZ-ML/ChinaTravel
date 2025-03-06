


import sys
import os 

# from chinatravel.environment.tools.accommodations.apis import Accommodations
# from chinatravel.environment.tools.restaurants.apis import Restaurants
# from chinatravel.environment.tools.attractions.apis import Attractions
# from chinatravel.environment.tools.intercity_transport.apis import IntercityTransport
# from chinatravel.environment.tools.transportation.apis import Transportation

from chinatravel.evaluation.utils import load_json_file

from chinatravel.symbol_verification.hard_constraint import get_symbolic_concepts, evaluate_constraints, evaluate_constraints_py

from tqdm import tqdm

import pandas as pd

# accommodation = Accommodations()
# restaurants = Restaurants()
# attractions = Attractions()




def evaluate_hard_constraints(data_index, symbolic_input_dict, plan_json_dict, verbose=False):
    
    result_agg = pd.DataFrame(columns=['data_id', 
                                        'Trip_Days', 'Trip_People', 
                                        'Required_InterCity_Transport_Type', 
                                        'Required_Transport_Type', 
                                        'Required_Attraction_Type', 'Required_Attraction', 
                                        'Required_Hotel_Type', 'Required_Hotel', 'Required_Room_Type', 'Required_Room_Count', 
                                        'Required_Restruant_Type', 'Required_Restaurants', 
                                        'Budget'])
    result_agg['data_id'] = data_index
    for col_i in result_agg.columns[1:]:
        result_agg[col_i] = 0

    macro_count, macro_succ_count = 0, 0
    micro_count, micro_succ_count = 0, 0
    

    results=[]
    passed_id = []

    for ii, idx in enumerate(data_index):
        symbolic_input, plan_json = symbolic_input_dict[idx], plan_json_dict[idx]  
        
        extracted_vars=get_symbolic_concepts(symbolic_input,plan_json, need_ood=True)
        
    
        
        result_ii = evaluate_constraints(extracted_vars, symbolic_input["hard_logic"])
        
        
        if verbose:
            print("symoblic concepts: ", extracted_vars)
            print(symbolic_input["hard_logic"])
            print(result_ii)
        results.append(result_ii)
        
        dict_ii = {}

        for j, logical_i in enumerate(symbolic_input["hard_logic"]):
            
            if "days" in logical_i:
                col_name = "Trip_Days"
            elif "people_number" in logical_i:
                col_name = "People_Number"
            elif "tickets" in logical_i:
                col_name = "People_Number"
            elif "intercity_transport" in logical_i:
                col_name = "Required_InterCity_Transport_Type"
            elif "transport_type" in logical_i:
                col_name = "Transport_Type"
            elif "spot_type" in logical_i:
                col_name = "Required_Attraction_Type"
            elif "attraction_names" in logical_i:
                col_name = "Required_Attraction"
            elif "hotel_feature" in logical_i:
                col_name = "Required_Hotel_Type"
            elif "hotel_names" in logical_i:
                col_name = "Required_Hotel"
            elif "room_type" in logical_i:
                col_name = "Required_Room_Type"
            elif "rooms" in logical_i:
                col_name = "Required_Room_Count"
            elif "food_type" in logical_i:
                col_name = "Required_Restruant_Type"
            elif "restaurant_names" in logical_i:
                col_name = "Required_Restaurants"

            elif "cost" in logical_i:
                col_name = "Budget"
            elif "price" in logical_i:
                col_name = "Budget"

            # result_agg[col_name, ii] = result_ii[j]
            if not col_name in dict_ii:
                dict_ii[col_name] = int(result_ii[j])
            else:
                if result_ii[j] == 0:
                    dict_ii[col_name] = 0
        
        result_agg.loc[ii] = pd.Series(dict_ii)
        

        succ_c_sum = 0
        for col in dict_ii.keys():
            # print(col, dict_ii[col])
            succ_c_sum += dict_ii[col]
        
        # print(dict_ii)
        # print(succ_c_sum, len(dict_ii))

        macro_count += 1
        macro_succ_count += (succ_c_sum == len(dict_ii))
        micro_count += len(dict_ii)
        micro_succ_count += succ_c_sum

        if succ_c_sum == len(dict_ii):
            passed_id.append(idx)

    # macro, micro, _ = calculate_metrics(results)

    macro = macro_succ_count / macro_count
    micro = micro_succ_count / micro_count

    return macro*100, micro*100, result_agg, passed_id


def evaluate_hard_constraints_v2(data_index, symbolic_input_dict, plan_json_dict, env_pass_id, verbose=False):


    max_logic_num = 0
    for idx in data_index:
        max_logic_num = max(max_logic_num, len(symbolic_input_dict[idx]["hard_logic_py"]))

    columns=['data_id']
    for i in range(max_logic_num):
        columns.append(f'logic_py_{i}')
    result_agg = pd.DataFrame(columns=columns)
    # result_agg['data_id'] = data_index
    for col_i in result_agg.columns[1:]:
        result_agg[col_i] = 0

    macro_count, macro_succ_count = 0, 0
    micro_count, micro_succ_count = 0, 0
    
    conditional_micro_succ_count, conditional_macro_succ_count = 0, 0

    results=[]
    passed_id = []

    for ii, idx in enumerate(tqdm(data_index)):
        symbolic_input, plan_json = symbolic_input_dict[idx], plan_json_dict[idx]  
        result_ii = evaluate_constraints_py(symbolic_input["hard_logic_py"], plan_json, verbose=verbose)
        results.append(result_ii)

        # print(symbolic_input)
        # print(plan_json)

        if verbose:
            for logic_i, res_i in zip(symbolic_input["hard_logic_py"], result_ii):
                print(logic_i, "\n", "[", res_i, "]")

        dict_ii = {}
        succ_c_sum = 0
        for logic_i in range(len(symbolic_input["hard_logic_py"])):
            dict_ii[f'logic_py_{logic_i}'] = int(result_ii[logic_i])
            succ_c_sum += int(result_ii[logic_i])
        

        macro_count += 1
        macro_succ_count += (succ_c_sum == len(dict_ii))
        micro_count += len(dict_ii)
        micro_succ_count += succ_c_sum

        if idx in env_pass_id:
            conditional_micro_succ_count += succ_c_sum
            conditional_macro_succ_count += (succ_c_sum == len(dict_ii))

        if succ_c_sum == len(dict_ii):
            passed_id.append(idx)
        
        dict_ii["data_id"] = idx
        result_agg.loc[ii] = pd.Series(dict_ii)
        
        # else:
        #     print(symbolic_input["hard_logic_py"])
        #     print(result_ii)
        #     print(plan_json)

    macro = macro_succ_count / macro_count
    micro = micro_succ_count / micro_count

    c_marco = conditional_macro_succ_count / macro_count
    c_micro = conditional_micro_succ_count / micro_count

    print("conditional_micro_succ_count: ", conditional_micro_succ_count)
    print("conditional_macro_succ_count: ", conditional_macro_succ_count)

    return macro*100, micro*100, c_marco*100, c_micro*100, result_agg, passed_id

if __name__ == "__main__":
    
    symbolic_input_list=[]
    plan_json_list=[]

    for i in range(1):
        test_plan_path='./example/plan_{}.json'.format(i+1)
        test_example_path='./example/query_{}.json'.format(i+1)
        test_example=load_json_file(test_example_path)
        test_plan=load_json_file(test_plan_path)
        symbolic_input_list.append(test_example)
        plan_json_list.append(test_plan)
    macro_accuracy, micro_accuracy,_=evaluate_hard_constraints(symbolic_input_list,plan_json_list)
    print('macro: {}%, micro: {}%'.format(macro_accuracy,micro_accuracy))