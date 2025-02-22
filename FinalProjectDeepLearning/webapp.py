#import libraries
import numpy as np
import pickle as pkl
from torchvision.models import resnet50
from sklearn.neighbors import NearestNeighbors

import scipy.io as sio
import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image
import torch.nn as nn
import zipfile
import torchvision.transforms as tf
import os
import streamlit as st

st.header('Fashion Recommendation System')

Image_features = pkl.load(open('Images_features.pkl','rb'))
filenames = pkl.load(open('filenames.pkl','rb'))

def extract_features_from_images(image_path, model, tr):

    img = Image.open(image_path)
    img = tr(img).unsqueeze(0)  # Add a batch dimension
    #display(tf.ToPILImage()(img.squeeze(0)))

    # Extract features using the model
    with torch.no_grad():
        features = model(img)

    # Flatten the features tensor
    flattened_features = features.flatten()

    # Normalize the features
    norm_features = flattened_features / torch.norm(flattened_features)

    return norm_features


model = resnet50(pretrained=True)

# Remove the fully connected layer (classification layer)
modules = list(model.children())[:-1]
model = torch.nn.Sequential(*modules)

# Set the model to evaluation mode
model.eval()

# Set all parameters to be non-trainable
for param in model.parameters():
    param.requires_grad = False


neighbors = NearestNeighbors(n_neighbors=6, algorithm='brute', metric='euclidean')
neighbors.fit(Image_features)

tr = tf.Compose([
    tf.Resize((224, 224)),
    tf.Grayscale(num_output_channels=3),  # Convert to 3 channels (RGB)
    tf.ToTensor(),  # Converts an image loaded in range [0, 255] to a torch.Tensor in range [0.0, 1.0]
    tf.Normalize(mean= [0.485, 0.456, 0.406] , std=[0.229, 0.224, 0.225]),  # Normalizes using imageNet mean, std values
    ])

upload_file = st.file_uploader("Upload Image")
if upload_file is not None:
    with open(os.path.join('upload/', upload_file.name), 'wb') as f:
        f.write(upload_file.getbuffer())
    st.subheader('Upload image')
    st.image(upload_file)

    input_img_features = extract_features_from_images('upload/'+ upload_file.name, model, tr)
    distance, indices = neighbors.kneighbors([input_img_features])
    st.subheader('Recommended Images')
    col1, col2, col3, col4, col5 = st.colums(5)
    with col1:
        st.image(filenames[indices][0][1])
    with col2:
        st.image(filenames[indices][0][2])
    with col3:
        st.image(filenames[indices][0][3])
    with col4:
        st.image(filenames[indices][0][4])
    with col5:
        st.image(filenames[indices][0][5])