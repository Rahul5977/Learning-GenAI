#!/bin/bash

export $(grep -v '^#' .env | xargs -d '\n') 

export PYTHONPATH=./rag_queue
rq worker --with-scheduler --url redis://valkey:6379