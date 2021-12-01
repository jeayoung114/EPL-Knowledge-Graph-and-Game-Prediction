#!/usr/bin/env bash

python pretrain.py -d data --gpu 0 --dropout 0.5 --n-hidden 200 --lr 1e-3 --max-epochs 20 --batch-size 1024

python train.py -d data --gpu 0 --dropout 0.5 --n-hidden 200 --lr 1e-3 --max-epochs 20 --batch-size 1024

python test.py --d data --gpu 0 --n-hidden 200
