import pydicom
import pydicom.data
from pydicom.pixel_data_handlers.util import apply_voi_lut, apply_color_lut, apply_modality_lut
import gdcm #Для работы с DICOM-файлами, у которых было использовано сжатие массива пикселей
import cv2
from PIL import Image
import numpy as np


import os, shutil

from glob import glob
from PIL import Image, ImageColor

IMAGE_SIZE = (180, 180)

STATIC_FOLDER = 'static'
UPLOAD_FOLDER = STATIC_FOLDER + '/uploads'
UPLOAD_FOLDER_DCM_SERIE = UPLOAD_FOLDER + '/buf_dcm_serie'
UPLOAD_FOLDER_IMGS = UPLOAD_FOLDER + '/buf_img/'

image_format = '.jpg'

#Получение серии снимков из указанной директории
def get_dcm_serie(path_to_dcm_serie : str):
    ds_list = []
    dcm_files = os.listdir(path_to_dcm_serie)
    for file in dcm_files:
        buf_ds_file = pydicom.dcmread(path_to_dcm_serie+'/'+file)
        #Проверяем, аксиальная ли проекция у снимка (иногда в датасетах появляются сагитальные и корональные снимки)
        if ("ImageType" in buf_ds_file) == False:
            ds_list.append(buf_ds_file)
        elif buf_ds_file.ImageType[-1] == 'AXIAL':
            ds_list.append(buf_ds_file)
    ds_list = sorted(ds_list, key=lambda s: s.ImagePositionPatient[2])
    return ds_list

def get_dcm_file_save_img(path, filename):
    dcm_file = pydicom.dcmread(path)
    px_ar = np.array(dcm_file.pixel_array)
    #image_path = image_path.replace(UPLOAD_FOLDER, image_format)
    im = Image.fromarray(np.dstack([px_ar, px_ar, px_ar]))
    im = ImageColor.getrgb('red')
    im.save(UPLOAD_FOLDER_IMGS + filename + image_format)
    #cv2.imwrite(UPLOAD_FOLDER_IMGS + filename + image_format, dcm_file.pixel_array)
    return UPLOAD_FOLDER_IMGS + filename + image_format

# Функция для вывода нескольких проекций (аксиальной, сагитальной, корональной)
def get_proections(ds_list, filename):
    #ds_list = sorted(ds_list, key=lambda s: s.ImagePositionPatient[2])

    # Создаем трехмерный массив
    img_shape = list(ds_list[0].pixel_array.shape)
    img_shape.append(len(ds_list))
    img3d=np.zeros(img_shape)
    #print(ds_list[0].pixel_array.shape)

    # Заполняем трехмерный массив нашими снимками (срезами)
    for i, s in enumerate(ds_list):
        img2d = s.pixel_array
        img3d[:,:,i] = img2d

    cv2.imwrite(UPLOAD_FOLDER_IMGS + filename +'axial' + image_format, img3d[:,:,img_shape[2]//2])
    cv2.imwrite(UPLOAD_FOLDER_IMGS + filename + 'sagital' +  image_format, img3d[:,img_shape[1]//2,:])
    cv2.imwrite(UPLOAD_FOLDER_IMGS + filename + 'coronal' + image_format, img3d[img_shape[0]//2,:,:].T)

    axial = UPLOAD_FOLDER_IMGS + filename + 'axial' + image_format
    sagital = UPLOAD_FOLDER_IMGS + filename + 'sagital' + image_format
    coronal = UPLOAD_FOLDER_IMGS + filename + 'coronal' + image_format

    return [axial, sagital, coronal]

#Функция, которая увличивает контрастность изображений (костная ткань становится видна лучше) и изменяет их размер
def resize_and_voi_lut(dcm_file):
    buf_pixel_array = apply_voi_lut(dcm_file.pixel_array, dcm_file)
    resized_array = cv2.resize(buf_pixel_array, IMAGE_SIZE, interpolation = cv2.INTER_NEAREST)
    return resized_array

def clear_dcm_data(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Не удалось удалить файлы %s. Причина: %s' % (file_path, e))