# League-of-Legends

This is an example of training a ML model, creating an app using `FastAPI`, and deploy it on a k8s cluster using Minikube specifying all resources with Terraform.

## Training pipeline

All resources related to model training, API, and Docker resides under folder [training_pipeline](./training_pipeline/)


## Kubernetes

All resources related to Kubernetes resides under folder [terraform](./terraform/)

## Problem description

The initial approach is training and evaluating a standard logistic regression. In addition, a support vector classifier and random forest model was also trained. From the initial results the achieved accuracy of the logistic model (with respect to F1 score) is quite good.

Uncertainty of our model is basically evaluated via precision and recall (again evaluated using F1 score). In the context of having a prediction with as little uncertainty as possible we should strive to maximize F1 score (i.e. maximize precision and recall).

Future work could include to train a deep learning model on more features to see if higher accuracy can be achieved.
