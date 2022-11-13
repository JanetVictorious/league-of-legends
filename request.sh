#!/bin/bash

while sleep 0.01;

do curl -X POST $(minikube ip):30001/predict \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
	"firstTower": 2,
  "firstInhibitor": 2,
  "firstBaron": 2,
  "firstDragon": 1,
  "t1_towerKills": 0,
  "t1_inhibitorKills": 0,
  "t1_baronKills": 0,
  "t1_dragonKills": 2,
  "t1_riftHeraldKills": 0,
  "t2_towerKills": 10,
  "t2_inhibitorKills": 2,
  "t2_baronKills": 1,
  "t2_dragonKills": 1,
  "t2_riftHeraldKills": 1
}';

done
