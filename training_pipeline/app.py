import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pickle


MODEL_PATH = os.path.join(os.path.dirname(__file__), './output/serving/logistic_model.pkl')
MODEL_PATH = os.path.abspath(MODEL_PATH)


app = FastAPI(title='Predicting LoL matches')


class LoLGame(BaseModel):
    firstTower: int
    firstInhibitor: int
    firstBaron: int
    firstDragon: int
    t1_towerKills: int
    t1_inhibitorKills: int
    t1_baronKills: int
    t1_dragonKills: int
    t1_riftHeraldKills: int
    t2_towerKills: int
    t2_inhibitorKills: int
    t2_baronKills: int
    t2_dragonKills: int
    t2_riftHeraldKills: int


@app.on_event('startup')
def load_model():
    """Load model object from pickle file"""
    with open(MODEL_PATH, 'rb') as file:
        global model
        model = pickle.load(file)


@app.get('/')
def home():
    return 'Congratulations, your API is working as expected! Head over to http://localhost:80/docs'


@app.post('/predict')
def predict(lol: LoLGame):
    """Make online predictions"""
    data_point = np.array([[lol.firstTower,
                            lol.firstInhibitor,
                            lol.firstBaron,
                            lol.firstDragon,
                            lol.t1_towerKills,
                            lol.t1_inhibitorKills,
                            lol.t1_baronKills,
                            lol.t1_dragonKills,
                            lol.t1_riftHeraldKills,
                            lol.t2_towerKills,
                            lol.t2_inhibitorKills,
                            lol.t2_baronKills,
                            lol.t2_dragonKills,
                            lol.t2_riftHeraldKills]])

    # Predict
    pred = model.predict(data_point).tolist()
    pred = pred[0]

    return {"Winning team": pred + 1}


if __name__ == '__main__':
    """This is for debugging purposes only.

    Run debugger and set breakpoints above where needed.
    Go to http://0.0.0.0/docs and run a POST, the debugger
    will stop at first breakpoint.
    """
    uvicorn.run(app, host='0.0.0.0', port=8080)
