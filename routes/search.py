from flask import Flask, request, jsonify, Blueprint
from transformers import RoFormerModel, RoFormerTokenizer
from pymilvus import connections
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType
import pymysql
from pymilvus import Collection
from models import tokenizer, model, device


search_bp = Blueprint('search_bp', __name__)


@search_bp.route("/neuralSearch/")
def neural_search():
    args = request.args
    query = args.get('query')
    field = args.get('field')
    if(query is  None):
        return 'no query'
    connections.connect(host='localhost', port='19530')
    if(field == "title"):
        collection = Collection("patent")  # Get an existing collection.
        collection.load()
        pt_inputs = tokenizer(query, max_length=64, padding=True, return_tensors="pt").to(device)
        # pt_inputs = tokenizer(query, max_length=505, return_tensors="pt")
        pt_outputs = model(**pt_inputs)
        query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]
        print("query vector:" + str(query_embeddings) )
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        vec_results = collection.search(query_embeddings, "title", param=search_params, limit=100, expr=None)
        idlist = list(vec_results[0].ids)
        print(idlist)
        return jsonify(idlist)
    elif field == "signoryItem":
        collection = Collection("signory")  # Get an existing collection.
        collection.load()
        pt_inputs = tokenizer(query, max_length=505, return_tensors="pt").to(device)
        pt_outputs = model(**pt_inputs)
        query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        vec_results = collection.search(query_embeddings, "signory", output_fields= ["signory_id", "patent_id"],
                                        param=search_params, limit=100, expr=None)
        idlist = []
        for result in vec_results[0]:
            if(result.entity.patent_id not in idlist):
                idlist.append(result.entity.patent_id)
        print(idlist)
        return jsonify(idlist)
    elif field == "abstract":
        collection = Collection("abstract")  # Get an existing collection.
        collection.load()
        pt_inputs = tokenizer(query, max_length=505, return_tensors="pt").to(device)
        pt_outputs = model(**pt_inputs)
        query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        vec_results = collection.search(query_embeddings, "abstract", param=search_params, limit=100, expr=None)
        idlist = list(vec_results[0].ids)
        print(idlist)
        return jsonify(idlist)
    elif field == "vector":
        pt_inputs = tokenizer(query, max_length=64, padding=True, return_tensors="pt")
        pt_outputs = model(**pt_inputs)
        query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]
        print("hello")
        return jsonify(query_embeddings)