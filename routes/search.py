from flask import Flask, request, jsonify, Blueprint
from services.search_service import *
from services.novelty_service import *
import pdfplumber
import io

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
@search_bp.route("/uploadSearch", methods=['GET', 'POST', 'OPTIONS'])
def upload_search():
    if request.method == 'POST':
        files = request.files
        if len(files) == 0:
            return 'file uploaded false'
        elif len(files) == 1:
            file = files.get("file")
            pdf_bytes = file.read()
            pdf = pdfplumber.open(io.BytesIO(pdf_bytes))
            signory_list = get_signory_list_by_pdf_file(pdf)
            response = search_by_patent(signory_list)
            return response
    else:
        return 'file uploaded false'