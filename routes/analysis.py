import io
from flask import Flask, request, jsonify, Blueprint
from flask_cors import *
import pdfplumber
from services.novelty_service import *

import services.novelty_service

analysis_bp = Blueprint('analysis_bp', __name__)

@analysis_bp.route('/upload', methods=['GET', 'POST', 'OPTIONS'])
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

@analysis_bp.route('/noveltyAnalysis', methods=['GET', 'POST', 'OPTIONS'])
def signory_analysis():
    args = request.args
    signory = args.get('signory')
    response = signory_item_analysis(signory)
    return jsonify(response)
