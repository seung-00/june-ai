from flask import Flask, jsonify
from ai_text import bp_text
from ai_image import bp_image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return jsonify({
        "message": "Hello World!",
        "status": "success"
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "flask-app"
    })

# 블루프린트 등록
app.register_blueprint(bp_text)
app.register_blueprint(bp_image)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True) 