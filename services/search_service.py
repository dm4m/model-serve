import torch
from flask import jsonify
from pymilvus import CollectionSchema, FieldSchema,DataType
import torch
import numpy as np
from repository.milvus_source import get_relevant_id_list, get_relevant_vec_results,get_relevant_all_field_results
from services.search_classes import aggregate,rerank,encode

def patent_neural_search(field, query,schema=None):
    if field == 'title' :
        id_list = get_relevant_id_list("patent", "title", query)
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
        signory_id = FieldSchema(name="signory_id", dtype=DataType.INT64, is_primary=True,auto_id=False,description="")
        patent_id = FieldSchema(name="patent_id", dtype=DataType.INT64,description="")
        signory = FieldSchema(name="signory", dtype=DataType.FLOAT_VECTOR,dim=768,description="")
        schema = CollectionSchema(fields=[signory_id, patent_id, signory],auto_id=False,description="signory_seg of patent,HNSW")
        query_embeddings = encode(query)
        id_list,embed_list,sig_id_list = get_relevant_all_field_results("signory_HNSW", "signory", schema, query_embeddings, limit = 100, output_list = ["signory_id","patent_id"])
        return_list = []
        return_list.append(id_list)
        return_list.append(embed_list)
        return_list.append(sig_id_list)
        return return_list


def search_by_patent(signory_list):
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
        all_field_list = patent_neural_search("allField", signory_list[i],schema)
        rawrank.append(all_field_list)
        all_embed.append(now_embedding[0])
    # 向量加权操作
    last_query_embedding = torch.tensor([0.0 for i in range(0, 768)])
    temp_sig = np.add.reduce(all_embed[1:])
    last_query_embedding = first_signory_weight*torch.tensor(all_embed[0])+other_signory_weight*torch.tensor(temp_sig)
    last_other_embedding = aggregate(rawrank)
    rerank_list = rerank(last_query_embedding,last_other_embedding)
    return jsonify(rerank_list)