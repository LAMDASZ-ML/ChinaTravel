import argparse

import numpy as np

import sys
import os
import json

project_root_path = os.path.dirname(os.path.abspath(__file__))
if project_root_path not in sys.path:
    sys.path.insert(0, project_root_path)

from copy import deepcopy

from chinatravel.data.load_datasets import load_query, save_json_file
from chinatravel.agent.load_model import init_agent, init_llm
from chinatravel.environment.world_env import WorldEnv


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="argparse testing")
    parser.add_argument(
        "--splits",
        "-s",
        type=str,
        default="easy",
        choices=["easy", "medium", "human"],
        help="query subset",
    )
    parser.add_argument("--index", "-id", type=str, default=None, help="query index")
    parser.add_argument(
        "--skip", "-sk", type=int, default=0, help="skip if the plan exists"
    )
    parser.add_argument(
        "--agent",
        "-a",
        type=str,
        default=None,
        choices=["RuleNeSy", "LLMNeSy", "ReAct", "Act"],
    )
    parser.add_argument(
        "--llm",
        "-l",
        type=str,
        default=None,
        choices=["deepseek", "deepseekv25", "gpt-4o", "glm4-plus", "qwen", "mistral", "llama"],
    )
    
    parser.add_argument('--oracle_translation', action='store_true', help='Set this flag to enable oracle translation.')
    parser.add_argument('--preference_search', action='store_true', help='Set this flag to enable preference search.')

    args = parser.parse_args()

    print(args)

    query_index, query_data = load_query(args)
    print(len(query_index), "samples")

    if args.index is not None:
        query_index = [args.index]

    cache_dir = os.path.join(project_root_path, "cache")

    method = args.agent + "_" + args.llm
    if args.oracle_translation:
        method = method + "_oracletranslation"
    if args.preference_search:
        method = method + "_preferencesearch"

    res_dir = os.path.join(
        project_root_path, "results", method
    )
    log_dir = os.path.join(
        project_root_path, "cache", method
    )
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    print("res_dir: ", res_dir)
    print("log_dir:", log_dir)

    kwargs = {
        "method": args.agent,
        "env": WorldEnv(),
        "backbone_llm": init_llm(args.llm),
        "cache_dir": cache_dir,
        "log_dir": log_dir, 
        "debug": True,
    }
    agent = init_agent(kwargs)


    white_list = []

    succ_count, eval_count = 0, 0

    for i, data_idx in enumerate(query_index):

        sys.stdout = sys.__stdout__
        print("------------------------------")
        print(
            "Process [{}/{}], Success [{}/{}]:".format(
                i, len(query_index), succ_count, eval_count
            )
        )
        print("data uid: ", data_idx)

        if args.skip and os.path.exists(os.path.join(res_dir, f"{data_idx}.json")):
            continue
        if i in white_list:
            continue
        eval_count += 1
        symbolic_input = query_data[data_idx]
        print(symbolic_input)
        if args.agent in ["ReAct", "Act"]:
            plan_log = agent(symbolic_input["nature_language"])
            plan = plan_log["ans"]
            log = plan_log["log"]
            save_json_file(
                json_data=log, file_path=os.path.join(log_dir, f"{data_idx}.json")
            )
            succ = 1
        else:
            succ, plan = agent.run(symbolic_input, load_cache=True, oralce_translation=args.oracle_translation, preference_search=args.preference_search)

        if succ:
            succ_count += 1

        save_json_file(
            json_data=plan, file_path=os.path.join(res_dir, f"{data_idx}.json")
        )
