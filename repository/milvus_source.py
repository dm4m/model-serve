from pymilvus import connections, Collection
from models import tokenizer, model, device

def get_relevant_vec_results(collection_name, field, query, limit = 100, output_list = []):
    connections.connect(alias="default", host='localhost', port='19530')
    collection = Collection(collection_name)  # Get an existing collection.
    collection.load()
    pt_inputs = tokenizer(query, return_tensors="pt", max_length=510, truncation=True).to(device)
    pt_outputs = model(**pt_inputs)
    query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]
    print("query vector:" + str(query_embeddings))
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    vec_results = collection.search(query_embeddings, field, output_fields=output_list, param=search_params, limit=limit,
                                    expr=None)
    connections.disconnect("default")
    return vec_results

def get_relevant_id_list(collection_name, field, query, limit = 100):
    vec_results = get_relevant_vec_results(collection_name, field, query, limit=limit)
    id_list = list(vec_results[0].ids)
    return id_list

def get_relevant_all_field_results(collection_name, field, schema, query_embeddings, limit = 100, output_list = []):
    ids= []
    primary_id = []
    embed = []
    
    connections.connect(alias="default", host='localhost', port='19530')
    collection = Collection(name=collection_name, schema=schema, using='default')
    collection.load()
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(query_embeddings, field, output_fields=output_list, param=search_params, limit=limit,
                                    expr=None)

    for hits in results:
        for hit in hits:
            ids.append(hit.entity.get('patent_id'))
            primary_id.append(hit.entity.get('signory_id'))
    for i in range(0,len(primary_id)):
        res2 = collection.query(expr = "signory_id in ["+str(primary_id[i])+"]", onsistency_level="Strong", output_fields=["signory"])
        embed.append(res2[0]["signory"])
    connections.disconnect("default")
    return ids,embed,primary_id
