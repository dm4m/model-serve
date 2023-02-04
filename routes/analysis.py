from flask import Flask, request, jsonify, Blueprint
from analysis.analysis_base import area, trend, author

analysis_bp = Blueprint('analysis_bp', __name__)

@analysis_bp.route('/analysis', methods=['POST'])
def pantent_analysis():
    if request.method == 'POST':
        data = request.json
        anaType = data.get('anaType')
        figType = data.get('figType')
        patentIds = data.get('patentIds')
        if anaType == 'area':
            return jsonify(area(patentIds, figType))
        elif anaType == 'trend':
            return jsonify(trend(patentIds, figType))
        elif anaType == 'author':
            return jsonify(author(patentIds, figType))