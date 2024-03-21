from pydicom.pixel_data_handlers.util import apply_voi_lut, apply_color_lut, apply_modality_lut
import gdcm #Для работы с DICOM-файлами, у которых было использовано сжатие массива пикселей
from PIL import Image
import numpy as np
import load_data
import tqdm

# PyTorch
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
from PIL import Image


model = torch.load(r"itog_201_epochs_86ac.pt")

if torch.cuda.is_available():
    device = torch.device("cuda:0")
else:
    device = torch.device("cpu")

BATCH_SIZE = 16
IMAGE_SIZE = (180, 180)
BASE = r"M:\all_mosmed_datasets"
STATIC_FOLDER = 'static'
UPLOAD_FOLDER = STATIC_FOLDER + '/uploads'
UPLOAD_FOLDER_DCM_SERIE = UPLOAD_FOLDER + '/buf_dcm_serie'
UPLOAD_FOLDER_IMGS = UPLOAD_FOLDER + '/buf_img/'

class MyDataSet(): 
    def __init__(self, x_tensor, y_tensor): 
        self.x = x_tensor
        self.y = y_tensor
        self.n_samples = len(x_tensor)

      
    def __getitem__(self, index): 
        return self.x[index], self.y[index] 
        
    # Чтобы можно было использовать len(dataset) для получения размера
    def __len__(self): 
        return self.n_samples 

def get_predictions(dataloader):
    y_pred_list = []
    y_true_list = []

    with torch.no_grad():
        for x_batch, y_batch in tqdm.tqdm(dataloader, leave=False):
            x_batch = x_batch.unsqueeze(1)
            x_batch = torch.cat((x_batch, x_batch, x_batch), 1)
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)
            y_test_pred = model(x_batch)
            y_test_pred = torch.log_softmax(y_test_pred, dim=1)
            _, y_pred_tag = torch.max(y_test_pred, dim = 1)
            y_pred_list.append(y_pred_tag.cpu().numpy())
            y_true_list.append(y_batch.cpu().numpy())

    return y_true_list, y_pred_list

def apply_voi_lut_array(ds_list):
    ds_list_lut = [load_data.resize_and_voi_lut(x) for x in ds_list]
    return ds_list_lut

def get_predict_for_lut_serie(ds_list_lut, filename):
    pathologies_x_test = np.array(ds_list_lut)
    pathologies_x_test = (pathologies_x_test - pathologies_x_test.min()) / (pathologies_x_test.max() - pathologies_x_test.min())

    tensor_x_test = torch.Tensor(pathologies_x_test)

    buf_y = np.arange(1, len(tensor_x_test)+1, 1)
    buf_y_tensor = torch.Tensor(buf_y)

    test_data = list(MyDataSet(tensor_x_test, buf_y_tensor))
    testloader = DataLoader(test_data, batch_size=1)

    _, y_pred_list = get_predictions(testloader)

    # Создадим полосу, которая укажет области, на которых были выявлены признаки патологии
    y_pred_list = np.concatenate(y_pred_list).ravel().reshape(len(y_pred_list),1).astype(np.uint8)
    
    img = Image.new('RGB', (len(y_pred_list),20))
    colors = [(0, 255, 0) if pixel == 0 else (255, 0, 0) for pixel in np.concatenate(y_pred_list).ravel().tolist()]

    for i in range(len(y_pred_list)):
        for j in range(20):
            img.putpixel((i, j), colors[i])
    
    img.save(UPLOAD_FOLDER_IMGS + filename + 'sag_map' + '.jpg')

    return f'Вероятность наличия остеопороза: {y_pred_list.mean()*100}%', UPLOAD_FOLDER_IMGS + filename + 'sag_map' + '.jpg'


def get_predict_for_serie_path(path: str, filename):
    dcm_serie = load_data.get_dcm_serie(path)
    dcm_serie = apply_voi_lut_array(dcm_serie)
    return get_predict_for_lut_serie(dcm_serie, filename)