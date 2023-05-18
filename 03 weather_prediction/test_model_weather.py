from weather_CNN import GetTrainingData

from keras.models import load_model
import matplotlib.pyplot as plt

# Load the saved model
model = load_model('Saved_model_weather')

# Get the test data
_, x_test, _, y_test = GetTrainingData()

# Evaluate the model on the test data
loss, accuracy = model.evaluate(x_test, y_test)

# Display the accuracy in a graph
plt.bar(['Accuracy'], [accuracy])
plt.ylim([0, 1])
plt.title('Model Accuracy')
plt.show()