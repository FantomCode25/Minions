# app/model.py

import tensorflow as tf

class SimpleModel:
    def __init__(self):
        # Define a simple feedforward neural network
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),  # Adjust input shape as needed
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1)  # Output layer
        ])
        self.model.compile(optimizer='adam', loss='mean_squared_error')

    def train(self, x_train, y_train, epochs=10, batch_size=32):
        self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)

    def predict(self, x):
        return self.model.predict(x)

    def save(self, filepath):
        self.model.save(filepath)

    def load(self, filepath):
        self.model = tf.keras.models.load_model(filepath)