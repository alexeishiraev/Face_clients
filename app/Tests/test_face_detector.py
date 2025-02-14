import pytest
import cv2
import numpy as np
from app.face_detector import FaceDetectorHaar  # Импортируем класс из face_detector.py


'''
тесты на работу распознавания лиц
1. тест на загрузку каскадов Хаара
2. тест на то, что в случае отсутствия лиц. программа не крашится
3. 
'''

@pytest.fixture
def haar_model():
    """Фикстура для создания экземпляра FaceDetectorHaar"""
    return FaceDetectorHaar("../static/haarcascade_frontalface_alt.xml")


def test_haar_import(haar_model):
    """Проверяем, что каскад загружается корректно"""
    assert haar_model.face_cascade is not None, 'Каскад Хаара не загрузился'

def test_faces_none(haar_model):
    """ Проверяем, найдены ли лица, и если нет, то просто выводим сообщение"""
    #сначала создадим пустую np картинку
    empty_img = np.zeros((500, 500, 3), dtype=np.uint8)
    #проверяем наличие лиц на пустой картинке
    faces, _ = haar_model.detect_faces(empty_img)
    assert len(faces) == 0, 'Найдено лицо на пустой картинке'



