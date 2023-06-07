import io
from flask import Flask, request, jsonify, Blueprint
from flask_cors import *
import pdfplumber
from services.novelty_service import *

import services.novelty_service

novelty_bp = Blueprint('novelty_bp', __name__)

@novelty_bp.route('/upload', methods=['GET', 'POST', 'OPTIONS'])
def pantent_extract():
    if request.method == 'POST':
        files = request.files
        if len(files) == 0:
            return 'file uploaded false'
        elif len(files) == 1:
            file = files.get("file")
            pdf_bytes = file.read()
            pdf = pdfplumber.open(io.BytesIO(pdf_bytes))
            signory_list = get_signory_list_by_pdf_file(pdf)
            response = {"signory_list": signory_list}
            return response
    else:
        return 'file uploaded false'

@novelty_bp.route('/noveltyAnalysis', methods=['GET', 'POST', 'OPTIONS'])
def signory_analysis():
    if request.method == 'POST':
        data = request.json
        signory = data.get('signory')
        patentIds = data.get('patentIds')
        response = signory_item_analysis(signory, patentIds)
        return jsonify(response)
    else:
        return "success"


@novelty_bp.route('/noveltyCompare', methods=['GET', 'POST', 'OPTIONS'])
def novelty_compare():
    if request.method == 'POST':
        data = request.json
        oriSig = data.get('oriSig')
        compareSigs = data.get('compareSigs')
        response = signory_item_analysis_with_compare_items(oriSig, compareSigs)
        return jsonify(response)
    else:
        return "success"
