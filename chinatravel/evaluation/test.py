import argparse
import os
import sys
import json


project_root_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if project_root_path not in sys.path:
    sys.path.insert(0, project_root_path)
if os.path.join(project_root_path, "chinatravel") not in sys.path:
    sys.path.insert(0, os.path.join(project_root_path, "chinatravel"))

from chinatravel.evaluation.utils import load_json_file, validate_json

from chinatravel.evaluation.commonsense_constraint import evaluate_commonsense_constraints
from chinatravel.evaluation.hard_constraint import evaluate_hard_constraints
from chinatravel.evaluation.preference import evaluate_preference

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
                "../results/", method, "{}.json".format(query_id)
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
    parser.add_argument("--preference", "-p", action="store_true", default=False)
    args = parser.parse_args()

    # print(args.splits)

    query_index, query_data = load_query(args)

    method_list, result_data = load_result(args, query_index)

    # print(query_data.keys())
    # print(result_data.keys())

    if not os.path.exists("eval_res/splits_{}/".format(args.splits)):
        os.makedirs("eval_res/splits_{}/".format(args.splits))

    for method in method_list:

        if not os.path.exists("eval_res/splits_{}/{}/".format(args.splits, method)):
            os.makedirs("eval_res/splits_{}/{}/".format(args.splits, method))

        macro_comm, micro_comm, result_agg = evaluate_commonsense_constraints(
            query_index, query_data, result_data[method], verbose=False
        )

        res_file = "eval_res/splits_{}/{}/commonsense.csv".format(args.splits, method)
        result_agg.to_csv(res_file, index=False)
        print("save to {}".format(res_file))

        print("Method: {}".format(method))
        print("Commonsense constraints:")
        print("micro accuracy: {}".format(micro_comm))
        print("macro accuracy: {}".format(macro_comm))

        # record the index of the queries that pass the commonsense constraints
        commonsense_pass_info = result_agg.iloc[:, 1:]
        id_list = result_agg.iloc[:, 0].tolist()
        commonsense_pass = [
            id_list[i]
            for i in range(len(id_list))
            if commonsense_pass_info.iloc[i].sum() == 0
        ]
        # record end

        print("Logical constraints:")
        macro_logi, micro_logi, result_agg = evaluate_hard_constraints(
            query_index, query_data, result_data[method], verbose=False
        )

        print("micro accuracy: {}".format(micro_logi))
        print("macro accuracy: {}".format(macro_logi))

        res_file = "eval_res/splits_{}/{}/logical.csv".format(args.splits, method)
        result_agg.to_csv(res_file, index=False)
        print("save to {}".format(res_file))
        if args.preference:
            print("Preference:")
            result_agg = evaluate_preference(
                query_index,
                query_data,
                result_data[method],
                commonsense_pass,
            )

            res_file = "eval_res/splits_{}/{}/preference.csv".format(
                args.splits, method
            )
            result_agg.to_csv(res_file, index=False)
            print("save to {}".format(res_file))
