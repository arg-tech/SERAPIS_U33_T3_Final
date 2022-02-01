from flask import Flask, render_template, request
from jinja2 import Environment, FileSystemLoader
from flask import json
from flask import jsonify
import os
import argparse
import json
import hashlib

from run_model import get_argument_relations

app=Flask(__name__)

# @app.route('/')

# def hello():
#     return 'Hello World'

@app.route('/identifyrelations', methods = ['POST'])
def identifyrelations():
    print("posted")
    if request.method == 'POST':
        print("posted")
        f = request.files['file']
        f.save(f.filename)
        ff = open(f.filename,'r')
        content = ff.read()
        result = get_argument_relations(f.filename)
        print(result)
    return result
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')