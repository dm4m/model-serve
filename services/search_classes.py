import numpy as np
from models import tokenizer, model, device

def encode(query):
    # 输入：文本
    # 输出：编码向量
    # 此处设置了截断长度512
    pt_inputs = tokenizer(query,max_length=512,padding='max_length', truncation=True, return_tensors="pt").to(device)
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
    # 输入: [[[doc_id],[embedding],[signory_id]],[[],[]],[[],[]]]
    # 输出: 聚合后的文档和对应向量，格式[dict,dict]
    s = len(id_score_list)
    last_embed = []
    have_search_id = []
    # 对每个文档向量进行加权
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
                        # 优化代码，map替代for
                        embedding = list(map(lambda x,y:x*rff+y,k[1][rank-1],embedding))
                    except:
                        continue
                last_embed.append({"embedding":embedding,"doc_id":now_doc_id})
    return last_embed

def rerank(query_vec,last_embed):
    # 输入：聚合后查询向量、文档向量
    # 输入：专利id列表,list
    doc_score = {}
    for docs in last_embed:
        mul_res = [x*y for x,y in zip(query_vec,docs["embedding"])]
        doc_score[docs["doc_id"]] = sum(mul_res)
    order = sorted(doc_score.items(),key=lambda d:d[1], reverse=True)
    order_list = [i[0] for i in order]
    # 修改部分，返回值新增整篇专利的得分
    order_score_list = [i[1] for i in order]
    return order_list[0:100],order_score_list[0:100]
