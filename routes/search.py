from flask import Flask, request, jsonify, Blueprint
from services.search_service import patent_neural_search

search_bp = Blueprint('search_bp', __name__)


@search_bp.route("/neuralSearch/")
def neural_search():
    args = request.args
    query = args.get('query')
    field = args.get('field')
    if(query is  None):
        return 'no query'
    res = patent_neural_search(field, query)
    return res