from flask import Flask, request, jsonify, Blueprint
from analysis.analysis_base import analyze_by_list, pdf_output
import base64

analysis_bp = Blueprint('analysis_bp', __name__)

@analysis_bp.route('/analysis', methods=['POST'])
def patent_analysis():
    if request.method == 'POST':
        data = request.json
        anaType = data.get('anaType')
        figType = data.get('figType')
        patentIds = data.get('patentIds')
        return jsonify(analyze_by_list(patentIds, figType, anaType))
    else:
        return "success"

@analysis_bp.route('/reportGen', methods=['POST'])
def report_generate():
    if request.method == 'POST':
        data = request.json
        reportId = data.get('reportId')
        pdf_output(reportId)
        return "success"
    else:
        return "success"

@analysis_bp.route('/reportFile', methods=['GET'])
def get_report_file():
    args = request.args
    pdfFilePath = args.get('pdfFilePath')
    with open(pdfFilePath, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
    return encoded_string