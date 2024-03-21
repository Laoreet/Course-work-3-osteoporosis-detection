from flask import Flask, render_template
from flask import request
from matplotlib.pyplot import imread
import os, shutil
import predict
import load_data

app = Flask(__name__)

# Пути к файлам, которые будут обрабатываться и выводиться
STATIC_FOLDER = 'static'
UPLOAD_FOLDER = STATIC_FOLDER + '/uploads'
UPLOAD_FOLDER_DCM_SERIE = UPLOAD_FOLDER + '/buf_dcm_serie'


@app.route('/about')
def about() -> str:
    return '''Курсовая работа, 3 курс, НИУ ВШЭ - ПЕРМЬ, Программная инженерия, 2024 год. \n 
    Информационная система диагностики остеопороза по КТ снимкам позвоночника. \n 
    Работу выполнил Кирьянов Сергей Вячеславович.'''

@app.route('/', methods=['GET'])
def index():
    load_data.clear_dcm_data(UPLOAD_FOLDER+"/buf_img")
    load_data.clear_dcm_data(UPLOAD_FOLDER_DCM_SERIE)
    return render_template('index.html')

@app.route('/predict', methods= ['GET', 'POST'])
def upload_data():
    if request.method == "POST":
        files = request.files.getlist("file[]")
        for file in files:
            fullname = os.path.join(UPLOAD_FOLDER_DCM_SERIE, file.filename)
            file.save(fullname)
        try:
            img_paths = load_data.get_proections(load_data.get_dcm_serie(UPLOAD_FOLDER_DCM_SERIE), files[0].filename)
            # Получаем прогноз от модели
            pred  = predict.get_predict_for_serie_path(UPLOAD_FOLDER_DCM_SERIE, files[0].filename)
        except Exception as err:
            pred = 'Ошибка! Загрузите корректную серию КТ снимков формата DICOM', ''
            img_paths = ['','']
        load_data.clear_dcm_data(UPLOAD_FOLDER_DCM_SERIE)
        return [pred, img_paths]
    return None

if __name__ == "__main__":
    app.run(debug = True)

