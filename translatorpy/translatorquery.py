from .trapigraph import TrapiGraph
from .utilities import *

import json
import requests
from collections import defaultdict
import copy
from datetime import datetime as dt
import urllib.parse
import time
from csv import reader
import os
import time

class TranslatorQuery():
    """
    An NCATS Biomedical Data Translator query class
    """
    def __init__(self) -> None:
        self.message_id =  None
        self.query_graph = None
        self.results = None
        self.arax_base='https://arax.ncats.io'
        self.ars_url='https://ars.transltr.io/ars/api'
        self.starttime = None
        self.runtime = None
        self.timeout = 20*60

    def __submit_to_ars(self,m,ars_url='https://ars.transltr.io/ars/api'):
        """
        A private method to submit a trapi message to the ARS and get back the message id.
        Has the side effect of storing the ARAX url for interaction with query in the browser.
        """

        submit_url=f'{ars_url}/submit'
        self.starttime = time.time()
        response = requests.post(submit_url,json=m)
        try:
            message_id = response.json()['pk']
        except:
            print('ARS failed to respond')
            message_id = None
            #
        self.arax_url = f'{self.arax_base}/?source=ARS&id={message_id}'
        return message_id

    def __check_status(self,mid,ars_url='https://ars.transltr.io/ars/api'):
        message_url = f'{ars_url}/messages/{mid}?trace=y'
        response = requests.get(message_url)
        j = response.json()
        return j['status']

    def __retrieve_ars_results(self,mid,ars_url='https://ars.transltr.io/ars/api'):
        """
        A private method to retrieve and munge ARS results based on a trapi message id
        """
        message_url = f'{ars_url}/messages/{mid}?trace=y'
        response = requests.get(message_url)
        j = response.json()
        print( j['status'] )
        results = {}
        for child in j['children']:
            print(child['status'])
            if child['status']  == 'Done':
                childmessage_id = child['message']
                child_url = f'{ars_url}/messages/{childmessage_id}'
                try:
                    child_response = requests.get(child_url).json()
                    nresults = len(child_response['fields']['data']['message']['results'])
                    if nresults > 0:
                        results[child['actor']['agent']] = {'message':child_response['fields']['data']['message']}
                except Exception as e:
                    nresults=0
                    child['status'] = 'ARS Error'
            elif child['status'] == 'Error':
                nresults=0
                childmessage_id = child['message']
                child_url = f'{ars_url}/messages/{childmessage_id}'
                try:
                    child_response = requests.get(child_url).json()
                    results[child['actor']['agent']] = {'message':child_response['fields']['data']['message']}
                except Exception as e:
                    print(e)
                    child['status'] = 'ARS Error'
            else:
                nresults = 0
            print( child['status'], child['actor']['agent'],nresults )
        return results

    def query(self,query_graph,delay=30):
        """
        Public method to submit a query graph. 
        """
        self.query_graph = query_graph
        self.message_id=self.__submit_to_ars(self.query_graph.query)
        print(self.message_id)
        #timeout_count = 0

        time.sleep(delay)#Time to figure itself out
        while self.__check_status(self.message_id) == 'Running':
            #current_time = time.time()
            #self.runtime = current_time - self.starttime
            #if self.runtime > self.timeout:
                
                #if timeout_count < 1:
                #    print("Re-submitting")
                #    self.message_id=self.__submit_to_ars(self.query_graph.query)
                #    timeout_count += 1
                #else:
            #    print("Giving up")
            #    break
            #else:
            print("Still Running")
            time.sleep(delay) #Time to finish
        time.sleep(delay*2) #Time to actually get the data in 
        self.results=self.__retrieve_ars_results(self.message_id)

    def __to_tsvlist(self,message,predicate_blacklist=[]):
        #results = getpath(message,["message","results"])
        #printjson(results)
        kg = getpath(message,["message","knowledge_graph"])
        edges = kg['edges'].items()
        nodes = kg['nodes']
        tsv_list=[]
        for id,edge in edges:
            triple = (nodes[edge['subject']]['name'],edge['predicate'],nodes[edge['object']]['name'])
            tsv_list.append('\t'.join(triple))
        
        return tsv_list

    def to_tsv(self,fname):
        with open(fname,'w') as ofile:
            for result in self.results:
                message =  self.results[result]['message'].get('results')
                if message is not None:
                    tsv_list = self.__to_tsvlist(self.results[result])
                    for line in tsv_list:
                        ofile.write(line + '\n')
