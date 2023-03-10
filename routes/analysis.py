from flask import Flask, request, jsonify, Blueprint
from analysis.analysis_base import analyze_by_list, pdf_output

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