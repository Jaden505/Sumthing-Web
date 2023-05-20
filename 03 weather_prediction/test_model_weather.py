from weather_CNN import GetTrainingData

from keras.models import load_model
import matplotlib.pyplot as plt
import pandas as pd

# Load the saved model
model = load_model('Saved_model_weather')
history = pd.read_csv('training_hist.log', sep=',', engine='python')
accuracy = history['accuracy']
loss = history['loss']

def plot_accuracy():
    plt.plot(accuracy)
    plt.title('Training History Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.show()

def plot_loss():
    plt.plot(loss)
    plt.title('Training History Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.show()

if __name__ == '__main__':
    plot_accuracy()
    plot_loss()
