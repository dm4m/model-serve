import numpy as np
from models import tokenizer, model, device

def encode(query):
    # input: text
    # output: embeddings in type IVF_SQ8
    pt_inputs = tokenizer(query, return_tensors="pt").to(device)
    pt_outputs = model(**pt_inputs)
    query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]

    # w_vec = query_embeddings / np.linalg.norm(query_embeddings)
    # w_vec = w_vec.tolist()
    # # turn to type IVF_SQ8
    # maxi = max(w_vec[0])
    # mini = min(w_vec[0])
    # length = maxi - mini
    # int8_vec = []
    # for i in w_vec[0]:
    #     temp = (i-mini)/length
    #     if temp > 1:
    #         int8_vec.append(int(1*80))
    #     elif temp < 0:
    #         int8_vec.append(int(0 * 80))
    #     else:
    #         int8_vec.append(int(temp * 80))
    return query_embeddings

def aggregate(id_score_list):
    # input: [[[doc_id],[embedding],[signory_id]],[[],[]],[[],[]]]
    # output: a dict of docs from aggregating its vectors
    s = len(id_score_list)
    last_embed = []
    have_search_id = []
    # count for all docs
    for i in id_score_list:
        # i[0]:doc_id
        for j in i[0]:
            if j not in have_search_id:
                now_doc_id = j
                have_search_id.append(now_doc_id)
                embedding = [0 for i in range(0,768)]
                for k in id_score_list:
                    try:
                        rank = k[0].index(now_doc_id)+1
                        rff = 1.0/(60 + rank)
                        weight_tensor = [i*rff for i in k[1][rank-1]]
                        embedding = [embedding[i]+weight_tensor[i] for i in range(0,len(embedding))]
                    except:
                        continue
                last_embed.append({"embedding":embedding,"doc_id":now_doc_id})
    return last_embed

def rerank(query_vec,last_embed):
    # input: the last query vector and the last docs vectors
    # output:id_list
    doc_score = {}
    for docs in last_embed:
        temp_score = 0
        mul_res = [query_vec[i]*docs['embedding'][i] for i in range(0,len(query_vec))]
        temp_score = sum(mul_res)
        doc_score[docs['doc_id']] = temp_score
    order = sorted(doc_score.items(),key=lambda d:d[1], reverse=True)
    order_list = []
    for i in order:
        order_list.append(i[0])
    return order_list