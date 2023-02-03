from flask import Flask, request, jsonify, Blueprint
from analysis.analysis_base import area

analysis_bp = Blueprint('analysis_bp', __name__)

@analysis_bp.route('/analysis', methods=['POST', 'OPTIONS'])
def pantent_extract():
    data = request.json
    anaType = data.get('anaType')
    anaType = data.get('anaType')
    patentIds = data.get('patentIds')
    return area([1,4,2,6,34,213,90])[0]