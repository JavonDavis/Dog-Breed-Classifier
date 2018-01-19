import numpy as np
from keras.applications.resnet50 import ResNet50
from keras.applications.resnet50 import preprocess_input
from keras.models import model_from_json
from keras.preprocessing import image
from sklearn.externals import joblib
from tqdm import tqdm
import cv2

from extract_bottleneck_features import extract_InceptionV3

# load json and create model
json_file = open('models/model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
dog_breed_model = model_from_json(loaded_model_json)
# load weights into new model
dog_breed_model.load_weights("models/model-weights.h5")
print("Loaded model from disk")

clf = joblib.load('models/face_classifier.pkl')
print("Loaded classifier from disk")

# define ResNet50 model
ResNet50_model = ResNet50(weights='imagenet')

dog_names = tuple(open('dog_names.txt', 'r'))


def path_to_tensor(img_path):
    # loads RGB image as PIL.Image.Image type
    img = image.load_img(img_path, target_size=(224, 224))
    # convert PIL.Image.Image type to 3D tensor with shape (224, 224, 3)
    x = image.img_to_array(img)
    # convert 3D tensor to 4D tensor with shape (1, 224, 224, 3) and return 4D tensor
    return np.expand_dims(x, axis=0)


def paths_to_tensor(img_paths):
    list_of_tensors = [path_to_tensor(img_path) for img_path in tqdm(img_paths)]
    return np.vstack(list_of_tensors)


def ResNet50_predict_labels(img_path):
    # returns prediction vector for image located at img_path
    img = preprocess_input(path_to_tensor(img_path))
    return np.argmax(ResNet50_model.predict(img))


def dog_detector(img_path):
    prediction = ResNet50_predict_labels(img_path)
    return (prediction <= 268) & (prediction >= 151)


def face_detector(img_path):
    data = paths_to_tensor([img_path]).astype('float32') / 255.
    data = data.reshape((1, -1))
    return clf.predict(data)[0]

# OpenCV Face detector
# extract pre-trained face detector
# face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml')

# print("Extracted face classifier")

# def face_detector(img_path):
#     img = cv2.imread(img_path)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray)
#     return len(faces) > 0


def get_breed(predicted_vector):
    threshold = 50
    predicted_vector = predicted_vector[0]
    k = 5
    topk = predicted_vector.argsort()[-k:][::-1]
    results = []
    classification_data = {}
    for pred in topk:
        percentage = predicted_vector[pred] * 100
        dog_name = dog_names[pred].replace('_', ' ').strip()
        classification_data[dog_name] = predicted_vector[pred]
        results.append((dog_name, percentage))
        print('{} - {}'.format(dog_name, percentage))
    print('-' * 10)

    def get_percentage(result):
        return result[1]

    def get_name(result):
        return result[0]

    disparity = get_percentage(results[0]) - get_percentage(results[1])

    if disparity > threshold:  # if you're at least sure as the defined threshold
        return [get_name(results[0])], classification_data
    else:
        return [get_name(results[0]), get_name(results[1])], classification_data


def InceptionV3_predict_breed(img_path):
    bottleneck_feature = extract_InceptionV3(path_to_tensor(img_path))
    predicted_vector = dog_breed_model.predict(bottleneck_feature)
    return get_breed(predicted_vector)


def classify_breed(img_path):
    breed, classification_data = InceptionV3_predict_breed(img_path)
    is_face = False
    if len(breed) == 1:
        formatted_message = breed[0]
    else:
        formatted_message = 'mixture of {} and {}'.format(breed[0], breed[1])
    if face_detector(img_path):
        is_face = True
        message = 'This face looks like a.... {}'.format(formatted_message)
    elif dog_detector(img_path):
        message = 'The dog breed is a.... {}'.format(formatted_message)
    else:
        message = 'I don\'t know what this is but it looks like a {}'.format(formatted_message)
    return {'message': message.strip(), 'breed': breed, 'data': classification_data, 'face': is_face}
