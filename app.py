from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
import requests
import pandas as pd
import PyPDF2
import io
from openai import OpenAI
import re
import json

app = Flask(__name__)

# Set your OpenAI API key
api_key = 'sk-proj-B8CjOSwdAGvgWGhHjMBPT3BlbkFJGXveG6xgZC9LpOZAkVqd'
client = OpenAI(api_key=api_key)

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def text_to_dataframe(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Convert the text into the proper dataframe. Return only the dictionary format as output. {text}"}
        ]
    )
    summary = response.choices[0].message.content
    return summary

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the file to a temporary location
        pdf_path = './temp.pdf'
        file.save(pdf_path)

        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_path)

        # Convert text to dataframe (as JSON)
        df_json = text_to_dataframe(extracted_text)

        # Extract JSON data from the response
        pattern = r'{(.*?)}'
        matches = re.findall(pattern, df_json, re.DOTALL)
        if matches:
            json_data = matches[0]
            parsed_data = json.loads('{' + json_data + '}')
            return jsonify(parsed_data), 200
        else:
            return jsonify({"error": "No valid data extracted"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
