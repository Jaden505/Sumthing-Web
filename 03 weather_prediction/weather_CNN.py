# Importing modules
import os

import cv2
import numpy as np
import pandas as pd
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.layers import Dense, Conv2D, Flatten, MaxPool2D, MaxPooling2D
from keras.models import Sequential
from keras.optimizers import Adam
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV, KFold
from matplotlib import pyplot as plt
import tensorflow as tf

from convert_to_jpg import image_name_changer

np.random.seed(1)


def GetTrainingData():
    train_images = []
    train_labels = []
    img_size = 300
    shape = (img_size, img_size)

    # Path for changer should be the path where all images are saved at first
    path_for_changer = ""
    # Path to save should be the path where all new images should be saved to
    path_to_save = ""

    # Image name changer makes sure that the photo's names change to have a number infront.
    # This numnber corresponds to the weather seen on the picture
    # ( Cloudy( 0 ), Sunny( 1 ), Rainy( 2 ), Snowy( 3 ), Foggy( 4 ))
    image_name_changer(path_for_changer, "jpg", path_to_save)

    for filename in os.listdir(path_to_save):
        if filename.split('.')[1] == 'JPG':
            img = cv2.imread(os.path.join(path_to_save, filename))

            # Spliting file names and storing the labels for image in list
            train_labels.append(filename.split('_')[0])

            # Resize all images to a specific shape
            img = cv2.resize(img / 255, shape)

            train_images.append(img)

    # Converting labels into One Hot encoded sparse matrix
    train_labels = pd.get_dummies(train_labels).values

    # Converting train_images to array
    train_images = np.array(train_images)

    # Splitting Training data into train and validation dataset
    x_train1, x_test1, y_train1, y_test1 = train_test_split(train_images, train_labels, random_state=1)

    # Test to see if all data got loaded in correctly
    print(y_train1[0])
    plt.imshow(x_train1[0], interpolation='nearest')
    plt.show()
    return [x_train1, x_test1, y_train1, y_test1]


def CreateModel():
    modifiableModel = Sequential()

    opt = Adam(learning_rate=0.0005)
    kernel_size = 2
    modifiableModel.add(Conv2D(16, (kernel_size,kernel_size), 1, activation="relu", input_shape=(300, 300, 3)))
    modifiableModel.add(MaxPooling2D(2))
    modifiableModel.add(Conv2D(32, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(MaxPooling2D(2))
    modifiableModel.add(Conv2D(64, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(Conv2D(128, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(Conv2D(128, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(Conv2D(264, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(Conv2D(264, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(Conv2D(264, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(Conv2D(264, (kernel_size,kernel_size), 1, activation="relu"))
    modifiableModel.add(MaxPooling2D(2))
    modifiableModel.add(Flatten())
    modifiableModel.add(Dense(256, activation="relu"))
    modifiableModel.add(Dense(5, activation='softmax'))

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
    model.fit(x_train, y_train, epochs=30, batch_size=100, validation_split=0.2, callbacks=callbacks)

    # Testing predictions and the actual label

    check_image = x_test[0]
    check_label = y_test[0]

    check_image = np.expand_dims(check_image / 255, 0)

    predict = model.predict(check_image)

    # ( Cloudy( 0 ), Sunny( 1 ), Rainy( 2 ), Snowy( 3 ), Foggy( 4 ))
    output = {0: 'Cloudy', 1: 'Sunny', 2: 'Rainy', 3: 'Snowy', 4: "Foggy"}

    print("Actual :- ", check_label)
    print("Predicted :- ", output[np.argmax(predict)])
    plt.imshow(x_test[0], interpolation='nearest')
    plt.show()
