# Importing modules
import os

import cv2
import numpy as np
import pandas as pd
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.layers import Dense, Conv2D, Flatten, MaxPooling2D
from keras.models import Sequential
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
import tensorflow as tf

from AWS_CRUD import conn_AWS, read_images_from_s3, DownloadWeatherImages

np.random.seed(1)

def GetTrainingData(dowload=True):
    aws_folder = 'weather/updated_dataset'
    local_folder = 'weather_data'
    s3, bucket_name = conn_AWS()


    print('Getting images from S3...')

    if os.path.isdir(local_folder):
        print('weather_data directory already exists.')
    elif dowload:
        print('Downloading weather images')
        train_images, train_labels = DownloadWeatherImages(local_folder)
    else:
        print('Getting weather images encoded, not downloading to local path')
        train_images, train_labels = read_images_from_s3(s3, bucket_name, aws_folder)

    # Converting labels into One Hot encoded sparse matrix and images into numpy array
    train_labels = pd.get_dummies(train_labels).values.reshape(-1, 4)
    train_images = np.array(train_images)

    # Splitting Training data into train and validation dataset
    x_train1, x_test1, y_train1, y_test1 = train_test_split(train_images, train_labels, random_state=1)

    # Test to see if all data got loaded in correctly
    print(x_train1.shape, x_test1.shape, y_train1.shape, y_test1.shape)
    plt.imshow(x_train1[0], interpolation='nearest')
    plt.show()
    return [x_train1, x_test1, y_train1, y_test1]


def CreateModel():
    modifiableModel = Sequential()

    opt = Adam(learning_rate=0.001)
    kernel_size = 2
    modifiableModel.add(Conv2D(16, (kernel_size,kernel_size), 1, activation="relu", input_shape=(300, 300, 3)))
    modifiableModel.add(MaxPooling2D(2))
    modifiableModel.add(Conv2D(32, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(MaxPooling2D(2))
    modifiableModel.add(Conv2D(64, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(Conv2D(128, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(Conv2D(128, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(Conv2D(264, (kernel_size,kernel_size), 1, activation="relu"))
    # modifiableModel.add(Conv2D(264, (kernel_size,kernel_size), 1, activation="relu"))
    # modifiableModel.add(Conv2D(264, (kernel_size,kernel_size), 1, activation="relu"))
    # modifiableModel.add(Conv2D(264, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(MaxPooling2D(2))
    modifiableModel.add(Flatten())
    modifiableModel.add(Dense(256, activation="relu"))
    modifiableModel.add(Dense(4, activation='softmax'))

    modifiableModel.compile(opt, loss=tf.losses.BinaryCrossentropy(), metrics=['accuracy'])
    return modifiableModel


def train_model():
    path_to_save = os.path.join(os.getcwd(), "Saved_model_weather")
    checkpoint = ModelCheckpoint(filepath=path_to_save,
                                 monitor="val_accuracy",
                                 verbose=1,
                                 save_best_only=True,
                                 mode="max")
    monitor_val_acc = EarlyStopping(monitor='val_accuracy',
                                    patience=7, min_delta=0.03)
    callbacks = [checkpoint, monitor_val_acc]
    x_train, x_test, y_train, y_test = GetTrainingData()
    model = CreateModel()
    model.fit(x_train, y_train, epochs=20, batch_size=64, validation_split=0.2, callbacks=callbacks)

    # Testing predictions and the actual label

    check_image = x_test[0]
    check_label = y_test[0]

    check_image = np.expand_dims(check_image / 255, 0)

    predict = model.predict(check_image)

    output = {0: 'Cloudy', 1: 'Foggy', 2: 'Rainy', 3: 'Sunny'}

    print("Actual :- ", check_label)
    print("Predicted :- ", output[np.argmax(predict)])
    plt.imshow(x_test[0], interpolation='nearest')
    plt.show()


if __name__ == "__main__":
    train_model()