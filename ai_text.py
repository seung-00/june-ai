from flask import Blueprint, request, jsonify, Response
import google.generativeai as genai
import json
from config import GEMINI_API_KEY
import os
import re
import ast

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

        print("ai_generate_text response is: ", response)

        message = response.text
        return Response(json.dumps({"message": message}, ensure_ascii=False), mimetype='application/json')
    
    except Exception as e:
        return jsonify({"error": f"API 호출 중 오류가 발생했습니다: {str(e)}"}), 500


@bp_text.route('/ai/question')
def ai_generate_question():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "query 파라미터가 필요합니다."}), 400

    prompt = f"""
    너는 행사 전문가야. 유저 아이디어 바탕으로 추가 질문을 3개 이하로 만들어야 해.
    * 아래를 반드시 지켜야 함
    1. 유저 친화적으로 단순하고 일반적인 질문을 한다.
    2. 질문이 길어지지 않는다.
    3. 유저가 왜 이런 아이디어를 냈는지 추측할 수 있는 질문을 해서 수요를 예측한다.
    4. 반드시 아래 형식으로 응답해줘:
    ["질문1", "질문2", "질문3"]

    아래는 예시야.
    input: 마라톤 행사 있었으면 좋겠어
    output: ["왜 마라톤을 하고 싶나요?", "주변에 마라톤을 하고 싶어하는 사람들이 많을 것 같나요?", "동네 사람들이 많이 좋아할 것 같나요?"]
    
    ----------------------------
    """

    prompt += f"input: {query}\noutput:"

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
    
        print("ai_generate_question ai response is: ", response)

        # 응답 텍스트 정리
        response_text = response.text.strip()

        items = extract_list(response_text)

        if items:
            return jsonify({"questions": items})
        else:
            # 모든 시도가 실패한 경우 빈 리스트 반환
            return jsonify({"questions": []})         
    
    except Exception as e:
        return jsonify({"error": f"API 호출 중 오류가 발생했습니다: {str(e)}"}), 500


@bp_text.route('/ai/draft')
def ai_generate_draft():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "query 파라미터가 필요합니다."}), 400

    prompt = """
    너는 행사 펀딩 전문가야. 주어진 유저의 응답을 바탕으로 펀딩 소개 초안을 만들어줘.
    * 아래를 반드시 지켜야 함
    1. 유저 친화적이고 단순하게 작성한다.
    2. 글자수는 400자를 넘지 않는다.
    3. 반드시 아래 형식으로 응답해줘:
    "title": "제목"
    "content": "내용"

    아래는 예시야.
    input:
    무엇을 함께 만들어볼까요?
    - 우리 동네에서도 철인 삼종경기를 했으면 좋겠어요.
    동네 사람들이 많이 좋아할 것 같나요?
    - 요즘 건강에 관심 많은 분들이 많고, 가족 단위로 참여하거나 응원하는 재미도 클 것 같아요.
    왜 마라톤을 하고 싶나요?
    - 운동을 좋아하고, 지역 사람들과 땀 흘리며 소통할 기회를 만들고 싶어요.
    주변에 마라톤을 하고 싶어하는 사람들이 많을 것 같나요?
    - 평소 조깅하는 사람들도 많고, 자전거 타는 분들도 종종 보여요.

    타겟:

    output:
    "title": "우리 동네 철인삼종 챌린지 – 같이 만들어봐요!"
    "content": "우리 동네에서도 철인삼종경기를 함께 열어보면 어떨까요?\n\n달리기, 자전거, 파워워킹으로 구성된 부담 없는 코스에, 건강을 즐기는 청년부터 가족 단위 참가자까지 누구나 어울릴 수 있어요.\n\n요즘 운동하는 이웃들 많잖아요! 함께 땀 흘리고 응원하면서 동네에 활력을 불어넣어요.\n\n참가자 기념품, 응원 이벤트 등도 준비해볼 수 있어요.\n\n이웃들과 함께 기획하고 만들어가는 마을 축제, 지금 펀딩으로 첫 발을 내디뎌보세요!"
    ----------------------------
    input:
    """

    prompt += f"input: {query}\noutput:"

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
    
        print("ai_generate_draft ai response is: ", response)

        # 응답 텍스트 정리
        response_text = response.text.strip()

        print("ai_generate_draft response_text is: ", response_text)

        # title과 content 파싱
        title = ""
        content = ""
        
        # 정규표현식으로 title과 content 추출
        title_match = re.search(r'"title":\s*"([^"]*)"', response_text)
        content_match = re.search(r'"content":\s*"([^"]*)"', response_text, re.DOTALL)
        
        if title_match:
            title = title_match.group(1)
        
        if content_match:
            content = content_match.group(1)
            # \n을 실제 줄바꿈으로 변환
            content = content.replace('\\n', '\n')
        
        # 파싱이 실패한 경우 전체 텍스트를 content로 사용
        if not title and not content:
            content = response_text
        
        return jsonify({
            "title": title,
            "content": content
        })
    
    except Exception as e:
        return jsonify({"error": f"API 호출 중 오류가 발생했습니다: {str(e)}"}), 500


@bp_text.route('/ai/summarize')
def ai_generate_summarize():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "query 파라미터가 필요합니다."}), 400

    prompt = """
    아래 행사 펀딩 소개글을 요약해줘. 30자 이내로.
    """

    prompt += f"input: {query}\noutput:"

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
    
        print("ai_generate_summarize ai response is: ", response)

        return jsonify({"message": response.text})
    
    except Exception as e:
        return jsonify({"error": f"API 호출 중 오류가 발생했습니다: {str(e)}"}), 500


@bp_text.route('/ai/hashtag')
def ai_generate_hashtag():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "query 파라미터가 필요합니다."}), 400

    prompt = """
    아래 행사 펀딩 소개글을 바탕으로 해시태그를 만들어줘.
    * 반드시 !! 아래 형식으로 응답해줘 *
    ["해시태그1", "해시태그2", "해시태그3"]
    
    아래는 예시야.
    input: 우리 동네 철인삼종 챌린지 – 같이 만들어봐요!
    output: ["#철인삼종", "#동네행사", "#참여하기"]
    ----------------------------
    """

    prompt += f"input: {query}\noutput:"

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
    
        print("ai_generate_hashtag ai response is: ", response)

        response_text = response.text.strip()

        print("ai_generate_hashtag response_text is: ", response_text)

        hashtags = extract_list(response_text)

        print("ai_generate_hashtag hashtags is: ", hashtags)

        if hashtags:
            return jsonify({"hashtags": hashtags})
        else:
            return jsonify({"hashtags": []})
    
    except Exception as e:
        return jsonify({"error": f"API 호출 중 오류가 발생했습니다: {str(e)}"}), 500


def extract_list(text):
    # 응답 텍스트 정리
    stripped_text = text.strip()
    
    # JSON 배열 추출 시도
    try:
        items = json.loads(stripped_text)
        if isinstance(items, list):
            return items
    except json.JSONDecodeError:
        pass
    
    # 정규표현식으로 리스트 추출 시도
    match = re.search(r'\[(.*?)\]', stripped_text, re.DOTALL)
    if match:
        try:
            items = ast.literal_eval('[' + match.group(1) + ']')
            if isinstance(items, list):
                return items
        except Exception:
            pass
    
    # 따옴표로 둘러싸인 문자열들을 찾아서 리스트로 변환
    items = re.findall(r'"([^"]*)"', stripped_text)
    if items:
        return items
    
    # 줄바꿈으로 구분된 질문들 추출
    lines = stripped_text.split('\n')
    items = []
    for line in lines:
        line = line.strip()
        if line and '?' in line and len(line) > 5:
            # 불필요한 문자들 제거
            line = re.sub(r'^[\d\-\.\s]*', '', line)
            line = re.sub(r'["\[\]]', '', line)
            if line and len(line) > 5:
                items.append(line)
    
    if items:
        return items[:3]
    
    # 모든 시도가 실패한 경우 빈 리스트 반환
    return []