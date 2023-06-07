import torch
from flask import jsonify
from pymilvus import CollectionSchema, FieldSchema,DataType
import torch
import numpy as np
from repository.milvus_source import get_relevant_id_list, get_relevant_vec_results,get_relevant_all_field_results
from repository.mysql_source import get_sig_by_id
from services.search_classes import aggregate,rerank,encode

def patent_neural_search(field, query, limit, schema=None):
    if field == 'title' :
        id_list = get_relevant_id_list("title", "title", query)
        return jsonify(id_list)
    elif field == 'abstract':
        id_list = get_relevant_id_list("abstract", "abstract", query)
        return jsonify(id_list)
    elif field == 'signoryItem':
        sig_id_list = []
        vec_results = get_relevant_vec_results("signory", "signory", query, output_list = ["signory_id", "patent_id"])
        for result in vec_results[0]:
            if result.entity.patent_id not in sig_id_list:
                sig_id_list.append(result.entity.patent_id)
        return jsonify(sig_id_list)
    elif field == 'allField':
        # 返回id和向量
        sig_id_list = []
        id_list = []
        embed_list = []
        # signory_id = FieldSchema(name="signory_id", dtype=DataType.INT64, is_primary=True,auto_id=False,description="")
        # patent_id = FieldSchema(name="patent_id", dtype=DataType.INT64,description="")
        # signory = FieldSchema(name="signory", dtype=DataType.FLOAT_VECTOR,dim=768,description="")
        # schema = CollectionSchema(fields=[signory_id, patent_id, signory],auto_id=False,description="signory_seg of patent,HNSW")
        query_embeddings = encode(query)
        id_list,embed_list,sig_id_list = get_relevant_all_field_results("signory", "signory", schema, query_embeddings, limit = limit, output_list = ["signory_id","patent_id"],out_type="sig")
        return_list = []
        return_list.append(id_list)
        return_list.append(embed_list)
        return_list.append(sig_id_list)
        return return_list
    elif field == "titleField":
        id_list = []
        title_e_list = []
        query_embeddings = encode(query)
        id_list, title_e_list = get_relevant_all_field_results("title", "title", schema,
                                                                          query_embeddings, limit=limit,
                                                                          output_list=["id"],out_type="title")
        return_list = []
        return_list.append(id_list)
        return_list.append(title_e_list)
        return_list.append(id_list)
        return return_list

def search_by_patent(signory_list, limit):
    first_signory_weight = 0.6
    other_signory_weight = 0.3
    # schema约束
    signory_id = FieldSchema(name="signory_id", dtype=DataType.INT64, is_primary=True, auto_id=False, description="")
    patent_id = FieldSchema(name="patent_id", dtype=DataType.INT64, description="")
    signory = FieldSchema(name="signory", dtype=DataType.FLOAT_VECTOR, dim=768, description="")
    schema = CollectionSchema(fields=[signory_id, patent_id, signory], auto_id=False,
                              description="signory_seg of patent,HNSW")
    #主权项分项操作
    rawrank = []
    all_embed = []
    for i in range(0,len(signory_list)):
        now_embedding = encode(signory_list[i])
        all_field_list = patent_neural_search("allField", signory_list[i], limit, schema)
        rawrank.append(all_field_list)
        all_embed.append(now_embedding[0])
    # 向量加权操作
    last_query_embedding = torch.tensor([0.0 for i in range(0, 768)])
    temp_sig = np.add.reduce(all_embed[1:])
    last_query_embedding = first_signory_weight*torch.tensor(all_embed[0])+other_signory_weight*torch.tensor(temp_sig)
    last_other_embedding = aggregate(rawrank)
    # 增加返回值分数，该分数为rrf算法得到的聚合向量的分数，值越大越相似，没有区间限制
    rerank_list,rerank_score = rerank(last_query_embedding,last_other_embedding,limit =limit)
    return rerank_list,rerank_score

def search_by_title_sig(title,signory_list,search_type):
    # search_type = “first_sig”(就是标题+主权项),其他的就是(标题+所有权利要求)
    first_signory_weight = 0.6
    other_signory_weight = 0.3
    title_weight = 1
    # 写支持title的方式
    all_embed = []
    t_embedding = encode(title)
    all_embed.append(t_embedding[0])

    id_ = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False)
    title_ = FieldSchema(name="title", dtype=DataType.FLOAT_VECTOR, dim=768)
    schema = CollectionSchema(fields=[id_, title_], description="title of patent,HNSW")
    t_list= patent_neural_search("titleField", title,schema)
    rawrank = []
    # title:[id,embedding]
    rawrank.append(t_list)

    signory_id = FieldSchema(name="signory_id", dtype=DataType.INT64, is_primary=True, auto_id=False, description="")
    patent_id = FieldSchema(name="patent_id", dtype=DataType.INT64, description="")
    signory = FieldSchema(name="signory", dtype=DataType.FLOAT_VECTOR, dim=768, description="")
    schema = CollectionSchema(fields=[signory_id, patent_id, signory], auto_id=False,
                              description="signory_seg of patent,HNSW")
    for i in range(0, len(signory_list)):
        # print("1")
        now_embedding = encode(signory_list[i])
        all_field_list = patent_neural_search("allField", signory_list[i], schema)
        rawrank.append(all_field_list)
        all_embed.append(now_embedding[0])
        if search_type == "first_sig":
            break
    last_query_embedding = torch.tensor([0.0 for i in range(0, 768)])
    temp_sig = np.add.reduce(all_embed[2:])
    last_query_embedding = title_weight * torch.tensor(all_embed[0]) + first_signory_weight * torch.tensor(all_embed[1]) + other_signory_weight * torch.tensor(
        temp_sig)
    last_other_embedding = aggregate(rawrank)
    # 增加返回值分数，该分数为rrf算法得到的聚合向量的分数，值越大越相似，没有区间限制
    rerank_list, rerank_score = rerank(last_query_embedding, last_other_embedding)
    return rerank_list,rerank_score


def get_compare_sig_by_patents(signory_item, patent_ids):
    # signory_item : string
    # patentids: [int, ...]
    # return 有序对象列表[dict,dict],dict:{"patent_id":int,"signory_id":int,"signory_seg":string,"score":float}
    query_embedding = encode(signory_item)
    signory_id = FieldSchema(name="signory_id", dtype=DataType.INT64, is_primary=True, auto_id=False, description="")
    patent_id = FieldSchema(name="patent_id", dtype=DataType.INT64, description="")
    signory = FieldSchema(name="signory", dtype=DataType.FLOAT_VECTOR, dim=768, description="")
    schema = CollectionSchema(fields=[signory_id, patent_id, signory], auto_id=False,
                              description="signory_seg of patent,HNSW")
    # milvus检索相关权利要求
    res = get_relevant_all_field_results("signory", "signory", schema, query_embeddings=None, limit=100, output_list=[],
                                   out_type="novelty_patent_sig", patent_idlist=patent_ids)
    # res:list dict_keys(['signory_id', 'patent_id', 'signory'])
    res_dic = {}
    for dic in res:
        score = sum([x*y for x,y in zip(query_embedding[0],dic["signory"])])
        l1 = np.sqrt(sum([x*x for x in query_embedding[0]]))
        l2 = np.sqrt(sum([x * x for x in dic["signory"]]))
        res_dic[dic["signory_id"]] = score/(l1*l2)
    order = sorted(res_dic.items(), key=lambda d: d[1], reverse=True)
    # 找截断位置,阈值在这里设置
    pos = 0
    for i in order:
        if i[1] < 0.7:
            break
        else:
            pos += 1
    order_list_sig = [i[0] for i in order[0:pos]]
    print(order[0:pos])
    # 获得权利要求文本
    sig_infos = get_sig_by_id(order_list_sig)
    new_sig_info = {}
    for i in sig_infos:
        new_sig_info[i["signory_id"]] = [i["patent_id"],i["signory_seg"]]
    sig_text_list = []
    for i in range(len(order_list_sig)):
        temp_dic = {"patent_id":new_sig_info[order_list_sig[i]][0],"signory_id":order_list_sig[i],"signory_seg":new_sig_info[order_list_sig[i]][1],"score":order[i][1]}
        sig_text_list.append(temp_dic)
    return sig_text_list