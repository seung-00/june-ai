from flask import Blueprint, request, jsonify, Response
import openai
import json
from config import OPENAI_API_KEY

bp_image = Blueprint('ai_image', __name__)

@bp_image.route('/ai/image')
def ai_generate_image():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "query 파라미터가 필요합니다."}), 400

    try:
        # OpenAI 클라이언트 설정
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # DALL-E 3로 이미지 생성
        response = client.images.generate(
            model="dall-e-3",
            prompt=query,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # 응답에서 이미지 URL 추출
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            
            return Response(json.dumps({
                "image_url": image_url,
                "prompt": query
            }, ensure_ascii=False), mimetype='application/json')
        
        return jsonify({"error": "이미지 생성에 실패했습니다."}), 500
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            "error": f"이미지 생성 중 오류가 발생했습니다: {str(e)}",
            "details": error_details
        }), 500
