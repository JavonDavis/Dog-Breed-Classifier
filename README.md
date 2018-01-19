# Dog Breed Classifier

[//]: # (Image References)

[image1]: ./readme_images/image1.png "App Screenshot"
[image2]: ./readme_images/image2.png "App Screenshot"
[image3]: ./readme_images/image3.png "App Screenshot"
[image4]: ./readme_images/image4.png "App Screenshot"

![App Screenshot][image1]

![App Screenshot][image2]

![App Screenshot][image3]

![App Screenshot][image4]

In this project I wrote a software pipeline that classifies dog breeds using a CNN. It also involves the use of a SVM to differentiate between human and dog faces and then uses the CNN to try and predict the breed of the dog or what breed the human looks like. 

The pipeline was then used then used to build a flask application that demonstrates it's functionality. 


## Getting Started 
To execute the Flask app you need to do the following steps.

* Install the requirements in the requirements/requirements.txt file using pip. 
* export FLASK_APP=webapp.py from the root dir
* flask run

The app should then be available on port 127.0.0.1:5000/home.

The dog_app.ipynb file containes the pipeline that was used to train both the face detector and the dog breed classifier.
