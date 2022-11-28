from flask import jsonify
from repository.milvus_source import get_relevant_id_list, get_relevant_vec_results

def patent_neural_search(field, query):
    if field == 'title' :
        id_list = get_relevant_id_list("patent", "title", query)
        return jsonify(id_list)
    elif field == 'abstract':
        id_list = get_relevant_id_list("abstract", "abstract", query)
        return jsonify(id_list)
    elif field == 'signoryItem':
        sig_id_list = []
        vec_results = get_relevant_vec_results("signory", "signory", query, ["signory_id", "patent_id"])
        for result in vec_results[0]:
            if (result.entity.patent_id not in sig_id_list):
                sig_id_list.append(result.entity.patent_id)
        return jsonify(sig_id_list)