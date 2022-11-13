# Terraform resources

In order to make the model available for online inference.

All terraform resources reside in the [terraform folder](/terraform/). The main orchestration script is [main.tf](/terraform/environment/dev/main.tf) which will specify to use Minikube as configuration and which [Kubernetes modules](/terraform/modules/kubernetes/main.tf) to deploy.

Some convetion:

* `main.tf` scripts are describing Terraform resources/modules
* `variables.tf` / `terraform.tfvars` describes variables being used
* `versions.tf` describes provider versions used for resources

### Kubernetes manifests

All `YAML` manifests reside in the [manifest folder](/terraform/modules/kubernetes/manifests/).

While there are Kubernetes resources on Terraform for deployment, service, etc. the use of traditional `YAML` files is somewhat nice. By utilizing the [kubernetes_manifest](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs/resources/manifest) or [kubectl_manifest](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/kubectl_manifest) you can easily deploy to a cluster by using already existing `YAML` files. One advantage of this is that you can keep your Terraform code small while still deploying large complex `YAML` files.

---

## Run cluster on minikube

Before deploying resources start Minikube:

```bash
minikube start --driver=virtualbox
```

In order for the cluster to use your docker image, run the Docker daemon out of Minikube:

```bash
eval $(minikube docker-env)
```

Build docker image on Minikube:

```bash
docker build -t lol-serving:3.10.6 .
```

Verify image was created by listing all images:

```bash
docker images
```

### Deploy resources

#### Terraform deployed resources

`cd` into the [dev folder](/terraform/environment/dev/) and run

```bash
terraform init
```

This will initialize Terraform and download required providers and versions.

Run the following to apply manifests:

```bash
terraform apply
```

This will create a `deployment`, `service`, and `autoscaling` under namespace `dev-cluster-ns`.

#### Deployment & Service

Check status of deployment (this will tell you if the deployment is ready):

```bash
kubectl get deploy -n dev-cluster-ns
```

You should see something like this:

```bash
NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
model-serving-deployment   1/1     1            1           4m17s
```

Check status of service:

```bash
kubectl get svc model-serving-service -n dev-cluster-ns
# or
kubectl get service -n dev-cluster-ns
```

You should see something like this:

```bash
NAME                    TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
model-serving-service   NodePort   10.102.166.117   <none>        80:30001/TCP   5m36s
```

You can try accessing the deployment now as a sanity check. The following `curl` command will send a row of inference requests to the Nodeport service:

```bash
curl -X POST $(minikube ip):30001/predict \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "island": "Torgersen",
  "culmen_length_mm": 39.1,
  "culmen_depth_mm": 18.7,
  "flipper_length_mm": 181,
  "body_mass_g": 3750,
  "sex": "MALE"
}'
```

<details>
<summary> <i> Troubleshooting: Click here if `curl` command is not working </i> </summary>

Please run this command in a separate window: `minikube service model-serving-service -n dev-cluster-ns`. You will see an output like below:

```shell
|----------------|-----------------------|-----------------------|---------------------------|
|   NAMESPACE    |         NAME          |      TARGET PORT      |            URL            |
|----------------|-----------------------|-----------------------|---------------------------|
| dev-cluster-ns | model-serving-service | model-serving-http/80 | http://192.168.49.2:30001 |
|----------------|-----------------------|-----------------------|---------------------------|
🏃  Starting tunnel for service model-serving-service.
|----------------|-----------------------|-------------|------------------------|
|   NAMESPACE    |         NAME          | TARGET PORT |          URL           |
|----------------|-----------------------|-------------|------------------------|
| dev-cluster-ns | model-serving-service |             | http://127.0.0.1:49688 |
|----------------|-----------------------|-------------|------------------------|
🎉  Opening service dev-cluster-ns/model-serving-service in default browser...
❗  Because you are using a Docker driver on darwin, the terminal needs to be open to run it.
```

This opens a tunnel to your service with a random port. Grab the URL at the bottom right box and use it in the curl command like this:

```bash
curl -X POST http://127.0.0.1:49688/predict \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "island": "Torgersen",
  "culmen_length_mm": 39.1,
  "culmen_depth_mm": 18.7,
  "flipper_length_mm": 181,
  "body_mass_g": 3750,
  "sex": "MALE"
}'
```

</details>
<br>

If the command is successful you should see something like:

```shell
{"Prediction":"Adelie"}%
```

#### Horisontal Pod Autoscaler

Launch Metrics Server in Minikube:

```bash
minikube addons enable metrics-server
```

You should see somthing like this:

```shell
💡  metrics-server is an addon maintained by Kubernetes. For any concerns contact minikube on GitHub.
You can view the list of minikube maintainers at: https://github.com/kubernetes/minikube/blob/master/OWNERS
    ▪ Using image k8s.gcr.io/metrics-server/metrics-server:v0.6.1
🌟  The 'metrics-server' addon is enabled
```

Run the command below and wait for the deployment to be ready:

```shell
kubectl get deployment metrics-server -n kube-system
```

You should see somthing like this:

```shell
NAME             READY   UP-TO-DATE   AVAILABLE   AGE
metrics-server   1/1     1            1           10h
```

### Stress test

To test the autoscaling capability of the deployment, run the bash script (`request.sh`) that will just persistently send requests to the application. Please open a new terminal window, make sure that you're in the root directory, then run this command:

```bash
/bin/bash request.sh
```

<details>
<summary> <i> Troubleshooting: Click here if `request.sh` command is not working </i> </summary>

If you experience a similar problem as when trying to send request with `$(minikube ip):3001` modify `request.sh` as follows:

```bash
do curl -X POST http://127.0.0.1:49688/predict \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "island": "Torgersen",
  "culmen_length_mm": 39.1,
  "culmen_depth_mm": 18.7,
  "flipper_length_mm": 181,
  "body_mass_g": 3750,
  "sex": "MALE"
}';
```

Remember this requires your tunnel to be open.

</details>
<br>

You should see the results being printed in quick succession:

```shell
{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%{"Prediction":"Adelie"}%
```

There are several ways to monitor this but the easiest would be to use Minikube's built-in dashboard. You can launch it by running:

```bash
minikube dashboard
```

Navigate from the `deafault` namespace to `dev-cluster-ns` and select the `Pods` section under `Workloads`.