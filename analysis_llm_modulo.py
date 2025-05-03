

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


    refine_steps = 5

    error_all = [0] * 6
    error_inc = [0] * 6
    error_ref = [0] * 6
    error_old = [0] * 6

    for method in method_list:
        print(method)
        if "deepseek" in method:
            cache_dir = os.path.join(project_root_path, "cache", method, "llm_modulo-DeepSeek-V3")
        elif "gpt-4o" in method:
            cache_dir = os.path.join(project_root_path, "cache", method, "llm_modulo-GPT4o")
        
        # print(os.listdir(os.path.join(project_root_path, 'cache', method)))
        # print(os.listdir(cache_dir))
        # exit(0)
        for query_id in query_index:


            error_previous_round = []
            for iter in range(6):
                file_name = os.path.join(cache_dir, f"problem_{query_id}_step_{iter}_error.err")
                
                # print(file_name)
                err_info_list = []
                if not os.path.exists(file_name):
                    err_info_list = []
                    # print("no file")
                else:
                    with open(os.path.join(cache_dir, file_name), "r") as f:
                        lines = f.readlines()
                        # print(lines)
                        for line_i in lines:
                            err_info_list.append(line_i.strip())
                        
                error_all[iter] += len(err_info_list)
                
                for err_i in err_info_list:
                    if err_i not in error_previous_round:
                        error_inc[iter] += 1
                    else:
                        error_old[iter] += 1
                
                for pre_err_i in error_previous_round:
                    if pre_err_i not in err_info_list:
                        error_ref[iter] += 1
                
                
                error_previous_round = err_info_list
        
        error_all = np.array(error_all) / len(query_index)
        error_ref = np.array(error_ref) / len(query_index)
        error_old = np.array(error_old) / len(query_index)
        error_inc = np.array(error_inc) / len(query_index)

        print("error count in each round: ",  error_all)
        print("error refinement count in each round: ",  error_ref)
        print("error old count in each round: ",  error_old)
        print("error increment count in each round: ",  error_inc)

            



# LLM-modulo_deepseek_5steps
# error count in each round:  [5.79220779 5.4025974  5.6038961  6.09090909 6.01298701 6.2987013 ]
# error refinement count in each round:  [0.         3.46753247 1.08441558 0.5974026  1.01298701 0.77272727]
# error old count in each round:  [0.         2.42857143 4.31818182 5.00649351 5.07792208 5.24025974]
# error increment count in each round:  [5.79220779 2.97402597 1.28571429 1.08441558 0.93506494 1.05844156]


# LLM-modulo_gpt-4o_5steps
# error count in each round:  [4.52597403 4.48701299 5.07142857 5.07142857 5.31168831 5.44805195]
# error refinement count in each round:  [0.         2.74675325 1.07142857 1.27922078 0.90909091 1.0974026 ]
# error old count in each round:  [0.         1.77922078 3.41558442 3.77922078 4.16233766 4.22727273]
# error increment count in each round:  [4.52597403 2.70779221 1.65584416 1.29220779 1.14935065 1.22077922]