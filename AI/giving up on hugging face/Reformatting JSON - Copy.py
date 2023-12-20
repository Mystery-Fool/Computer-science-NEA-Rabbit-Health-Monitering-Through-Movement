'''#code eddited from https://huggingface.co/docs/transformers/tasks/object_detection to fit with my data set made by https://github.com/jsbroks/coco-annotator
import json
from PIL import Image, ImageDraw
import random
random.seed(42)
#jsonfile=open("Rabbit.json", "w")
oldjsonfile=open("Rabbits-JSON-COCO.json", "r")
olddata = json.load(oldjsonfile)
reformatted_json={}
reformatted_json["images"]=[]
#reformatted_json["categories"]=[]
random_images=[]
x=0
while True:
    num=random.randint(1,1000)
    if num not in random_images:
        x=x+1
        random_images.append(num)
        if x==50:
            break
random_images.sort()
def get_objects(id):
    anno_id_temp=[]
    bbox_temp=[]
    area_temp=[]
    category_id_temp=[]
    for x in olddata["annotations"]:
        if x["image_id"]==id:
            anno_id_temp.append(x["id"])
            bbox_temp.append(x["bbox"])
            area_temp.append(x["area"])
            category_id_temp.append(x["category_id"])
    temp={
        "id": anno_id_temp,
        "area": area_temp,
        "bbox": bbox_temp,
        "category": category_id_temp
    }
    return temp



for image in olddata["images"]:
    reformatted_json["images"].append({
    "id": image["id"],
    "image": Image.open(image["path"][1:]),#image["path"][1:],
    "width": image["width"],
    "height": image["height"],
    "objects": get_objects(image["id"])
    })

for category in olddata["categories"]:
    reformatted_json["categories"].append({
        "supercategory": "none",
        "id": category["id"],
        "name": category["name"]
    })
train=[]
test=[]
i=0
random_images.append(-1)
for images in reformatted_json["images"]:
    if random_images[i]==images["id"]:
        test.append(images)
        i=i+1
    else:
        train.append(images)
train=tuple(train)
test=tuple(test)
reformatted_json={
    "train": train,
    "test": test,
    "category": reformatted_json["categories"]
}'''
#json.dump(reformatted_json,jsonfile)



#end of my code:

from datasets import load_dataset, Dataset
#dataset = Dataset.from_dict(reformatted_json)
cppe5=load_dataset('json', data_files='Rabbits-JSON-COCO.json')
cppe5
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

image