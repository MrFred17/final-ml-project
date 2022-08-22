import base64
import io
import json

import firebase_admin
from deep_translator import GoogleTranslator
from firebase_admin import credentials
from firebase_admin import db

import torch
from PIL import Image
import tensorflow as tf
from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer


model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTFeatureExtractor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}


def predict_step(image_paths):
    images = []
    for image_path in image_paths:
        i_image = Image.open(io.BytesIO(image_path))
        if i_image.mode != "RGB":
            i_image = i_image.convert(mode="RGB")

        images.append(i_image)

    pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    output_ids = model.generate(pixel_values, **gen_kwargs)

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds


def decode_and_resize(img_path):
    img = tf.io.read_file(img_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, (299, 299))
    img = tf.image.convert_image_dtype(img, tf.float32)
    return img


# from bs4 import BeautifulSoup
# import requests

# def translate_to_hebrew(english):
#     # MORFIX
#     words = english.split()
#     exact_format = ''.join([words[i] + '%20' for i in range(len(words))])[:-3]
#     url = f'https://www.morfix.co.il/{exact_format}'
#     result1 = requests.get(url)
#     doc = BeautifulSoup(result1.text, 'html.parser')
#     tag = doc.find_all(class_='MachineTranslation_divfootertop_enTohe')[0].decode_contents()
#     hebrew_mf = tag.strip()
#
#     # Formatting
#     SYMBOLS = ',:;+-!:?-'
#     if hebrew_mf[-1] in SYMBOLS:
#         hebrew_mf = hebrew_mf[-1] + hebrew_mf[:-1]
#
#     return hebrew_mf



def working_translate(english):
    # print(english)

    heb = GoogleTranslator(source='auto', target='iw').translate(english)
    if "sitting on top" in english:
        heb = heb.replace("יושבת", "מונחת").replace("יושב", "מונח")

    return heb


def predict(path):
    # get caption
    return predict_step([path])[0]


def result(data):
    refresh = data

    if refresh == "True":
        try:
            refRefresh.set("False")
            ref1.set("Processing...")

            b64 = ref.get()
            image_data = base64.b64decode(str(b64))

            captions = predict(image_data)

            # print(str(captions))
            #
            # tic1 = time.perf_counter()
            # print(working_translate(str(captions)))
            # print(str(time.perf_counter()-tic1) + " google translate")
            #
            # tic = time.perf_counter()
            # print(translate_to_hebrew(str(captions)))
            # print(str(time.perf_counter() - tic) + " mrofix")

            ref1.set(working_translate(str(captions)))

        except Exception as e:
            print(e)


admin = # hidden



cred = credentials.Certificate(json.loads(admin))
firebase_admin = firebase_admin.initialize_app(cred, {
    'databaseURL': #hidden
})

ref = db.reference('message')
ref1 = db.reference("output")
refRefresh = db.reference("refresh")


refRefresh.listen(lambda x: result(x.data))

