import joblib
import numpy as np
import pandas as pd
from datetime import date, timedelta
import mysql.connector as connection

def data():
    mysql = connection.connect(host='sql6.freesqldatabase.com', database='sql6709970',user='sql6709970',passwd='gTUGfbb99U',use_pure=True)
    his_df = pd.read_sql("SELECT * FROM history",mysql)
    last = his_df.iloc[-1,:]
    instalasi = int(last['id_instalasi'])
    print (instalasi)
    level = last['status']
    if level == 'Aman':
        level = 1
    elif level == 'Gangguan':
        level = 2
    elif level == 'Bahaya':
        level = 3
    ins_df = pd.read_sql("SELECT * FROM instalasi",mysql)
    item = ins_df.loc[ins_df['id'] == instalasi]
    print(item)
    check = ins_df.loc[ins_df['nama_instalasi'] == item['nama_instalasi'].values[0]]
    temp=check['suhu_kabel']
    first_check= check.tgl_pengecekan.min()
    print(first_check)
    last_check = check.tgl_pengecekan.max()
    print(last_check)
    day_check = (last_check - first_check).days + 1
    print(day_check,temp,level,last_check)
    return day_check,temp,level,last_check

# Predict diganti
def predict() :
    day_check,temp,level,last_check = data()
    model_rf = joblib.load('my_random_forest.joblib')
    new = np.array ([[day_check,temp.iloc[0] if isinstance(temp, pd.Series) else temp,level]])
    rul = model_rf.predict(new)
    rul = int(rul[0])
    print (rul)
    if rul>=100:
      if level == 1:
        recom = 'Tidak Perlu Perbaikan'
      elif level == 2:
        pemantauan = last_check + timedelta(days=28)
        recom = 'Pemantuan ulang pada Tanggal '+ str(pemantauan)
      else:
        perbaikan = last_check + timedelta(days=7)
        recom = 'Perbaikan pada Tanggal '+ str(perbaikan)
    else : 
      perbaikan = last_check + timedelta(days=rul)
      recom = 'Perbaikan pada Tanggal '+ str(perbaikan)
    return recom

print(predict())

