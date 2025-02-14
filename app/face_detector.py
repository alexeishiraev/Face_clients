import os

import cv2
class FaceDetectorHaar:
    def __init__(self, cascade_path=None):
        """
  Инициализирует детектор лиц с использованием каскадов Хаара.

  cascade_path: Путь к файлу каскада Хаара.
  """

        if cascade_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cascade_path = os.path.join(base_dir, "static", "haarcascade_frontalface_alt.xml")

            # Проверка наличия файла
        if not os.path.exists(cascade_path):
            raise ValueError(f"Файл каскада Хаара не найден по пути: {cascade_path}")

            # Загрузка классификатора
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            raise ValueError(f"Не удалось загрузить каскадный классификатор из файла: {cascade_path}")


    def detect_faces(self, image):
            """
      Обнаруживает лица на изображении.

          image: Изображение в формате numpy array.
          return: список прямоугольников, изображение с отрисованными прямоугольниками
      """
            grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Ищем лица на изображении
            faces = self.face_cascade.detectMultiScale(
                grayscale_image,  # Изображение в оттенках серого
                scaleFactor=1.1,  # На сколько уменьшать размер окна на каждом шаге
                minNeighbors=5,  # Сколько соседей должно быть у прямоугольника
                minSize=(30, 30)  # Минимальный размер объекта
            )

            # Рисуем прямоугольники вокруг обнаруженных лиц
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

            return faces, image


