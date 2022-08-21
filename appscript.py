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


admin = r"""{
  "type": "service_account",
  "project_id": "image-labeling-88825",
  "private_key_id": "fff2d984dd73b8f260018ba1a6d6097af3a2ba87",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC6wYJj9ZQNIamN\nJmZ6drf/5DhfEMLbsBGX66XT5xeH27s8NL1ECBSN7CpzKctOYMQ4Czk8aX/G5Gfg\nhG18A8IVl2Xt34JtrquOsfMXwmSjxw7RXnMCaU4wdlkB3lvVLVXzzqsUb7+FLwFM\nFgQjrJGG0BIyKoOo9SlBvy7tAamRtQwfw2QJ+voDywNLzg2b3bfs7BV076RJGkfl\nlH+KB6ql3f5X9iKcl9mO2BVxQS9OqwKpHMdwLhZqtqLaiY4K1V7Hr/922nNjVQkz\n9RHFZ8kHazy2EZtxG6B214TatlB0j0nnCBXXunpUy/evBZT/wmnzpkbf7tBjlLTz\nlyZhcbyBAgMBAAECggEABFgIHlo6ZB5VoCs6DfyQEHkn+hw6qWXyx5zfdx/jW9wv\nHBXS4yuCrYxoahh3EfdnGg+MPMRj1V1ywcKT2tIH9Se+L+Z5ohGLDFar31a0ODpW\nLHa5xeeNV7sHYKMMk9c7JZxRTrhqjpGXsTtVMrcXjbihUQ1VXk9mUOZYAxyoFjgg\n9xNdSGBxpwW43bDZoMIpVt6DmB7CiGMd4MwudQcZ3GkufFSgschUAGJt/0j036vM\nwGA8iHC3YkyyrMufIFMCAoRyE4Njd6S9SXhdrGGyOtf5EcFNUiBhAVi09Kf5H9/B\nQPNhVu0FZlfFNmX0hlng9VDpsuuSOUdbDb86OsQSewKBgQDdQPS/pvvB4Kymrtqb\nBLOS7574wtXhnTte62Sm6qWYNUAuNN9yCKFitKjJhPa77C7uRrqjqVvOdjohPR8H\nVXjj5Iovwvg040epiVJRwf2RXGaCWMpHW0IWdCbVdpqUXaxyNj9Fr3PniClLk8U4\nLbS4bj1kMv20GmlK7tQxxxR7FwKBgQDYFaPJHRLz6M2rUuBLOtbgFD/cvppb4pI8\nMa47sZERmSTi+ky4/ACk3vXNlgAjpI/QcL/ulUyafRLnunEsRXr9HpPUOLZaldl7\nLFwDOb+HQMew+j0k7GQwgZOy1CytaMPl4tMNrBYKXGPqYLR+bIoj1Quh2e6YYOLP\nD6tly3JkJwKBgQDY4b2IyLTsncJgOfKMFpW4qS8aBlMGL8xtBS3K+SSOCVT6dlW6\nQH+CdDkoITCDkceHRsnZeEBIKFhfEL0DwWMZcYOLwgDwRwKOS8/n2NMo1HyftU3D\nmM81l3IhuXtZiGFsK4TmWFCzWyOvtBCVOyh1yYpgWCOdkm44R9i1WsLWzQKBgHw+\nJQhT8TvRFcB2TIS09iutOPMBnNtMMOzvW9DyzgiiV3Uymb6bFvu1PvvQTZAw5Ifi\n7FiP+5WwaJhYuQ3NfWPgmvshCKiZFI0f+l/YammoM6lsmI+MZCcHuhbOrEmgvVKG\n0vc/hQS8Dq8Kn305h0wHCUMsfWWb/40y40gKbGFtAoGBAIf2vWDqErY2Q4SUno+1\nwM/UQZdY3aKHI83mJZJumY8T2L7p5pk6Iw+YwB+xz9Rf+uCrCTN2iaaynoBt+W4t\n3Rv3doq95/EGRAuCm+1H/u11nRzbrGEFcU/R3PCLmvAsgs/oag+J51F79ABvLXFV\nvAfPIh06ToiJJCLARa0hfcXk\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-nqidv@image-labeling-88825.iam.gserviceaccount.com",
  "client_id": "107531603737998454444",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-nqidv%40image-labeling-88825.iam.gserviceaccount.com"
}"""



cred = credentials.Certificate(json.loads(admin))
firebase_admin = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://image-labeling-88825-default-rtdb.firebaseio.com/'})

ref = db.reference('message')
ref1 = db.reference("output")
refRefresh = db.reference("refresh")


refRefresh.listen(lambda x: result(x.data))

