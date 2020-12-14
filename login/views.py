from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.template import loader

import datetime,quandl
import numpy as np
import math
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing,neighbors
from sklearn.model_selection import train_test_split

import json
import requests

def index(request):
    return render(request, 'login/base.html')

def graph(request):
    searchValue = request.session.get('search', None)
	
def search1(request):
    searchValue = request.POST['search']
    print (searchValue)
    request.session['search'] = searchValue
    t = loader.get_template('login/base2.html')
    c = {'search': searchValue}
    return HttpResponse(t.render(c, request))

def search(request):
    searchValue = request.POST['search']
    print (searchValue)
    request.session['search'] = searchValue
    df = quandl.get(searchValue)
    '''
    #Selection of equity
    url = 'http://signals.pythonanywhere.com/getfulldata?val=' + request.session.get('search',None)
    df = requests.get(url)
    #print (df.text)
    df = json.dumps(df.text)
    #print(df.tail())
    '''

    #High/Low, pct calculation

    df = df[['Open','High','Low','Close']]
    df['HL_pct'] = ((df['High'] - df['Low']) / df['Close']) * 100.0
    df['pct_ch'] = ((df['Close'] - df['Open']) / df['Open']) * 100.0

    df = df[['Close','HL_pct','pct_ch']]

    #forecast label by 1% of df length

    forecast_col = 'Close'
    df.fillna('-1', inplace=True)
    #print(len(df))
    forecast_out = int(math.ceil(0.01*len(df)))
    df['label'] = df[forecast_col].shift(-forecast_out)

    #print('\n')
    #print(df.tail(10))

    #Create arrays for features and labels

    X = np.array(df.drop(['label'],1))
    X = preprocessing.scale(X)
    X = X[:-forecast_out:]
    X_lately = X[-forecast_out:]

    df.dropna(inplace=True)
    y = np.array(df['label'])
    y = np.array(df['label'])

    #cross validate train, test variables

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

   
    clf = neighbors.KNeighborsRegressor()
    clf.fit(X_train, y_train)
    accuracy = clf.score(X_test, y_test)

    print(accuracy)

    forecast_set = clf.predict(X_lately)
    print(forecast_set, accuracy, forecast_out)
    df['Forecast'] = np.nan

    last_date = df.iloc[-1].name
    last_unix = last_date.timestamp()
    one_day = 86400
    next_unix = last_unix + one_day

    for i in forecast_set:
        next_date = datetime.datetime.fromtimestamp(next_unix)
        next_unix += one_day
        df.loc[next_date] = [np.nan for _ in range(len(df.columns)-1)] + [i]

    print(df)
    t = loader.get_template('login/base2.html')
    c = {'search': searchValue,'table':df}
    return HttpResponse(t.render(c, request))

def create(request):
	uname = request.POST.get('uname')
	pwd = request.POST.get('pwd')
	payload = {}
	payload['password'] = pwd
	payload['username'] = uname
	#jsonVal = json.loads(data)
	#data = dict(data)
	print(json.dumps(payload, indent=4, sort_keys=True))
	headers = {
		"content-type" : "application/json"
	}
	r = requests.post('http://signals.pythonanywhere.com/register', headers = headers, json=payload)
	messages.info(request,'Registered successfully.')
	return render(request, 'login/base.html')

def validate(request):
	uname = request.POST.get('uname')
	pwd = request.POST.get('psw')
	payload = {}
	payload['password'] = pwd
	payload['username'] = uname
	headers = {
		"content-type" : "application/json"
	}
	r = requests.post('http://signals.pythonanywhere.com/login', headers = headers, json=payload)
	messages.info(request,'Loggedin successfully.')
	return render(request, 'login/base.html')
	
