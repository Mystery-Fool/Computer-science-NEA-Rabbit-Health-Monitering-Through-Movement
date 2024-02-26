import matplotlib.pyplot as plt
from transformers import DetrForObjectDetection
import torch
from transformers import DetrImageProcessor
import cv2
import matplotlib.pyplot as plt
import supervision as sv
import numpy as np

class Ai():
    """
    Class for handling object detection.

    Args:
        Confidence (float, optional): The confidence threshold for a given object. Defaults to 0.5.

    Attributes:
        image_processor (DetrImageProcessor): The DetrImageProcessor class for image preprocessing.
        model (DetrForObjectDetection): The pretrained model for object detection.
        Device (torch.device): The GPU to run the model on.
        box_annotator (sv.BoxAnnotator): An instance of the BoxAnnotator class for drawing bounding boxes.
        Confidence (float): The confidence threshold for object detection. Defaults to 0.5.

    Methods:
        Private:
        __Ai_Estimation_detection(image_location): Performs object detection on the given image.
        __largest_probability_position(length, prob): Finds the position of the largest probability of an object in the given probability array.

        Public:
        find_rabbits(image_location): Finds the most likely bounding box coordinates for rabbits in the given image.
    """

    def __init__(self, Confidence=0.5):
        self.image_processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        self.model = DetrForObjectDetection.from_pretrained("Image_and_server_handling//custom-model")
        self.Device = torch.device("cuda")
        self.model.to(self.Device)
        self.model.eval()
        self.box_annotator = sv.BoxAnnotator()
        self.Confidence = Confidence

    def __Ai_Estimation_detection(self, image_location): # helped
        """
        Performs object detection on the given image.

        Args:
            image_location (str): The file path of the image.

        Returns:
            tuple: A tuple containing the bounding box coordinates in form (xyxy), confidence scores, and class IDs.
        """

        image = cv2.imread(image_location)
        with torch.no_grad(): #got from https://colab.research.google.com/github/roboflow-ai/notebooks/blob/main/notebooks/train-huggingface-detr-on-custom-dataset.ipynb?ref=blog.roboflow.com#scrollTo=jbzTzHJW22u
            # load image and predict
            inputs = self.image_processor(images=image, return_tensors='pt').to(self.Device)
            outputs = self.model(**inputs)
            # post-process
            target_sizes = torch.tensor([image.shape[:2]]).to(self.Device)
            results = self.image_processor.post_process_object_detection(
                outputs = outputs,
                threshold = self.Confidence,
                target_sizes=target_sizes
            )[0]
        detections = sv.Detections.from_transformers(transformers_results=results)
        return detections.xyxy, detections.confidence, detections.class_id

    def __largest_probability_position(self, length, prob):
        """
        Finds the position of the most probable object.

        Args:
            length (int): The length of the probability array.
            prob (list): The probability array.

        Returns:
            int: The position of the largest probability.
        """

        largest_prob = 0
        for position in range(length):
            if prob[position] > largest_prob:
                largest_prob = prob[position]
                largest_pos = position
        return largest_pos

    def find_rabbits(self, image_location):
        """
        Finds the most probable bounding box coordinates for rabbits in the image.

        Args:
            image_location (str): The file path of the image.

        Returns:
            tuple: The bounding box coordinates for Cinny, Cleo, and a flag indicating the presence of a human.
        """
        
        xyxy, confidence, class_id = self.__Ai_Estimation_detection(image_location)
        position = 0
        cinny_pos = []
        cleo_pos = []
        cinny_prob = []
        cleo_prob = []
        base_array = np.array([0, 0, 0, 0])
        human_flag = False
        for id in class_id:
            if id == 1:
                cinny_pos.append(position)
                cinny_prob.append(confidence[position])
            elif id == 2:
                cleo_pos.append(position)
                cleo_prob.append(confidence[position])
            elif id == 3:
                human_flag = True
            position += 1
        len_cinny = len(cinny_pos)
        len_cleo = len(cleo_pos)
        match len_cinny, len_cleo:
            case 0, 0:
                return base_array, base_array, human_flag
            case 1, 1:
                return xyxy[cinny_pos[0]], xyxy[cleo_pos[0]], human_flag
            case 1, 0:
                return xyxy[cinny_pos[0]], base_array, human_flag
            case 0, 1:
                return base_array, xyxy[cleo_pos[0]], human_flag
            case _ if len_cinny > 1 and len_cleo > 1:
                largest_cinny_pos = self.__largest_probability_position(len_cinny, cinny_prob)
                largest_cleo_pos = self.__largest_probability_position(len_cleo, cleo_prob)
                return xyxy[cinny_pos[largest_cinny_pos]], xyxy[cleo_pos[largest_cleo_pos]], human_flag
            case _ if len_cinny > 1 and len_cleo == 1:
                largest_cinny_pos = self.__largest_probability_position(len_cinny, cinny_prob)
                return xyxy[cinny_pos[largest_cinny_pos]], xyxy[cleo_pos[0]], human_flag
            case _ if len_cinny > 1 and len_cleo == 0:
                largest_cinny_pos = self.__largest_probability_position(len_cinny, cinny_prob)
                return xyxy[cinny_pos[largest_cinny_pos]], base_array, human_flag
            case _ if len_cinny == 1 and len_cleo > 1:
                largest_cleo_pos = self.__largest_probability_position(len_cleo, cleo_prob)
                return xyxy[cinny_pos[0]], xyxy[cleo_pos[largest_cleo_pos]], human_flag
            case _ if len_cinny == 0 and len_cleo > 1:
                largest_cleo_pos = self.__largest_probability_position(len_cleo, cleo_prob)
                return base_array, xyxy[cleo_pos[largest_cleo_pos]], human_flag
            
