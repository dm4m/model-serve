import sys
import os
from repository.milvus_source import get_relevant_id_similarity


def signory_creativity(query, threshold):
    sig_id, sig_simliar = get_relevant_id_similarity("signory", "signory", query=query)
    # 如果相似的第一个向量相似性大于threhold，就不具有相似性
    if 1 / sig_simliar[0] > threshold:
        string = "该主权项接近于现有技术，可能不具有创造性。"
        sig_id = sig_id[0]
        sig_sim_score = 1 - sig_simliar[0]
        return string, [sig_id, sig_sim_score]
    else:
        string = "该主权项可能具有创造性。"
        return string,[]
