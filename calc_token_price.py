

import argparse

import numpy as np

import sys
import os
import json

project_root_path = os.path.dirname(os.path.abspath(__file__))
if project_root_path not in sys.path: sys.path.insert(0, project_root_path)


from chinatravel.data.load_datasets import load_query
from chinatravel.evaluation.utils import load_json_file, validate_json


METHOD_LIST = [
    "example" "act_Deepseek_zeroshot",
    "act_GPT4o_zeroshot",
    "react_Deepseek_zeroshot",
    "react_GPT4o_zeroshot",
    "react_GLM4Plus_zeroshot",
    "react_Deepseek_oneshot",
    "react_GPT4o_oneshot",
    "naive_ns_Deepseek",
    "naive_ns_GPT4o",
    "naive_ns_GLM4Plus",
]


def load_result(args, query_index, verbose=False):

    def load_result_for_method(method):
        plans = {}
        for query_id in query_index:
            result_file = os.path.join(
                "results/", method, "{}.json".format(query_id)
            )

            try:
                if os.path.exists(result_file):
                    result = load_json_file(result_file)
                    plans[query_id] = result
                else:
                    plans[query_id] = {}
            except:
                plans[query_id] = {}
        return plans

    result = {}
    if args.method == "all":
        method_list = []
        for mi in METHOD_LIST:
            if mi != "example":
                method_list.append(mi)
    else:
        method_list = [args.method]

    for method in method_list:
        result[method] = load_result_for_method(method)

    if verbose:
        print(result)

    return method_list, result
if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument("--splits", "-s", type=str, default="example")
    parser.add_argument(
        "--method", "-m", type=str, default="example"
    )  # , choices=METHOD_LIST)
    args = parser.parse_args()

    print(args)

    
    query_index, query_data = load_query(args)
    method_list, result_data = load_result(args, query_index)


    input_token_count = []
    output_token_count = []
    input_token_maxx = []


    for method in method_list:
        print(method)
        print("There are {} results...".format(len(result_data[method])))
        for query_id in query_index:

            result = result_data[method][query_id]
            if "input_token_count" in result:
                input_token_count.append(result["input_token_count"])
            if "output_token_count" in result:
                output_token_count.append(result["output_token_count"])
            if "input_token_maxx" in result:
                input_token_maxx.append(result["input_token_maxx"])
            
    input_mean = np.mean(input_token_count)
    output_mean = np.mean(output_token_count)

    if 'deepseek' in args.method:
        input_price = 0.5 * 1e-6 * 0.1387  # 1RMB = 0.1387 USD
        output_price = 2 * 1e-6 * 0.1387    # 1RMB = 0.1387 USD
    elif 'Llama' in args.method:
        input_price = 0.18 * 1e-6   
        output_price = 0.18 * 1e-6     
        # https://www.together.ai/models/llama-3-1
    elif 'mistral' in args.method:
        input_price = 0.0001 * 1e-3   
        output_price = 0.0002 * 1e-3     
    else:
        raise Exception('Please provide the price for the method: {}'.format(args.method))
    


    print("Input token mean: {}".format(input_mean))
    print("Output token mean: {}".format(output_mean))
    print("Input token maxx: {}".format(np.mean(input_token_maxx)))


    print("Price per query: {}".format(input_mean * input_price + output_mean * output_price))


            



# LLMNeSy_deepseek_oracletranslation
# There are 154 results...
# Input token count: 13869.233766233767
# Output token count: 3871.7272727272725
# Input token maxx: 1648.5089285714287
# LLM rec count: 21.5
# LLM rec format error count: 1.7532467532467533
# LLM rec format error rate: 0.08732860159754216
# Search nodes: 7381.974025974026
# Backtrack count: 3030.2727272727275
# Constraints validation count: 6.220779220779221
# Commonsense pass count: 5.409090909090909
# Logical pass count: 0.42207792207792205
# All constraints pass: 0.42207792207792205


# LLMNeSy_Llama3-8B_oracletranslation
# There are 154 results...
# Input token count: 50092.207792207795
# Output token count: 18098.103896103898
# Input token maxx: 1837.2818181818182
# LLM rec count: 38.51298701298701
# LLM rec format error count: 25.83116883116883
# LLM rec format error rate: 0.44144626793146896
# Search nodes: 18245.51948051948
# Backtrack count: 11022.162337662337
# Constraints validation count: 8.2012987012987
# Commonsense pass count: 2.564935064935065
# Logical pass count: 4.48051948051948
# All constraints pass: 0.19480519480519481

# LLMNeSy_mistral_oracletranslation
# There are 154 results...
# Input token count: 18705.545454545456
# Output token count: 768.6818181818181
# Input token maxx: 2257.935064935065
# LLM rec count: 23.837662337662337
# LLM rec format error count: 22.623376623376622
# LLM rec format error rate: 0.9317166129178838
# Search nodes: 10773.136363636364
# Backtrack count: 4707.194805194805
# Constraints validation count: 3.6818181818181817
# Commonsense pass count: 3.6818181818181817
# Logical pass count: 0.2857142857142857
# All constraints pass: 0.2857142857142857