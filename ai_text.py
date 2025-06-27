from flask import Blueprint, request, jsonify, Response
import google.generativeai as genai
import json
from config import GEMINI_API_KEY
import os

# 환경변수로 API 키 설정
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)

bp_text = Blueprint('ai_text', __name__)

@bp_text.route('/ai/text')
def ai_generate_text():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "query 파라미터가 필요합니다."}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(query)
        message = response.text
        return Response(json.dumps({"message": message}, ensure_ascii=False), mimetype='application/json')
    
    except Exception as e:
        return jsonify({"error": f"API 호출 중 오류가 발생했습니다: {str(e)}"}), 500

