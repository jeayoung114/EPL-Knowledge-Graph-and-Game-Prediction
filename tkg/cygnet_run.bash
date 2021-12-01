#!/usr/bin/env bash

python train.py --dataset infer_data --entity object --time-stamp 1 --alpha 0.5 --lr 0.001 --n-epoch 30 --hidden-dim 200 --gpu 0 --batch-size 1024 --counts 4 --valid-epoch 5

python train.py --dataset infer_data --entity subject --time-stamp 1 --alpha 0.5 --lr 0.001 --n-epoch 30 --hidden-dim 200 --gpu 0 --batch-size 1024 --counts 4 --valid-epoch 5

python test.py --dataset infer_data
