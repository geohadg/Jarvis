import os
from ollama import generate
from pathlib import Path
import sys
import pytesseract
from pdf2image import convert_from_path
import cv2
from PIL import Image
from commonfunctions import getaisummary, getfilelist

def getpdffilecontents(filepath: str) -> str:
    completetext = ''
    """
    reader = PdfReader(filepath)   # This code works but the parser fales to detect spaces and ends up merging words
    
    for page in reader.pages:
        text += page.extract_text()   # This is why i resorted to computer vision
    """
    images = convert_from_path(filepath, poppler_path="C:\\Users\\geoha\\Downloads\\Release-24.08.0-0\\poppler-24.08.0\\Library\\bin") # converts pdf pages to images
    numberofpages = len(images)
    for image in images:
        text = pytesseract.image_to_string(image) # extracts text from each image and adds it to a string
        # print(text)
        completetext += text

    return completetext, filepath, numberofpages

def getimgfilecontents(filepath: str) -> str:
    if Path(filepath).is_file():
        image = cv2.imread(filepath) # reads img file into an image object
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)   # converting image to grayscale can help recognition accuracy 
        text = pytesseract.image_to_string(Image.fromarray(gray))  

    elif Path(filepath).is_dir():
        text = ''
        files = getfilelist(filepath)

        for file in files:
            image = cv2.imread(file) # reads img file into an image object
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)   # converting image to grayscale can help recognition accuracy 
            text += pytesseract.image_to_string(Image.fromarray(gray))  

    print(text)
    return text

if __name__ == "__main__":
    try:
        file = Path(sys.argv[1])
        if str(file).endswith(".pdf"):
            text = getpdffilecontents(file)[0]

        else:
            text = getimgfilecontents(file)

        if "summarize" in sys.argv:
            getaisummary(text, file)

    except Exception as e:
        print(f"Error Occured: {e}")