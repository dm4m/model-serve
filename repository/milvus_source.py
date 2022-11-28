from pymilvus import connections, Collection
from models import tokenizer, model, device

def get_relevant_vec_results(collection_name, field, query, output_list = []):
    connections.connect(alias="default", host='localhost', port='19530')
    collection = Collection(collection_name)  # Get an existing collection.
    collection.load()
    pt_inputs = tokenizer(query, return_tensors="pt").to(device)
    pt_outputs = model(**pt_inputs)
    query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]
    print("query vector:" + str(query_embeddings))
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    vec_results = collection.search(query_embeddings, field, output_fields=output_list, param=search_params, limit=100,
                                    expr=None)
    connections.disconnect("default")
    return vec_results

def get_relevant_id_list(collection_name, field, query):
    vec_results = get_relevant_vec_results(collection_name, field, query, [])
    id_list = list(vec_results[0].ids)
    return id_list
