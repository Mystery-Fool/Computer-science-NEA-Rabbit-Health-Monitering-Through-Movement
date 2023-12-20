#code eddited from https://huggingface.co/docs/transformers/tasks/object_detection to fit with my data set made by https://github.com/jsbroks/coco-annotator
import json
from PIL import Image, ImageDraw
jsonfile=("Rabbit.json", "w")
oldjsonfile=open("Rabbits-JSON-COCO.json", "r")
olddata = json.load(oldjsonfile)
reformatted_json={}
reformatted_json["images"]=[]
reformatted_json["categories"]=[]
reformatted_json["annotations"]=[]
for category in olddata["categories"]:
    reformatted_json["categories"].append({
    "supercategory": "none",
    "id": category["id"],
    "name": category["name"]
    })
for image in olddata["images"]:
    reformatted_json["images"].append({
    "image_id": image["id"],
    "width": image["width"],
    "height": image["height"],
    "image": Image.open(image["path"][1:])
    })

for anno in olddata["annotations"]:
    reformatted_json["annotations"].append({
    "id": anno["id"],
    "category_id": anno["category_id"],
    "iscrowd": 0,
    "image_id": anno,
    "area": anno["area"],
    "bbox": anno["bbox"],
    })


from datasets import load_dataset, Dataset
dataset = Dataset.from_dict(reformatted_json,field='images')
cppe5=dataset


import numpy as np

import os

from PIL import Image, ImageDraw

image = cppe5["image"][0]["image"]

annotations = cppe5["train"][0]["objects"]

draw = ImageDraw.Draw(image)

categories = cppe5["train"].features["objects"].feature["category"].names

id2label = {index: x for index, x in enumerate(categories, start=0)}

label2id = {v: k for k, v in id2label.items()}

for i in range(len(annotations["id"])):

    box = annotations["bbox"][i]

    class_idx = annotations["category"][i]

    x, y, w, h = tuple(box)

    draw.rectangle((x, y, x + w, y + h), outline="red", width=1)

    draw.text((x, y), id2label[class_idx], fill="white")

