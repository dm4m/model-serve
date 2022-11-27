import io
from flask import Flask, request, jsonify, Blueprint
from flask_cors import *
import pdfplumber
from services.analysis_service import *

import services.analysis_service

analysis_bp = Blueprint('analysis_bp', __name__)

@analysis_bp.route('/upload', methods=['GET', 'POST', 'OPTIONS'])
def pantent_analysis():
    if request.method == 'POST':
        files = request.files
        if len(files) == 0:
            return 'file uploaded false'
        elif len(files) == 1:
            file = files.get("file")
            pdf_bytes = file.read()
            pdf = pdfplumber.open(io.BytesIO(pdf_bytes))
            novelty_analysis(pdf)
            return 'file uploaded successfully'
    else:
        return 'file uploaded false'