import os
import numpy as np
import librosa
import soundfile as sf
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Function to extract features
def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=22050)
    mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
    chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr).T, axis=0)
    mel = np.mean(librosa.feature.melspectrogram(y=y, sr=sr).T, axis=0)
    contrast = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr).T, axis=0)
    return np.hstack([mfccs, chroma, mel, contrast])

# Load dataset
DATASET_PATH = "./ravdess"
X, y = [], []

for subdir, dirs, files in os.walk(DATASET_PATH):
    for file in files:
        if file.endswith(".wav"):
            emotion_label = file.split("-")[2]  # Extract emotion from filename
            file_path = os.path.join(subdir, file)
            features = extract_features(file_path)
            X.append(features)
            y.append(emotion_label)

X = np.array(X)
y = np.array(y)

# Encode labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Feature extraction completed successfully!")
