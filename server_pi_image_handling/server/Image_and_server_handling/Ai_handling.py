#help from https://colab.research.google.com/github/roboflow-ai/notebooks/blob/main/notebooks/train-huggingface-detr-on-custom-dataset.ipynb?ref=blog.roboflow.com#scrollTo=jbzTzHJW22up

import matplotlib.pyplot as plt
from transformers import DetrForObjectDetection
import torch
from transformers import DetrImageProcessor
import cv2
import matplotlib.pyplot as plt
import supervision as sv
import numpy as np

class Ai():
    def __init__(self,Confidence=0.5):
        self.image_processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        self.model = DetrForObjectDetection.from_pretrained("Image_and_server_handling//custom-model")
        self.Device = torch.device("cuda")
        self.model.to(self.Device)
        self.model.eval()
        self.box_annotator = sv.BoxAnnotator()
        self.Confidence=Confidence

    def __Ai_Estimation_detection(self,image_location): #helped
        image = cv2.imread(image_location)
        with torch.no_grad():
            # load image and predict
            inputs = self.image_processor(images=image, return_tensors='pt').to(self.Device)
            outputs = self.model(**inputs)
            # post-process
            target_sizes = torch.tensor([image.shape[:2]]).to(self.Device)
            results = self.image_processor.post_process_object_detection(
                outputs=outputs, 
                threshold=self.Confidence, 
                target_sizes=target_sizes
            )[0]
            detections = sv.Detections.from_transformers(transformers_results=results)
            return detections.xyxy, detections.confidence, detections.class_id
        
    def __largest_probability_position(self,length,prob):
        largest_prob=0
        for position in range(length):
            if prob[position]>largest_prob:
                largest_prob=prob[position]
                largest_pos=position
        return largest_pos
    
    def find_rabbits(self,image_location):
        xyxy,confidence,class_id=self.__Ai_Estimation_detection(image_location)
        position=0
        cinny_pos=[]
        cleo_pos=[]
        cinny_prob=[]
        cleo_prob=[]
        base_array=np.array([0,0,0,0])
        human_flag=False
        for id in class_id:
            if id==1:
                cinny_pos.append(position)
                cinny_prob.append(confidence[position])
            elif id==2:
                cleo_pos.append(position)
                cleo_prob.append(confidence[position])
            elif id==3:
                human_flag=True
            position+=1
        len_cinny=len(cinny_pos)
        len_cleo=len(cleo_pos)
        match len_cinny,len_cleo:
            case 0,0:
                return base_array,base_array,human_flag
            case 1,1:
                return xyxy[cinny_pos[0]],xyxy[cleo_pos[0]],human_flag
            case 1,0:
                return xyxy[cinny_pos[0]],base_array,human_flag
            case 0,1:
                return base_array,xyxy[cleo_pos[0]],human_flag
            case _ if len_cinny>1 and len_cleo>1:
                largest_cinny_pos=self.__largest_probability_position(len_cinny,cinny_prob)
                largest_cleo_pos=self.__largest_probability_position(len_cleo,cleo_prob)
                return xyxy[cinny_pos[largest_cinny_pos]],xyxy[cleo_pos[largest_cleo_pos]],human_flag
            case _ if len_cinny>1 and len_cleo==1:
                largest_cinny_pos=self.__largest_probability_position(len_cinny,cinny_prob)
                return xyxy[cinny_pos[largest_cinny_pos]],xyxy[cleo_pos[0]],human_flag
            case _ if len_cinny>1 and len_cleo==0:
                largest_cinny_pos=self.__largest_probability_position(len_cinny,cinny_prob)
                return xyxy[cinny_pos[largest_cinny_pos]],base_array,human_flag
            case _ if len_cinny==1 and len_cleo>1:
                largest_cleo_pos=self.__largest_probability_position(len_cleo,cleo_prob)
                return xyxy[cinny_pos[0]],xyxy[cleo_pos[largest_cleo_pos]],human_flag
            case _ if len_cinny==0 and len_cleo>1:
                largest_cleo_pos=self.__largest_probability_position(len_cleo,cleo_prob)
                return base_array,xyxy[cleo_pos[largest_cleo_pos]],human_flag
            
