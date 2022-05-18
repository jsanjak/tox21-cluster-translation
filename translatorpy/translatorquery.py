from .trapigraph import TrapiGraph

import json
import requests
from collections import defaultdict
import copy
from datetime import datetime as dt
import urllib.parse
import time
from csv import reader
import os

class TranslatorQuery():
    """
    An NCATS Biomedical Data Translator query class
    """
    def __init__(self) -> None:
        self.message_id =  None
        self.query_graph = None
        self.results = None
        self.arax_base='https://arax.ncats.io'

    def __submit_to_ars(self,m,ars_url='https://ars.transltr.io/ars/api'):
        """
        A private method to submit a trapi message to the ARS and get back the message id.
        Has the side effect of storing the ARAX url for interaction with query in the browser.
        """

        submit_url=f'{ars_url}/submit'
        response = requests.post(submit_url,json=m)
        try:
            message_id = response.json()['pk']
        except:
            print('ARS failed to respond')
            message_id = None

        self.arax_url = f'{self.arax_base}/?source=ARS&id={message_id}'
        return message_id
    
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

    def query(self,query_graph):
        """
        Public method to submit a query graph. 
        """
        self.query_graph = query_graph
        self.message_id=self.__submit_to_ars(self.query_graph.query)
        time.sleep(60)
        self.results=self.__retrieve_ars_results(self.message_id)

