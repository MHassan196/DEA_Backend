# import argparse
# import io
# from typing import List
# import cv2
# import matplotlib.pyplot as plt
# from path import Path
# import os
# from word_detector import detect, prepare_img, sort_multiline
# import pandas as pd
# from tqdm import tqdm
# from mltu.configs import BaseModelConfigs
# import numpy as np
# from PIL import Image as im
# import typing
# import numpy as np
# from mltu.inferenceModel import OnnxInferenceModel
# from mltu.utils.text_utils import ctc_decoder, get_cer, get_wer
# from mltu.transformers import ImageResizer
# from PIL import Image

# import warnings


# # Ignore all warnings
# warnings.simplefilter("ignore")

# output_folder = 'output_images'
# os.makedirs(output_folder, exist_ok=True)

# list_img_names_serial = []

# def process_image(image_data: np.ndarray, kernel_size: int, sigma: float, theta: float, min_area: int, img_height: int):
#     # Convert the bytes to an image using PIL
#     img = Image.open(io.BytesIO(image_data))

#     # Convert the PIL image to a NumPy array
#     img_array = np.array(img)
#     # Load image and process it
#     img = prepare_img(img_array, img_height)
#     detections = detect(img, kernel_size=kernel_size, sigma=sigma, theta=theta, min_area=min_area)
#     # Sort detections: cluster into lines, then sort each line
#     lines = sort_multiline(detections)
#     # Plot results
#     plt.imshow(img, cmap='gray')
#     num_colors = 7
#     colors = plt.cm.get_cmap('rainbow', num_colors)
#     for line_idx, line in enumerate(lines):
#         for word_idx, det in enumerate(line):
#             xs = [det.bbox.x, det.bbox.x, det.bbox.x + det.bbox.w, det.bbox.x + det.bbox.w, det.bbox.x]
#             ys = [det.bbox.y, det.bbox.y + det.bbox.h, det.bbox.y + det.bbox.h, det.bbox.y, det.bbox.y]
#             plt.plot(xs, ys, c=colors(line_idx % num_colors))
#             plt.text(det.bbox.x, det.bbox.y, f'{line_idx}/{word_idx}')
#             crop_img = img[det.bbox.y:det.bbox.y+det.bbox.h, det.bbox.x:det.bbox.x+det.bbox.w]
#             image_filename = f"line{line_idx}word{word_idx}.jpg"
#             image_path = os.path.join(output_folder, image_filename)                 
#             cv2.imwrite(image_path, crop_img)
#             full_img_path = f"line{line_idx}word{word_idx}.jpg"
#             list_img_names_serial.append(f"./{output_folder}/{full_img_path}")

# def save_image_names_to_text_file(image_path):
#     parser = argparse.ArgumentParser()
#     process_image(image_path,25,11,5, 100,1000)
#     list_img_names_serial_set = set(list_img_names_serial)
#     textfile = open("img_names_sequence.txt", "w")
#     for element in list_img_names_serial_set:
#         textfile.write(element + "\n")
#     textfile.close()

# class ImageToWordModel(OnnxInferenceModel):
#     def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.char_list = char_list

#     def predict(self, image: np.ndarray):
#         if image is None:
#             raise ValueError("Unable to load the image.")
        
#          # Ensure the input image has the correct shape (H, W, C)
#         if len(image.shape) == 2:
#             image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

#         # image = ImageResizer.resize_maintaining_aspect_ratio(image, *self.input_shape[:2][::-1])
#         # Resize the image using OpenCV
#         height, width = self.input_shape[2:4]
#         image = cv2.resize(image, (width, height))
#         # # Check if the image is grayscale and convert it to RGB
#         # if image.shape[-1] == 1:
#         #     image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB) 

#         # Add batch dimension if the model expects it
#         if len(self.input_shape) == 4:
#             image = np.expand_dims(image, axis=0)

#         image_pred = np.expand_dims(image, axis=0).astype(np.float32)

#         preds = self.model.run(None, {self.input_name: image_pred})[0]

#         text = ctc_decoder(preds, self.char_list)[0]

#         return text


#     # Open the file in read mode ('r')
# def process_images(image_data,model):
#     # Open the file in read mode ('r')
#     # with open(file_path, 'rb') as file:
#     #     paths = file.readlines()
#     with io.BytesIO(image_data) as file:
#         img = Image.open(file)
#         img_array = np.array(img)
    
#     # Define a function to extract line and word indices from the file paths
#     def extract_indices(path):
#         filename = os.path.basename(path)
#         parts = filename.replace('.jpg', '').split('line')[1].split('word')
#         if len(parts) == 2:
#             line_idx, word_idx = map(int, parts)
#             return line_idx, word_idx
#         return -1, -1  # Default values if unable to extract indices
    
#     # Get a list of image paths
#     list_img_names_serial = ["line{}word{}.jpg".format(line, word) for line in range(img_array.shape[0]) for word in range(img_array.shape[1])]


#     # Sort the file paths based on the extracted indices
#     sorted_paths = sorted(list_img_names_serial, key=extract_indices)

#     current_line = None
#     result = []

#     for image_path in sorted_paths:
#         # Read the image and perform predictions
#         row, col = extract_indices(image_path)
#         image = img_array[row, col]

#         if image is not None:
#             # Assuming 'model' is defined and can perform predictions
#             prediction_text = model.predict(image)
            
#             # Extract line index from the image path
#             # line_idx, _ = extract_indices(image_path)
            
#             # Check if it's a new line
#             if row != current_line:
#                 # Print a line break if it's not the first line
#                 if current_line is not None:
#                     result.append('\n')
#                 # Print the line index
#                 # result.append("")
#                 current_line = row

#             # Append the word prediction to the result
#             result.append(prediction_text + ' ')
#         else:
#             result.append(f"Failed to read image: {image_path}")

#     return ''.join(result)
# if __name__ == "__main__":

#     image_path=input("Enter image path: ")
#     save_image_names_to_text_file(image_path)
    
#     configs = BaseModelConfigs.load("D:/Hassan/FYP/model/configs.yaml")
#     model_path = "D:/Hassan/FYP/model/model.onnx"
#     model = ImageToWordModel(model_path=model_path, char_list=configs.vocab)
  
#     file_path = 'img_names_sequence.txt'
#     formatted_output = process_images(file_path,model)

#     # Print or use the formatted output as needed
#     print(formatted_output)


import argparse
from typing import List
import cv2
import matplotlib.pyplot as plt
from path import Path
import os
from word_detector import detect, prepare_img, sort_multiline
import pandas as pd
from tqdm import tqdm
from mltu.configs import BaseModelConfigs 
import numpy as np
from PIL import Image as im
import typing
import numpy as np
from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder, get_cer, get_wer
from mltu.transformers import ImageResizer

import warnings


# Ignore all warnings
warnings.simplefilter("ignore")

output_folder = 'output_images'
os.makedirs(output_folder, exist_ok=True)

list_img_names_serial = []

def process_image(image_data: bytes, kernel_size: int, sigma: float, theta: float, min_area: int, img_height: int):
     # Convert the image data to a NumPy array
    nparr = np.frombuffer(image_data, np.uint8)
    
    # Load image and process it
    img = prepare_img(cv2.imdecode(nparr, cv2.IMREAD_COLOR), img_height)
    detections = detect(img, kernel_size=kernel_size, sigma=sigma, theta=theta, min_area=min_area)
    # Sort detections: cluster into lines, then sort each line
    lines = sort_multiline(detections)
    # Plot results
    plt.imshow(img, cmap='gray')
    num_colors = 7
    colors = plt.cm.get_cmap('rainbow', num_colors)
    for line_idx, line in enumerate(lines):
        for word_idx, det in enumerate(line):
            xs = [det.bbox.x, det.bbox.x, det.bbox.x + det.bbox.w, det.bbox.x + det.bbox.w, det.bbox.x]
            ys = [det.bbox.y, det.bbox.y + det.bbox.h, det.bbox.y + det.bbox.h, det.bbox.y, det.bbox.y]
            plt.plot(xs, ys, c=colors(line_idx % num_colors))
            plt.text(det.bbox.x, det.bbox.y, f'{line_idx}/{word_idx}')
            crop_img = img[det.bbox.y:det.bbox.y+det.bbox.h, det.bbox.x:det.bbox.x+det.bbox.w]
            image_filename = f"line{line_idx}word{word_idx}.jpg"
            image_path = os.path.join(output_folder, image_filename)                 
            cv2.imwrite(image_path, crop_img)
            full_img_path = f"line{line_idx}word{word_idx}.jpg"
            list_img_names_serial.append(f"./{output_folder}/{full_img_path}")

def save_image_names_to_text_file(image_path, output_file_path="img_names_sequence.txt"):
    process_image(image_path,25,11,5, 100,1000)
    list_img_names_serial_set = set(list_img_names_serial)
    with open(output_file_path, "w") as textfile:
        for element in list_img_names_serial_set:
            textfile.write(element + "\n")

class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, image: np.ndarray):
        if image is None:
            raise ValueError("Unable to load the image.")

        image = ImageResizer.resize_maintaining_aspect_ratio(image, *self.input_shape[:2][::-1])

        image_pred = np.expand_dims(image, axis=0).astype(np.float32)

        preds = self.model.run(None, {self.input_name: image_pred})[0]

        text = ctc_decoder(preds, self.char_list)[0]

        return text


    # Open the file in read mode ('r')
def process_images(file_path,model):
    # Open the file in read mode ('r')
    with open(file_path, 'r') as file:
        paths = file.readlines() 

    # Define a function to extract line and word indices from the file paths
    def extract_indices(path):
        filename = path.strip().split('/')[-1]
        parts = filename.replace('.jpg', '').split('line')[1].split('word')
        if len(parts) == 2:
            line_idx, word_idx = map(int, parts)
            return line_idx, word_idx
        return -1, -1  # Default values if unable to extract indices

    # Sort the file paths based on the extracted indices
    sorted_paths = sorted(paths, key=extract_indices)

    current_line = None
    result = []

    for image_path in sorted_paths:
        image_path = image_path.replace('\n', '')
        # Read the image and perform predictions
        image = cv2.imread(image_path)
        if image is not None:
            # Assuming 'model' is defined and can perform predictions
            prediction_text = model.predict(image)
            
            # Extract line index from the image path
            line_idx, _ = extract_indices(image_path)
            
            # Check if it's a new line
            if line_idx != current_line:
                # Print a line break if it's not the first line
                if current_line is not None:
                    result.append('\n')
                # Print the line index
                #result.append("")
                current_line = line_idx

            # Append the word prediction to the result
            result.append(prediction_text + ' ')
        else:
            result.append(f"Failed to read image: {image_path}")

    return ''.join(result)
if __name__ == "__main__":

    image_path=input("Enter image path: ")
    save_image_names_to_text_file(image_path)
    
    configs = BaseModelConfigs.load("D:/Hassan/FYP/model/configs.yaml")
    model_path = "D:/Hassan/FYP/model/model.onnx"
    model = ImageToWordModel(model_path=model_path, char_list=configs.vocab)
  
    file_path = 'img_names_sequence.txt'
    formatted_output = process_images(file_path,model)

    # Print or use the formatted output as needed
    print(formatted_output)