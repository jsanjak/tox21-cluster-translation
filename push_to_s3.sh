#!/bin/bash

aws s3 cp data/tox21_cluster_nodes.tsv s3://bucket-sdoz4r/tox21_cluster_nodes.tsv
aws s3 cp data/tox21_cluster_edges.tsv s3://bucket-sdoz4r/tox21_cluster_edges.tsv
