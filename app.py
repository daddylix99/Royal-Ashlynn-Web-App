from flask import Flask, render_template, request, jsonify, session, send_file
import os
import requests
from datetime import datetime
import secrets
import openai
import urllib.parse
import base64
import hashlib
import json
import qrcode
from io import BytesIO
import random
import string
import hashlib as hl

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Create uploads folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'gpt-3.5-turbo')

        if not OPENAI_API_KEY and not GEMINI_API_KEY:
            return jsonify({'error': 'API key not configured'}), 500

        if model.startswith('gpt') and OPENAI_API_KEY:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message}
                ]
            )
            reply = response.choices[0].message.content
        elif model.startswith('gemini') and GEMINI_API_KEY:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": message}]}]}
            resp = requests.post(url, json=payload)
            reply = resp.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            reply = "API key not available for selected model."

        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/image-generator')
def image_generator():
    return render_template('image_generator.html')

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        image_url += "?width=1024&height=1024&nologo=true"

        return jsonify({'image_url': image_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/instagram-downloader')
def instagram_downloader():
    return render_template('instagram.html')

@app.route('/temp-mail')
def temp_mail():
    return render_template('temp_mail.html')

@app.route('/api/temp-mail/generate', methods=['POST'])
def generate_temp_mail():
    try:
        response = requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
        email = response.json()[0]
        session['temp_email'] = email
        return jsonify({'email': email})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/anime-wallpapers')
def anime_wallpapers():
    return render_template('anime.html')

@app.route('/ip-lookup')
def ip_lookup():
    return render_template('ip_lookup.html')

@app.route('/sms-sender')
def sms_sender():
    return render_template('sms_sender.html')

@app.route('/dev-tools')
def dev_tools():
    return render_template('dev_tools.html')

@app.route('/unique-tools')
def unique_tools():
    return render_template('unique_tools.html')

@app.route('/subtitle-tools')
def subtitle_tools():
    return render_template('subtitle_tools.html')

@app.route('/youtube-downloader')
def youtube_downloader():
    return render_template('youtube.html')

@app.route('/weather')
def weather():
    return render_template('weather.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
