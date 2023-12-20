from datasets import load_dataset
dataset = load_dataset("json", data_files="Rabbits-JSON-COCO.json")

import numpy as np
import os
from PIL import Image, ImageDraw
image=Image.open("datasets/Rabbits/00-00-00_2023-12-03.jpg")

annotations = dataset["train"][0]["annotations"]

draw = ImageDraw.Draw(image)

categories = dataset["categories"]

id2label = {index: x for index, x in enumerate(categories, start=0)}

label2id = {v: k for k, v in id2label.items()}

for i in range(len(annotations["id"])):

    box = annotations["bbox"][i]

    class_idx = annotations["categories"][i]

    x, y, w, h = tuple(box)

    draw.rectangle((x, y, x + w, y + h), outline="red", width=1)

    draw.text((x, y), id2label[class_idx], fill="white")