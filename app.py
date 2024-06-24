from flask import Flask, request, render_template
from transformers import pipeline

app = Flask(__name__)

# Load T5 Summarization Model
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

def summarize_text(text):
    summary = summarizer(text, max_length=150, min_length=40, do_sample=False)
    return summary[0]['summary_text']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    if 'file' in request.files:
        file = request.files['file']
        article = file.read().decode('utf-8')
    else:
        article = request.form['article']
    
    summary = summarize_text(article)
    return render_template('result.html', article=article, summary=summary)

if __name__ == '__main__':
    app.run(debug=True)