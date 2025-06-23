from flask import Flask, Response, render_template, send_from_directory
import data
import os

app = Flask(__name__)

@app.route('/download')
def download_pdf():
    # Assumes your CV PDF is stored in a folder named 'static'
    return send_from_directory(directory='static', path='cv.pdf', as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html', bio=data.bio, skills=data.skills)

@app.route('/cv')
def cv():
    return render_template('cv.html', tools=data.tools, skills=data.skills,
        education=data.education, experience=data.experience, bio=data.bio)

@app.route('/projects')
def projects():
    return render_template('projects.html', projects=data.projects, bio=data.bio)

@app.route('/contact')
def contact():
    return render_template('contact.html', bio=data.bio)

#if __name__ == '__main__':
#    app.run(debug=True)
