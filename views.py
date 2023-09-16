from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from scouter import get_data, convertUsage
import json

views = Blueprint(__name__, "views")

@views.route('/', methods=['POST', 'GET'])
def home():
    if (request.method == 'POST'):
        form_text = request.form['statsbox']
        names = request.form['names']
        results = get_data(form_text, names)
        mon_data = convertUsage(results)
        return render_template('results.html', form_response=results, names=names, mon_data=mon_data)
    else:
        return render_template('index.html')
