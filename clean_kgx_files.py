import csv
import os
import glob
import sys

csv.field_size_limit(sys.maxsize)

def clean_up_files(ofname,single_files,fields):

    with open(ofname,'w') as clean_file:
        clean_writer = csv.DictWriter(clean_file,fieldnames=fields,delimiter='\t')
        clean_writer.writeheader()
        
        for ifname in single_files:
            with open(ifname,'r') as single_file:
                single_reader = csv.DictReader(single_file,delimiter='\t')
                for row in single_reader:
                    clean_writer.writerow({i:row[i] for i in fields} )

def main():

    core_node_fields=["id","category","name","provided_by","knowledge_source"]
    core_edge_fields=["id","subject","predicate","object","knowledge_source"]

    single_node_files = glob.glob("data/kgx_files/*_nodes.tsv")
    single_edges_files = glob.glob("data/kgx_files/*_edges.tsv")
    
    node_fname = "data/tox21_cluster_nodes.tsv"
    edge_fname = "data/tox21_cluster_edges.tsv"

    clean_up_files(node_fname,single_node_files,core_node_fields)
    clean_up_files(edge_fname,single_edges_files,core_edge_fields)

if __name__=="__main__":
    main()