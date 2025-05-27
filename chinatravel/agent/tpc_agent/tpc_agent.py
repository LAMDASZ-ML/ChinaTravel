import sys
import os
import time
import argparse
import pandas as pd
import json
import numpy as np

sys.path.append("./../../../")
project_root_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

if project_root_path not in sys.path:
    sys.path.insert(0, project_root_path)


from agent.base import AbstractAgent, BaseAgent

class TPCAgent(BaseAgent):
    # def __init__(
    #     self,
    #     env,
    #     backbone_llm,
    #     method="NeSy",
    #     cache_dir="cache/",
    #     max_time=None,
    #     debug=True,
    #     search_width=None,
    # ):

    def __init__(self, **kwargs):
        super().__init__(name="TPC", **kwargs)
    
    def run(self, query, prob_idx, oralce_translation=False):


        self.reset_clock()

        result = {
            "itinerary": [], 
            "elapsed_time(sec)": time.time() - self.start_clock, 
            }
        
        return result