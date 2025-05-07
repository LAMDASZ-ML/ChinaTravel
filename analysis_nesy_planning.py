

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
    llm_rec_count = []
    llm_rec_format_error_count = []
    search_nodes = []
    backtrack_count = []
    constraints_validation_count = []
    commonsense_pass_count = []
    logical_pass_count = []
    all_constraints_pass = []


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
            if "llm_rec_count" in result:
                llm_rec_count.append(result["llm_rec_count"])
            if "llm_rec_format_error_count" in result:
                llm_rec_format_error_count.append(result["llm_rec_format_error_count"])
            if "search_nodes" in result:
                search_nodes.append(result["search_nodes"])
            if "backtrack_count" in result:
                backtrack_count.append(result["backtrack_count"])
            if "constraints_validation_count" in result:
                constraints_validation_count.append(result["constraints_validation_count"])
            if "commonsense_pass_count" in result:
                commonsense_pass_count.append(result["commonsense_pass_count"])
            if "logical_pass_count" in result:
                logical_pass_count.append(result["logical_pass_count"])
            if "all_constraints_pass" in result:
                all_constraints_pass.append(result["all_constraints_pass"])

    llm_rec_format_err_ratio = np.array(llm_rec_format_error_count).reshape(-1) / np.array(llm_rec_count).reshape(-1)
    
    print("Input token count: {}".format(np.mean(input_token_count)))
    print("Output token count: {}".format(np.mean(output_token_count)))
    print("Input token maxx: {}".format(np.mean(input_token_maxx)))
    print("LLM rec count: {}".format(np.mean(llm_rec_count)))
    print("LLM rec format error count: {}".format(np.mean(llm_rec_format_error_count)))
    print("LLM rec format error rate: {}".format(np.mean(llm_rec_format_err_ratio)))
    print("Search nodes: {}".format(np.mean(search_nodes)))
    print("Backtrack count: {}".format(np.mean(backtrack_count)))
    print("Constraints validation count: {}".format(np.mean(constraints_validation_count)))
    print("Commonsense pass count: {}".format(np.mean(commonsense_pass_count)))
    print("Logical pass count: {}".format(np.mean(logical_pass_count)))
    print("All constraints pass: {}".format(np.mean(all_constraints_pass)))

            



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


# LLMNeSy_Qwen3-8B_oracletranslation
# There are 154 results...
# Input token count: 16425.79220779221
# Output token count: 26527.428571428572
# Input token maxx: 2069.4552845528456
# LLM rec count: 20.850649350649352
# LLM rec format error count: 1.7142857142857142
# LLM rec format error rate: 0.1026188887520615
# Search nodes: 14278.616883116883
# Backtrack count: 9584.253246753247
# Constraints validation count: 3.6298701298701297
# Commonsense pass count: 3.6233766233766236
# Logical pass count: 0.42857142857142855
# All constraints pass: 0.42857142857142855