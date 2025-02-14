from facenet_pytorch import InceptionResnetV1, MTCNN
from PIL import Image
from torch.nn.functional import cosine_similarity
import torch

class FaceNetVerify:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FaceNetVerify, cls).__new__(cls, *args, **kwargs)
            cls._instance.mtcnn = MTCNN(image_size=160, margin=0)
            cls._instance.resnet = InceptionResnetV1(pretrained="vggface2").eval()
        return cls._instance


    def verify_faces(self, img1_path, img2_path, thr = 0.5):
        """
        Сравнивает два изображения лиц и определяет, совпадают ли они.

        :param img1_path: Путь к первому изображению (фото из камеры).
        :param img2_path: Путь ко второму изображению (фото из базы).
        : thr = пороговое значение, выше которого считается, что лицо на одном изображении есть и на другом
        :return: True, если лица совпадают, False в противном случае.
        """
        try:
            # Загрузка изображений
            img1 = Image.open(img1_path)
            img2 = Image.open(img2_path)

            # Детектирование и вырезание лиц
            face1 = self.mtcnn(img1)
            face2 = self.mtcnn(img2)
            # Проверка, найдены ли лица на обоих изображениях
            if face1 is None or face2 is None:
                print("Лицо не найдено на одном из изображений.")
                return False

            # Получение эмбеддингов
            embedding1 = self.resnet(face1.unsqueeze(0))
            embedding2 = self.resnet(face2.unsqueeze(0))

            # Сравнение (например, косинусное расстояние)

            similarity = cosine_similarity(embedding1, embedding2)
            is_match = False
            print(similarity.item())

            if (similarity.item() > thr):
                is_match = True

            return is_match
        except Exception as e:
            print(f"Ошибка при сравнении лиц: {e}")
            return False

# Пример использования
if __name__ == "__main__":
    face_recognizer = FaceNetVerify()

   # Проверяем, совпадают ли лица на двух фото
    is_match = face_recognizer.verify_faces("test_image.jpg", "temp_captured.jpg")
    print(f"Совпадение: {is_match}")
