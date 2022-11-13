# Model training

## Notebooks

Two notebooks have been created for this problem:

* [EDA - Exploratory Data Analysis](./eda.ipynb)
* [Logistic classifier](./logistic_model.ipynb)

In [EDA - Exploratory Data Analysis](./eda.ipynb) an initial investigation is done on the data. Correlation analysis is performed as a way to select features with high correlation against our target.

In [Logistic classifier](./logistic_model.ipynb) we use the selected features to train a standard logistic model and evaluate the performance.

---

## Training pipeline

A more scalable approach for model training and serving.

A logisic classifier trained on the [League-of-Legends dataset](https://www.kaggle.com/datasets/datasnaek/league-of-legends) is already trained and resides under [output/serving](/training_pipeline/output/serving/).

### Serving with FastAPI

Build docker image:

```bash
# Use Python version as tag
# Stand in root folder
docker build -t lol-model:3.10.6 .
```

Check that model is working out of container by running the following:

```bash
docker run --rm -p 80:80 lol-model:3.10.6
```

> This will spin up a service of the API.

In a new terminal window (or under [localhost](https://localhost:80/docs)) make some predictions by running:

```bash
# cd into training_pipeline/serving
curl -X POST http://localhost:80/predict \
    -d @./lol_examples/0.json \
    -H "Content-Type: application/json"
```

> Once you've verified that the running container can take a request and return predictions you can stop the running API.


<details>
<summary> <i> Debugging FastAPI </i> </summary>

In case the API needs debugging, set breakpoint in [app.py](/training_pipeline/app.py) and run debugger from your console (VSCode, Pycharm, etc.).

This will start the API session, go to [localhost](https://localhost:80/docs) and send an example `JSON` (or send data via `curl`) to the API. You should hit the breakpoint and you can start debugging.

</details>
<br>