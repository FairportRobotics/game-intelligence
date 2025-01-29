from PIL import Image
import os


def validation(source, destination, n=50):
    if not os.path.exists(destination):
        os.makedirs(destination)
    imageFiles = [f for f in os.listdir(source) if f.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    for i, imageFile in enumerate(imageFiles):
        if i % n == 0:
            imagePath = os.path.join(source, imageFile)
            image = Image.open(imagePath)
            destinationPath = os.path.join(destination, imageFile)
            image.save(destinationPath)

if __name__=="__main__":
    source = "C:/Users/pig04/Pictures/extractedFrames"
    destination = "C:/Users/pig04/Pictures/valid"
    validation(source, destination, 50)






