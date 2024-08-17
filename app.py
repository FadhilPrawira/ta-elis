#Bagian Import
from flask import Flask, request,  jsonify, render_template
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import MySQLdb.cursors
import os
import shutil
import warnings
import cv2
import numpy as np
import matplotlib.pyplot as plt
import ultralytics
import torch
from ultralytics import YOLO
import pandas as pd
import joblib
from datetime import datetime, timedelta
import mysql.connector as connection

warnings.filterwarnings("ignore", category=UserWarning)

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

# Konfigurasi MySQL
app = Flask(__name__)
app.secret_key = 'secret'
app.config['MYSQL_HOST'] = 'sql6.freesqldatabase.com'
app.config['MYSQL_USER'] = 'sql6709970'
app.config['MYSQL_PASSWORD'] = 'gTUGfbb99U'
app.config['MYSQL_DB'] = 'sql6709970'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER'] = './static/uploads'
app.config['STATUS'] = ''
app.config['HOT_AREA'] = ''
app.config['PREDIKSI_TANGGAL'] = ''

mysql = MySQL(app)

# Bagian Login Website 
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, email, password):
        self.email = email
        self.password = password
    
    def get_id(self):
        return self.email

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM login WHERE email = %s", (user_id,))
    user = cur.fetchone()
    if user:
        return User(user['email'], user['password'])  # Access user data using dictionary keys
    return None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM login WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    if user:
        user_obj = User(user['email'], user['password'])  # Access user data using dictionary keys
        login_user(user_obj)
        return redirect(url_for('main_menu'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('index'))

# Fungsi untuk meresize gambar pakai skala
# def resize_image(image, target_width=100):
#     scale_percent = target_width / image.shape[1] * 100
#     width = int(image.shape[1] * (scale_percent / 100))
#     height = int(image.shape[0] * (scale_percent / 100))
#     dim = (width, height)
#     return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

# Fungsi untuk meresize gambar ukuran target size = width = height
def resize_image(image, target_size=500):
    dim = (target_size, target_size)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

##PEDIKSI TANGGAL PERBAIKAN##
#Menarik Data dari Basis Data
def data(safety_level):
    mysql = connection.connect(host=app.config['MYSQL_HOST'], database=app.config['MYSQL_DB'], user=app.config['MYSQL_USER'], passwd=app.config['MYSQL_PASSWORD'],use_pure=True)
    ins_df = pd.read_sql("SELECT * FROM instalasi",mysql)
    nama_instalasi = request.form['property_name']
    print(nama_instalasi)
    temp= request.form['property_suhu']
    print(temp)
    level = safety_level
    if level == 'Aman':
        level = 1
    elif level == 'Gangguan':
        level = 2
    elif level == 'Bahaya':
        level = 3
    print(level)
    last_check = request.form['check_in_date']
    last_check = datetime.strptime(last_check, '%Y-%m-%d').date()
    print(last_check)
    check = ins_df.loc[ins_df['nama_instalasi'] == nama_instalasi]
    if len(check.index) ==0:
        day_check=1
    else:
        first_check= check.tgl_pengecekan.min()
        print(first_check)
        day_check = (last_check - first_check).days + 1
    print(day_check,temp,level,last_check)
    return day_check,temp,level,last_check
# Prediksi
def predict(safety_level) :
    day_check,temp,level,last_check = data(safety_level)
    model_rf = joblib.load('my_random_forest.joblib')
    new = np.array ([[day_check,temp.iloc[0] if isinstance(temp, pd.Series) else temp,level]])
    rul = model_rf.predict(new)
    rul = int(rul[0])
    print (rul)
    if rul>=100:
      if level == 1:
        recom = 'Tidak Perlu Perbaikan'
      else:
        recom = last_check + timedelta(days=14)
        recom = recom.strftime("%d/%m/%Y")
    else : 
      recom = last_check + timedelta(days=rul)
      recom = recom.strftime("%d/%m/%Y")
    return recom

    
# Bagian Deteksi dan Segmentasi
# Melakukan deteksi dari data yang sudah diresize
def detect_and_segment_object(original_image_path, flir_image_path, target_size=500, has_damages=True):
    # Menginput gambar dari file
    original_image = cv2.imread(original_image_path)
    flir_image = cv2.imread(flir_image_path)

    resized_original_image = resize_image(original_image, target_size)
    resized_flir_image = resize_image(flir_image, target_size)

    # Bagian deteksi jaringan saraf tiruan
    def detect_cnn(flir_image_path):
        model = YOLO('best.pt')
        results = model.predict(flir_image_path)
        results = results[0].probs.data
        class_list = ['Aman', 'Gangguan', 'Bahaya']
        output_class = class_list[np.argmax(results)]
        return output_class

    output_class = detect_cnn(resized_flir_image)
    safety_level = output_class
    print(f"Deteksi Kabel dengan metode Jaringan Saraf Tiruan: {safety_level}")

    # Mendeteksi objek berdasarkan warna merah dan merah cendrung putih dalam gambar menggunakan representasi warna HSV (Hue, Saturation, Value)
    hsv_image = cv2.cvtColor(resized_flir_image, cv2.COLOR_BGR2HSV)

    # Range warna HSV untuk suhu panas (white-red,red)
    #https://www.selecolor.com/en/hsv-color-picker/ gunakan url untuk mengatur nilai hsv
    lower_red = np.array([0, 100, 100])  # red
    upper_red = np.array([10, 255, 255])

    lower_white = np.array([0, 0, 200])  # white
    upper_white = np.array([15, 50, 255])

    # Membuat mask untuk menentukan range warna
    red_mask = cv2.inRange(hsv_image, lower_red, upper_red)
    white_mask = cv2.inRange(hsv_image, lower_white, upper_white)
      
    # Mengkombinasikan mask
    hot_mask = cv2.bitwise_or(red_mask, white_mask)

    # Mencari contours dari combined mask
    contours, _ = cv2.findContours(hot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Variabel untuk menyimpan jumlah area panas
    total_hot_area = 0

    # Membuat mask untuk hot area
    hot_mask_image1 = np.zeros_like(resized_original_image)
    hot_mask_image2 = np.zeros_like(resized_original_image)

    # Iterate through contours and update mask
    for contour in contours:     
        #Hitung luas contur
        area = cv2.contourArea(contour)
        # Jika luas kontur mencukupi, itu mungkin merupakan kabel merah
        if area > 500:  # Ubah nilai ini sesuai dengan kebutuhan
            # Gambar kotak pembatas di sekitar kontur / Deteksi
            x, y, w, h = cv2.boundingRect(contour)
            cv2.drawContours(hot_mask_image1, [contour], -1, (0, 0, 255), thickness=cv2.FILLED)
            cv2.rectangle(resized_flir_image, (x, y), (x+w, y+h), (255, 255, 255), 5)
            
            # Tambahkan luas kotak pembatas pada total area panas
            total_hot_area += 1

       # x, y, w, h = cv2.boundingRect(contour) / Segmentasi
        cv2.drawContours(hot_mask_image2, [contour], -1, (0, 0, 255), thickness=cv2.FILLED)

    # Generate image with edge detection on hot-colored pixels area (White, merah)
    hot_area_edges = cv2.Canny(hot_mask_image2, 100, 200)

   # Resize hot_mask_image1 to match the size of flir_image
    hot_mask_image1_resized = cv2.resize(hot_mask_image1, (flir_image.shape[1], flir_image.shape[0]))
    # Add the resized hot_mask_image1 onto original_image with blending
    blended_image1 = cv2.addWeighted(flir_image, 0.45, hot_mask_image1_resized, 0.55, 0)

       # Resize hot_mask_image1 to match the size of flir_image
    hot_mask_image2_resized = cv2.resize(hot_mask_image2, (flir_image.shape[1], flir_image.shape[0]))
    # Add the resized hot_mask_image1 onto original_image with blending
    blended_image2 = cv2.addWeighted(flir_image, 0.2, hot_mask_image2_resized, 0.8, 0)

    # Membuat Plot Gambar
    # Function to determine safety level based on suhu
    plt.figure(figsize=(9, 6))
    plt.subplot(2, 3, 1)
    plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    plt.title('Gambar Asli')
    plt.axis('off')

    # Display the original FLIR image
    plt.subplot(2, 3, 2)
    plt.imshow(cv2.cvtColor(flir_image, cv2.COLOR_BGR2RGB))
    plt.title('Gambar FLIR')
    plt.axis('off')

    # Display the image with hot-marked areas (deteksi)
    plt.subplot(2, 3, 3)
    plt.imshow(cv2.cvtColor(resized_flir_image, cv2.COLOR_BGR2RGB))
    plt.title('Deteksi Area Panas')
    plt.axis('off')

    # Display the image with hot-marked areas (segmentasi)
    plt.subplot(2, 3, 4)
    plt.imshow(cv2.cvtColor(blended_image2, cv2.COLOR_BGR2RGB))
    plt.title('Segmentasi Area Panas')
    plt.axis('off')

    # Display the image with hot areas and edge detection
    plt.subplot(2, 3, 5)
    plt.imshow(hot_area_edges, cmap='gray')
    plt.title('Deteksi Tepi pada Area Panas')
    plt.axis('off')
  
    # #Rara prediksi  
    prediksi_tgl = predict(safety_level)
    app.config['PREDIKSI_TANGGAL'] = prediksi_tgl
    print( f'Warning: {prediksi_tgl}')

    # Print total hot area
    app.config['HOT_AREA'] = total_hot_area
    print( f'Total Hot Area: {total_hot_area}')


    # Display the result
    plt.savefig('./static/uploads/prediction.jpeg')
    return ['./static/uploads/prediction.jpeg', safety_level]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/main_menu', methods=['GET'])
@login_required
def main_menu():
    return render_template('main menu.html')

@app.route('/deteksi', methods=['GET', 'POST'])
def deteksi():
    return render_template('fitur deteksi.html')

@app.route('/deteksi/<status>', methods=['POST'])
def deteksi_status(status):
    if request.method == 'POST' and status == 'cek':
        files = ['property_image', 'property_image2']
        images = []
        for x in files:
            if x not in request.files:
                return jsonify({'status': False, 'message': 'Tidak terdapat file gambar'}), 400
            file = request.files[x]
            if file.filename == '':
                return jsonify({'status': False, 'message': 'Harap pilih file gambar'}), 400
            if file and allowed_file(file.filename):
                if x == 'property_image':
                    file_name = 'gambar_asli'
                else:
                    file_name = 'gambar_flir'
                path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_name}.jpeg")
                file.save(path)
                images.append(path)
                print(f'File {file.filename} saved to {path}')
            else:
                return jsonify({'status': False, 'message': 'Format gambar tidak didukung'}), 400

        result = detect_and_segment_object(images[0], images[1])
        if result == 'gagal':
            return jsonify({'status': False, 'message': 'Gagal melakukan deteksi, pastikan file gambar sesuai'}), 400
        app.config['STATUS'] = result[1]
        return jsonify({'status': True, 'message': 'Gambar berhasil dideteksi', 'data': {'hasil_prediksi': result[0], 'prediksi': app.config['HOT_AREA'], 'prediksi_tgl' : app.config['PREDIKSI_TANGGAL'],'status': app.config['STATUS']}}), 200

    elif request.method == 'POST' and status == 'submit':
        result_status = app.config['STATUS']
        if result_status == '':
            return jsonify({'status': False, 'message': 'Harap lakukan deteksi terlebih dahulu'}), 400
        nama_instalasi = request.form['property_name']
        suhu_kabel = request.form['property_suhu']
        tgl_pengecekan = request.form['check_in_date']
        prediksi = app.config['HOT_AREA']
        prediksi_tgl = app.config['PREDIKSI_TANGGAL']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO instalasi (nama_instalasi, suhu_kabel, tgl_pengecekan, prediksi_tgl) VALUES (%s, %s, %s, %s)', (nama_instalasi, suhu_kabel, tgl_pengecekan, prediksi_tgl))
        mysql.connection.commit()

        cursor.execute('SELECT id FROM instalasi ORDER BY id DESC LIMIT 1')
        mysql.connection.commit()
        latest_record = cursor.fetchone()['id']
        source = app.config['UPLOAD_FOLDER']
        destination = f'./static/images/{latest_record}'
        if not os.path.exists(destination):
            os.makedirs(destination)
        allfiles = os.listdir(source)
        for f in allfiles:
          
            src_path = os.path.normpath(os.path.join(source, f))
            dst_path = os.path.normpath(os.path.join(destination, f))
            shutil.move(src_path, dst_path)
            print(f'Moved {src_path} to {dst_path}')
        print(f'Destination: {destination}')
       
        gambar_asli_path = destination + '/gambar_asli.jpeg'
        gambar_flir_path = destination + '/gambar_flir.jpeg'
        gambar_hasil_path = destination + '/prediction.jpeg'

        # Construct the SQL query using f-strings
        query_update_gambar = f'UPDATE instalasi SET gambar_asli = "{gambar_asli_path}", gambar_flir = "{gambar_flir_path}", gambar_hasil = "{gambar_hasil_path}" WHERE id = {latest_record}'
        print(query_update_gambar)
        cursor.execute(query_update_gambar)
        mysql.connection.commit()
        # query_insert_history = 'INSERT INTO history (id_instalasi, status, prediksi, status_akhir) VALUES (%s, %s, %s, %s)', (latest_record, prediksi, result_status,)
        query_insert_history = f'INSERT INTO history (id_instalasi, status, prediksi, prediksi_tgl) VALUES ({latest_record}, \'{result_status}\', \'{prediksi}\', \'{prediksi_tgl}\')'
        print(query_insert_history)
        cursor.execute(query_insert_history)
        mysql.connection.commit()
        return jsonify({'status': True, 'message': 'Data berhasil disimpan'}), 200

@app.route('/riwayat/<selected_data>', methods=['GET'])
def get_riwayat(selected_data):
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if selected_data == 'get-history':
            cursor.execute('SELECT * FROM history')
            data = cursor.fetchall()
            return jsonify({'status': True, 'message': 'Berhasil mengambil data history', 'data': data}), 200
        elif selected_data == 'get-instalasi':
            cursor.execute('SELECT * FROM instalasi')
            data = cursor.fetchall()
            return jsonify({'status': True, 'message': 'Berhasil mengambil data instalasi', 'data': data}), 200
    return jsonify({'status': False, 'message': 'Gagal mengambil data'}), 400

@app.route('/update/<status>', methods=['POST'])
def update_status(status):
    id_history = request.args['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM history WHERE id = %s', (id_history,))
    data_history = cursor.fetchone()

    if data_history:
        if request.method == 'POST' and status == 'perbaikan':
            # tgl_perbaikan = request.args['tgl_perbaikan']
            # foto_perbaikan = request.args['foto_perbaikan']
            # suhu_perbaikan = request.args['suhu_perbaikan']
            query_update_status_akhir = f"UPDATE history SET status_akhir = '{status}' WHERE id = {id_history}"
            print(query_update_status_akhir)
            cursor.execute(query_update_status_akhir)
            mysql.connection.commit()
            # cursor.execute('INSERT INTO history (id_instalasi, status, suhu_perbaikan, tgl_perbaikan, prediksi, status_akhir, progres) VALUES (%s, %s, %s, %s, %s, %s, %s)', (data_history['id_instalasi'], 'Aman', suhu_perbaikan, tgl_perbaikan, data_history['prediksi'], 'Aman', '4'))
            # query_masukkan_history = f"INSERT INTO history (id_instalasi, status, suhu_perbaikan, tgl_perbaikan, prediksi, status_akhir, progres) VALUES ({data_history['id_instalasi']}, 'Aman', '{suhu_perbaikan}', '{tgl_perbaikan}', '{data_history['prediksi']}', 'Aman', '4')"
            # print(query_masukkan_history)
            # cursor.execute(query_masukkan_history)

            mysql.connection.commit()
            return jsonify({'status': True, 'message': 'Berhasil update data history'}), 200
        elif request.method == 'POST' and status == 'progres':
            progres = request.args['progres']
            cursor.execute('UPDATE history SET progres = %s WHERE id = %s', (progres, id_history,))
            mysql.connection.commit()
            return jsonify({'status': True, 'message': 'Berhasil update data history'}), 200
        
        elif request.method == 'POST' and status == 'suhu_perbaikan':
            suhu_perbaikan = request.args['suhu_perbaikan']
            query_update_suhu_perbaikan = f"UPDATE history SET suhu_perbaikan = '{suhu_perbaikan}' WHERE id = {id_history}"
            cursor.execute(query_update_suhu_perbaikan)
            mysql.connection.commit()
            return jsonify({'status': True, 'message': 'Berhasil update data suhu_perbaikan'}), 200
            
        elif request.method == 'POST' and status == 'foto_perbaikan':

            # begin 
            latest_record = id_history
            # source = app.config['UPLOAD_FOLDER']
            destination = f'./static/images/{latest_record}'

            file = request.files['foto_perbaikan']
           
            foto_perbaikan_path = destination + 'foto_perbaikan.jpeg'
            file.save(foto_perbaikan_path)
        
           
            # Construct the SQL query using f-strings
            query_update_foto_perbaikan = f"UPDATE history SET foto_perbaikan = '{foto_perbaikan_path}' WHERE id = {id_history}"
            print(query_update_foto_perbaikan)
            cursor.execute(query_update_foto_perbaikan)
            mysql.connection.commit()
            # end code
            return jsonify({'status': True, 'message': 'Berhasil update data foto_perbaikan'}), 200
        
        elif request.method == 'POST' and status == 'tgl_perbaikan':
            tgl_perbaikan = request.args['tgl_perbaikan']
            query_update_tgl_perbaikan = f"UPDATE history SET tgl_perbaikan ='{tgl_perbaikan}', status_akhir='Aman' WHERE id = {id_history}"
            print(query_update_tgl_perbaikan)
            cursor.execute(query_update_tgl_perbaikan)
            mysql.connection.commit()
            return jsonify({'status': True, 'message': 'Berhasil update data tgl_perbaikan'}), 200

    else:
        return jsonify({'status': False, 'message': 'Id tidak ditemukan'}), 400
    return jsonify({'status': False, 'message': 'Gagal update data'}), 400

@app.route('/riwayat')
def riwayat():
    return render_template('riwayat data.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)