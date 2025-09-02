import numpy as np
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TimeOutError(Exception):
    def __init__(self, message="Searching TIME OUT !!!"):
        self.message = message
        super().__init__(self.message)

def time_to_minutes(tstr: str) -> int:
    """'HH:MM' -> 分钟"""
    h, m = map(int, tstr.split(":"))
    return h * 60 + m

def minutes_to_time(minutes: int) -> str:
    """分钟 -> 'HH:MM'"""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def time_compare_if_earlier_equal(time_1, time_2):
    time1 = float(time_1.split(":")[0]) * 60 + float(time_1.split(":")[1])
    time2 = float(time_2.split(":")[0]) * 60 + float(time_2.split(":")[1])

    return time1 <= time2


def add_time_delta(time1, time_delta):
    hour, minu = int(time1.split(":")[0]), int(time1.split(":")[1])

    min_new = minu + time_delta

    if min_new >= 60:
        hour_new = hour + int(min_new / 60)
        min_new = min_new % 60
    else:
        hour_new = hour

    if hour_new < 10:
        time_new = "0" + str(hour_new) + ":"
    else:
        time_new = str(hour_new) + ":"
    if min_new < 10:

        time_new = time_new + "0" + str(min_new)
    else:
        time_new = time_new + str(min_new)

    return time_new

def get_time_delta(time1, time2):
    """
    计算 time1 和 time2 的时间差（分钟数）
    假设 time1 早于 time2，格式为 HH:MM
    """
    hour1, min1 = int(time1.split(":")[0]), int(time1.split(":")[1])
    hour2, min2 = int(time2.split(":")[0]), int(time2.split(":")[1])

    delta_minutes = (hour2 - hour1) * 60 + (min2 - min1)
    return delta_minutes


def calc_cost_from_itinerary_wo_intercity(itinerary, people_number):
    total_cost = 0
    for day in itinerary:
        for activity in day["activities"]:

            for transport in activity.get("transports", []):

                mode = transport["mode"]
                if mode == 'taxi':
                    if 'cars' in transport.keys():
                        total_cost += transport.get('cars', 0) * transport.get("cost", 0)
                    else:
                        total_cost += transport.get('tickets', 0) * transport.get("cost", 0)
                if mode == 'metro':
                    total_cost += transport.get('tickets', 0) * transport.get("cost", 0)

            # if activity["type"] == "airplane":
            #     total_cost += activity.get('tickets',0)*activity.get("cost", 0)

            # if activity["type"] == "train":
            #     total_cost += activity.get('tickets',0)*activity.get("cost", 0)

            if activity["type"] == "breakfest" or activity["type"] == "lunch" or activity["type"] == "dinner":
                total_cost += activity.get('cost', 0) * people_number

            # if activity["type"] == "accommodation":
            #     total_cost += activity.get('rooms',0)*activity.get("cost", 0)

            if activity["type"] == "attraction":
                total_cost += activity.get('tickets', 0) * activity.get("cost", 0)
    return total_cost


def mmr_algorithm(name_list, score, lambda_value=0.3):
    selected_indices = []
    remaining_indices = list(range(len(name_list)))

    tfidf_vectorizer = TfidfVectorizer()

    while len(selected_indices) < len(name_list):
        if len(selected_indices) == 0:
            mmr_scores = np.ones(len(name_list))
        else:
            selected_names = [name.split()[0] for name in name_list[selected_indices]]
            remaining_names = [name.split()[0] for name in name_list[remaining_indices]]

            tfidf_matrix = tfidf_vectorizer.fit_transform(np.concatenate((selected_names, remaining_names)))
            similarity_matrix = cosine_similarity(tfidf_matrix)

            selected_similarities = similarity_matrix[:len(selected_names), len(selected_names):]
            remaining_similarities = similarity_matrix[len(selected_names):, len(selected_names):]

            mmr_scores = lambda_value * score[remaining_indices] - (1 - lambda_value) * np.max(selected_similarities,
                                                                                               axis=0)

        max_index = np.argmax(mmr_scores)
        selected_indices.append(remaining_indices[max_index])
        del remaining_indices[max_index]

    return mmr_scores