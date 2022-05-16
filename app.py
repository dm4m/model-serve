from flask import Flask, request, jsonify
from transformers import RoFormerModel, RoFormerTokenizer
from pymilvus import connections
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType
import pymysql
from pymilvus import Collection

app = Flask(__name__)

model = RoFormerModel.from_pretrained("junnyu/roformer_chinese_sim_char_ft_base")
tokenizer = RoFormerTokenizer.from_pretrained("junnyu/roformer_chinese_sim_char_ft_base")
use_gpu = True

def load_model():
    """Load the pre-trained model, you can use your model just as easily
    """
    global model
    global tokenizer
    model = RoFormerModel.from_pretrained("junnyu/roformer_chinese_sim_char_ft_base")
    tokenizer = RoFormerTokenizer.from_pretrained("junnyu/roformer_chinese_sim_char_ft_base")

    if use_gpu:
        model.cuda()

# @app.route('/')
# def hello_world():  # put application's code here
#     return 'Hello World!'

@app.route("/")
def predict():
    args = request.args
    query = args.get('query')
    field = args.get('field')
    if(query is  None):
        return 'no query'
    connections.connect(host='localhost', port='19530')
    if(field == "title"):
        collection = Collection("patent")  # Get an existing collection.
        collection.load()
        pt_inputs = tokenizer(query, max_length=64, padding=True, return_tensors="pt")
        pt_outputs = model(**pt_inputs)
        query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        vec_results = collection.search(query_embeddings, "title", param=search_params, limit=100, expr=None)
        idlist = list(vec_results[0].ids)
        return jsonify(idlist)
    elif field == "signory_item":
        collection = Collection("signory")  # Get an existing collection.
        collection.load()
        pt_inputs = tokenizer(query, max_length=64, padding=True, return_tensors="pt")
        pt_outputs = model(**pt_inputs)
        query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        vec_results = collection.search(query_embeddings, "signory", output_fields= ["signory_id", "patent_id"],
                                        param=search_params, limit=100, expr=None)
        idlist = []
        for result in vec_results[0]:
            if(result.entity.patent_id not in idlist):
                idlist.append(result.entity.patent_id)
        return jsonify(idlist)
    elif field == "vector":
        pt_inputs = tokenizer(query, max_length=64, padding=True, return_tensors="pt")
        pt_outputs = model(**pt_inputs)
        query_embeddings = [pt_outputs["last_hidden_state"][0][0].tolist()]
        print("hello")
        return jsonify(query_embeddings)

if __name__ == '__main__':
    # load_model()
    app.run(host='0.0.0.0', port='5000')
