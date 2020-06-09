import numpy as np
from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import pandas as pd
from flask_cors import CORS
import math

dataset_path = os.path.abspath('src/dataset/suicide.csv')

app = Flask(__name__, static_url_path='/static')
CORS(app)

# fungsi untuk membaca dataset
def getDf(country = None):
  data = pd.read_csv(dataset_path)

  if (country == None):
    return data
  
  return data[data['country'] == country]

# mengirim untuk halaman  utama
@app.route('/')
def index():
  return app.send_static_file('index.html')

# mengirim static file untuk country list
@app.route('/country')
def country():
  return app.send_static_file('country-list.html')

# mengirim static file untuk country list
@app.route('/country/<x>')
def indexx(x):
  return app.send_static_file('country.html')

# mengirim file image
@app.route('/img/<path:path>')
def sendImg(path):
  return send_from_directory('static/img', path)


'''
Code ini digunaan untuk menampilkan nilai pada card awal halaman utama
'''
@app.route('/api/overview')
def overview():
  # membaca dataset
  df = getDf()
  # mengelompokan data
  tmp = df.groupby(['sex']).suicides_no.sum()

  # perhitungan jumlah kematian
  male_suicide = np.round(tmp['male'] / 1000)
  female_suicide = np.round(tmp['female'] / 1000)
  total_suicide = np.round(tmp.sum() / 1000)

  # mencari tahun awal dan akhir
  minYear = df['year'].min()
  maxYear = df['year'].max()

  # menghitung growth rate
  suicide_1985 = df[df['year'] == minYear].suicides_no.sum()
  suicide_2015 = df[df['year'] == maxYear].suicides_no.sum()
  growth = suicide_2015 / suicide_1985
  growth = growth ** (1 / (maxYear - minYear))
  growth = round((growth - 1) * 100, 2)

  # mengirim seluruh hasil
  return jsonify({
    'totalSuicide': f'{np.int(total_suicide)}K',
    'maleSuicide': f'{np.int(male_suicide)}K',
    'femaleSuicide': f'{np.int(female_suicide)}K',
    'growth': f'{growth}%'
  })

'''
Code ini digunakan untuk menampilkan nilai trend
'''
@app.route('/api/trend')
def growth():
  # membaca dataset
  data = getDf()

  # membaca pengelompokan data yang di inginkan
  by = request.args.get('by', 'Total')

  if (by == 'Genre'):
    # perhitungan jumlah kematian
    tmp = data.groupby(['year', 'sex'])
    pop = tmp.population.sum().unstack(1)
    suicide = tmp.suicides_no.sum().unstack(1)
    suicide_rate = (suicide / pop) * 100000

    # pemformatan data sebelum pengiriman
    res = []
    for x in range(len(suicide_rate.index)):
      data = {}
      data['year'] = str(suicide_rate.index[x])
      data['male'] = round(suicide_rate.iloc[x, 1], 2)
      data['female'] = round(suicide_rate.iloc[x, 0], 2)
      res.append(data)
    
    # mengirim data
    return jsonify(res)
    
  if (by == 'Age'):
    # perhitungan jumlah kematian
    tmp = data.groupby(['year', 'age'])
    pop = tmp.population.sum().unstack(1)
    suicide = tmp.suicides_no.sum().unstack(1)
    suicide_rate = (suicide / pop) * 100000

    # pemformatan data sebelum pengiriman
    res = []
    for x in range(len(suicide_rate.index)):
      data = {}
      data['year'] = str(suicide_rate.index[x])
      data['15-24 years'] = 0 if math.isnan(suicide_rate.iloc[x, 0]) else round(suicide_rate.iloc[x, 0], 2)
      data['25-34 years'] = 0 if math.isnan(suicide_rate.iloc[x, 1]) else round(suicide_rate.iloc[x, 1], 2)
      data['35-54 years'] = 0 if math.isnan(suicide_rate.iloc[x, 2]) else round(suicide_rate.iloc[x, 2], 2)
      data['5-14 years'] = 0 if math.isnan(suicide_rate.iloc[x, 3]) else round(suicide_rate.iloc[x, 3], 2)
      data['55-74 years'] = 0 if math.isnan(suicide_rate.iloc[x, 4]) else round(suicide_rate.iloc[x, 4], 2)
      data['75+ years'] = 0 if math.isnan(suicide_rate.iloc[x, 5]) else round(suicide_rate.iloc[x, 5], 2)
      res.append(data)
    
    # mengirim data
    return jsonify(res)

  # perhitungan jumlah kematian
  tmp = data.groupby(['year'])
  pop = tmp.population.sum()
  suicide = tmp.suicides_no.sum()
  suicide_rate = (suicide / pop) * 100000

  # pemformatan data sebelum pengiriman
  res = []
  for x in range(len(suicide_rate.index)):
    data = {}
    data['year'] = str(suicide_rate.index[x])
    data['total'] = round(suicide_rate.iloc[x], 2)
    res.append(data)

  # mengirim data
  return jsonify(res)

'''
code ini diguakan untuk menampilkan total bunuh diri dari tahun ke tahun
'''
@app.route('/api/count')
def growthData():
  # membaca data set
  df = getDf()
  # membaca pengelompokan data yang di inginkan
  by = request.args.get('by', 'Total')

  if (by == 'Age'):
    # melakukan pengelompokan data
    df = df.groupby(['year', 'age']).suicides_no.sum().unstack(1).sort_index()

    # pemformatan data sebelum pengiriman
    res = []
    for x in range(len(df)):
      data = {}
      for y in range(len(df.iloc[x].index)):
        data['year'] = str(df.index[x])
        data[str(df.iloc[x].index[y])] = 0 if math.isnan(df.iloc[x].iloc[y]) else np.int(df.iloc[x].iloc[y])
      
      res.append(data)

    # mengirim data
    return jsonify(res)
  
  if (by == 'Genre'):
    # melakukan pengelompokan data
    df = df.groupby(['year', 'sex']).suicides_no.sum().unstack(1).sort_index()

    # pemformatan data sebelum pengiriman
    res = []
    for x in range(len(df)):
      data = {}
      for y in range(len(df.iloc[x].index)):
        data['year'] = str(df.index[x])
        data['female'] = 0 if math.isnan(df.iloc[x, 0]) else np.int(df.iloc[x, 0])
        data['male'] = 0 if math.isnan(df.iloc[x, 1]) else np.int(df.iloc[x, 1])
      
      res.append(data)

    # mengirim data
    return jsonify(res)
  
  # melakukan pengelompokan data
  df = df.groupby(['year']).suicides_no.sum().sort_index()

# pemformatan data sebelum pengiriman
  res = []
  for x in range(len(df)):
    data = {}
    data['year'] = str(df.index[x])
    data['total'] = 0 if math.isnan(df.iloc[x]) else np.int(df.iloc[x])
    
    res.append(data)

  # mengirim data
  return jsonify(res)

'''
code ini digunakan untuk menampilkan data berdasarkan genre
'''
@app.route('/api/sex')
def sexData():
  # membaca data set
  df = getDf()
  # melakukan pengelompokan data
  dfSex = df.groupby(['sex']).suicides_no.sum()
  df = df.groupby(['sex', 'age']).suicides_no.sum().unstack(1)

# pemformatan data sebelum pengiriman
  res = []
  for x in range(len(df)):
    res.append({
      'genre': df.index[x],
      df.iloc[x].index[0]: np.int(df.iloc[x, 0]),
      df.iloc[x].index[1]: np.int(df.iloc[x, 1]),
      df.iloc[x].index[2]: np.int(df.iloc[x, 2]),
      df.iloc[x].index[3]: np.int(df.iloc[x, 3]),
      df.iloc[x].index[4]: np.int(df.iloc[x, 4]),
      df.iloc[x].index[5]: np.int(df.iloc[x, 5]),
      'total': np.int(dfSex.iloc[x])
    })

    # mengirim data
  return jsonify(res)

'''
code ini digunakan untuk menampilkan data berdasarkan umur
'''
@app.route('/api/age')
def ageData():
  # membaca data set
  df = getDf()
  # melakukan pengelompokan data
  df = df.groupby(['age', 'sex']).suicides_no.sum().unstack(1)
  df['total '] = df['female'] + df['male']

# pemformatan data sebelum pengiriman
  res = []
  for x in range(len(df)):
    res.append({
      'age': df.index[x],
      'female': np.int(df.iloc[x, 0]),
      'male': np.int(df.iloc[x, 1]),
      'total': np.int(df.iloc[x, 2])
    })

  # mengirim data
  return jsonify(res)

'''
menampilkan data negara terbanyak yang memiliki kasus bunuh diri
'''
@app.route('/api/topCountry')
def topCountry():
  # membaca data set
  df = getDf()

# melakukan pengelompokan data
  df = df\
    .groupby(['country'])\
    .suicides_no.sum()

  df = df.sort_values(ascending=False).head(10)
  
  # pemformatan data sebelum pengiriman
  res = []
  for x in range(len(df.index)):
    res.append({
      'country': df.index[x],
      'total': np.int(df.iloc[x])
    })

  # mengirim data
  return jsonify(res)

'''
menampikan negara dengan tingkat bunuh diri ter tinggi
'''
@app.route('/api/trendCountry')
def trendCountry():
  # membaca data set
  df = getDf()

# melakukan pengelompokan data
  tmp = df.groupby(['country'])
  pop = tmp.population.sum()
  suicide = tmp.suicides_no.sum()
  suicide_rate = (suicide / pop) * 100000
  suicide_rate.sort_values(ascending=False, inplace=True)
  suicide_rate = suicide_rate.head(10)
  
  # pemformatan data sebelum pengiriman
  res = []
  for x in range(len(suicide_rate.index)):
    res.append({
      'country': suicide_rate.index[x],
      'total': round(suicide_rate.iloc[x], 2)
    })

  # mengirim data
  return jsonify(res)

'''
Code ini digunaan untuk menampilkan nilai pada card awal halaman country
'''
@app.route('/<country>/api/overview')
def overviewCountry(country):
  # membaca data set
  df = getDf(country=country)

  # melakukan pengelompokan data
  tmp = df.groupby(['sex']).suicides_no.sum()

  male_suicide = np.round(tmp['male'] / 1000)
  female_suicide = np.round(tmp['female'] / 1000)
  total_suicide = np.round(tmp.sum() / 1000)

  minYear = df['year'].min()
  maxYear = df['year'].max()

  suicide_1985 = df[df['year'] == minYear].suicides_no.sum()
  suicide_2015 = df[df['year'] == maxYear].suicides_no.sum()
  growth = suicide_2015 / suicide_1985
  growth = growth ** (1 / (maxYear - minYear))
  growth = round((growth - 1) * 100, 2)
  if (np.isinf(growth)):
    growth = 100


# mengirim data
  return jsonify({
    'totalSuicide': f'{np.int(total_suicide)}K',
    'maleSuicide': f'{np.int(male_suicide)}K',
    'femaleSuicide': f'{np.int(female_suicide)}K',
    'growth': f'{growth}%'
  })

'''
menampilkan trend berdasarkan country
'''
@app.route('/<country>/api/trend')
def growthCountry(country):
  # membaca data set
  data = getDf(country=country)

# membaca pengelompokan data yang di inginkan
  by = request.args.get('by', 'Total')

  if (by == 'Genre'):
    # melakukan pengelompokan data
    tmp = data.groupby(['year', 'sex'])
    pop = tmp.population.sum().unstack(1)
    suicide = tmp.suicides_no.sum().unstack(1)
    suicide_rate = (suicide / pop) * 100000

  # pemformatan data sebelum pengiriman
    res = []
    for x in range(len(suicide_rate.index)):
      data = {}
      data['year'] = str(suicide_rate.index[x])
      data['male'] = round(suicide_rate.iloc[x, 1], 2)
      data['female'] = round(suicide_rate.iloc[x, 0], 2)
      res.append(data)
    
    # mengirim data
    return jsonify(res)
    
  if (by == 'Age'):
    # melakukan pengelompokan data
    tmp = data.groupby(['year', 'age'])
    pop = tmp.population.sum().unstack(1)
    suicide = tmp.suicides_no.sum().unstack(1)
    suicide_rate = (suicide / pop) * 100000

    # pemformatan data sebelum pengiriman
    res = []
    for x in range(len(suicide_rate.index)):
      data = {}
      data['year'] = str(suicide_rate.index[x])
      # check is nan
      data['15-24 years'] = 0 if math.isnan(suicide_rate.iloc[x, 0]) else round(suicide_rate.iloc[x, 0], 2)
      data['25-34 years'] = 0 if math.isnan(suicide_rate.iloc[x, 1]) else round(suicide_rate.iloc[x, 1], 2)
      data['35-54 years'] = 0 if math.isnan(suicide_rate.iloc[x, 2]) else round(suicide_rate.iloc[x, 2], 2)
      data['5-14 years'] = 0 if math.isnan(suicide_rate.iloc[x, 3]) else round(suicide_rate.iloc[x, 3], 2)
      data['55-74 years'] = 0 if math.isnan(suicide_rate.iloc[x, 4]) else round(suicide_rate.iloc[x, 4], 2)
      data['75+ years'] = 0 if math.isnan(suicide_rate.iloc[x, 5]) else round(suicide_rate.iloc[x, 5], 2)
      res.append(data)
    
    # mengirim data
    return jsonify(res)

# melakukan pengelompokan data
  tmp = data.groupby(['year'])
  pop = tmp.population.sum()
  suicide = tmp.suicides_no.sum()
  suicide_rate = (suicide / pop) * 100000

# pemformatan data sebelum pengiriman
  res = []
  for x in range(len(suicide_rate.index)):
    data = {}
    data['year'] = str(suicide_rate.index[x])
    data['total'] = round(suicide_rate.iloc[x], 2)
    res.append(data)

# mengirim data
  return jsonify(res)

'''
menampilkan total bunuh diri dari tahun ke tahun
'''
@app.route('/<country>/api/count')
def growthDataCountry(country):
  # membaca data set
  df = getDf(country=country)
  # membaca pengelompokan data yang di inginkan
  by = request.args.get('by', 'Total')

  if (by == 'Age'):
    # melakukan pengelompokan data
    df = df.groupby(['year', 'age']).suicides_no.sum().unstack(1).sort_index()

# pemformatan data sebelum pengiriman
    res = []
    for x in range(len(df)):
      data = {}
      for y in range(len(df.iloc[x].index)):
        data['year'] = str(df.index[x])
        data[str(df.iloc[x].index[y])] = 0 if math.isnan(df.iloc[x].iloc[y]) else np.int(df.iloc[x].iloc[y])
      
      res.append(data)

    # mengirim data
    return jsonify(res)
  
  if (by == 'Genre'):
    # melakukan pengelompokan data
    df = df.groupby(['year', 'sex']).suicides_no.sum().unstack(1).sort_index()

# pemformatan data sebelum pengiriman
    res = []
    for x in range(len(df)):
      data = {}
      for y in range(len(df.iloc[x].index)):
        data['year'] = str(df.index[x])
        data['female'] = 0 if math.isnan(df.iloc[x, 0]) else np.int(df.iloc[x, 0])
        data['male'] = 0 if math.isnan(df.iloc[x, 1]) else np.int(df.iloc[x, 1])
      
      res.append(data)
      # mengirim data
    return jsonify(res)
  
  # melakukan pengelompokan data
  df = df.groupby(['year']).suicides_no.sum().sort_index()

# pemformatan data sebelum pengiriman
  res = []
  for x in range(len(df)):
    data = {}
    data['year'] = str(df.index[x])
    data['total'] = 0 if math.isnan(df.iloc[x]) else np.int(df.iloc[x])
    
    res.append(data)
    # mengirim data
  return jsonify(res)

'''
bunuh diri berdasar genre pada sebuah negara
'''
@app.route('/<country>/api/sex')
def sexDataCountry(country):
  # membaca data set
  df = getDf(country=country)
  dfSex = df.groupby(['sex']).suicides_no.sum()
  # melakukan pengelompokan data
  df = df.groupby(['sex', 'age']).suicides_no.sum().unstack(1)

# pemformatan data sebelum pengiriman
  res = []
  for x in range(len(df)):
    res.append({
      'genre': df.index[x],
      df.iloc[x].index[0]: np.int(df.iloc[x, 0]),
      df.iloc[x].index[1]: np.int(df.iloc[x, 1]),
      df.iloc[x].index[2]: np.int(df.iloc[x, 2]),
      df.iloc[x].index[3]: np.int(df.iloc[x, 3]),
      df.iloc[x].index[4]: np.int(df.iloc[x, 4]),
      df.iloc[x].index[5]: np.int(df.iloc[x, 5]),
      'total': np.int(dfSex.iloc[x])
    })
    # mengirim data
  return jsonify(res)

'''
bunuh diri berdasarkan umur ada sebuah negara
'''
@app.route('/<country>/api/age')
def ageDataCountry(country):
  # membaca data set
  df = getDf(country=country)
  # melakukan pengelompokan data
  df = df.groupby(['age', 'sex']).suicides_no.sum().unstack(1)
  df['total '] = df['female'] + df['male']

# pemformatan data sebelum pengiriman
  res = []
  for x in range(len(df)):
    res.append({
      'age': df.index[x],
      'female': np.int(df.iloc[x, 0]),
      'male': np.int(df.iloc[x, 1]),
      'total': np.int(df.iloc[x, 2])
    })
    # mengirim data
  return jsonify(res)

'''
mengambil tahun awal dan akhir dari sebuah negara
'''
@app.route('/<country>/api/year')
def getYear(country):
  # membaca data set
  df = getDf(country=country)
  # mengirim data
  return jsonify({
    'min': int(df['year'].min()),
    'max': int(df['year'].max())
  })

'''
menampilkan data country
'''
@app.route('/api/country')
def countryList():
  # membaca data set
  df = getDf()

# mengirim data
  return jsonify(list(df['country'].unique()))
