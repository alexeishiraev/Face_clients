import pytest

'''
тесты на загрузку файлов с нужным расширением:
- .jpeg
- .jpg
- .tiff
- .bmp
- ...
'''

# декоратор для проверки разных вариантов входящих файлов
@pytest.mark.parametrize("filename, expected", [
    ("image.jpeg", True),
    ("photo.png", True),
    ("scan.tiff", True),
    ("picture.jpg", True),
    ("document.pdf", False),
    ("archive.zip", False),
    ("graphic.bmp", False),
])

def test_img_extension (filename, expected):
    valid_extensions = {"jpeg", "png", "tiff", "jpg"}
    #разбиваем название файла, отделяем расширение
    ext = filename.split(".")[-1].lower()
    assert (ext in valid_extensions) == expected, f"Extension {ext} validity check failed"



