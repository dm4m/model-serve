from pymilvus import connections, Collection
from models import tokenizer, model, device


def get_relevant_vec_results(collection_name, field, query, limit=100, output_list=[]):
    connections.connect(alias="default", host='localhost', port='19530')
    collection = Collection(collection_name)  # Get an existing collection.
    collection.load()
    pt_inputs = tokenizer(query, return_tensors="pt").to(device)
    pt_outputs = model(**pt_inputs)
    query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]
    print("query vector:" + str(query_embeddings))
    # search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    # 以下查询参数均为HNSW准备，ef取值为top k到3w多
    search_params_HNSW = {"metric_type": "L2", "params": {"ef": 128}}
    vec_results = collection.search(query_embeddings, field, output_fields=output_list, param=search_params_HNSW,
                                    limit=limit,
                                    expr=None)
    connections.disconnect("default")
    return vec_results


def get_relevant_id_list(collection_name, field, query, limit=100):
    vec_results = get_relevant_vec_results(collection_name, field, query, limit=limit)
    id_list = list(vec_results[0].ids)
    return id_list


def get_relevant_all_field_results(collection_name, field, schema, query_embeddings, limit=100, output_list=[]):
    ids = []
    primary_id = []
    embed = []
    connections.connect(alias="default", host='localhost', port='19530')
    collection = Collection(name=collection_name, schema=schema, using='default')
    collection.load()
    # 非HNSW检索方式使用以下参数集合
    search_params = {"metric_type": "L2", "params": {"nprobe": 100}}
    # 以下查询参数均为HNSW准备，ef取值为top k-3w多
    search_params_HNSW = {"metric_type": "L2", "params": {"ef": 128}}
    results = collection.search(query_embeddings, field, output_fields=output_list, param=search_params_HNSW,
                                limit=limit,
                                expr=None)
    for hits in results:
        for hit in hits:
            ids.append(hit.entity.get('patent_id'))
            primary_id.append(hit.entity.get('signory_id'))
    # 优化向量查询
    res2 = collection.query(expr="signory_id in " + str(primary_id) + "", onsistency_level="Strong",
                            output_fields=["signory"])
    embed = list(map(lambda x: x["signory"], res2))
    connections.disconnect("default")
    return ids, embed, primary_id

def get_relevant_id_similarity(collection_name, field, query, limit=100):
    vec_results = get_relevant_vec_results(collection_name, field, query, limit=limit)
    id_list = list(vec_results[0].ids)
    id_score = list(vec_results[0].distances)
    return id_list,id_score
