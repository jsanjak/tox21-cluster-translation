import requests
import urllib.parse

def resolve_name(string):
        url_string=urllib.parse.quote(string)
        name_resolver_url="https://name-resolution-sri.renci.org/lookup?string="
        message_url = f'{name_resolver_url}{string}&offset=0&limit=10'
        response = requests.post(message_url)
        return response.json()


def translate_node_name(list_input, ontology_prefix, sort_by_ontology=False, log=False):
        '''
        translate array of values using the translator name resolver
        will return multiple rows if multiple results returned for one name
        ex: 
            list_test_result = translate(list_test, 'NCBIGene', sort_by_ontology=True)
        get:
            [('MT-ND2', 'NCBIGene:56168'), ('MT-ND2', 'NCBIGene:387315')]
        '''
        # initialize
        list_result = []

        # query for the list of names
        for name in list_input:
            #url_call = urllib.parse.quote(name)
            try:
                #response = requests.post(url_call)
                output_json = resolve_name(name)
                #output_json = response.json()
            except ValueError:
                print("got json error for {}, so skip".format(name))
                continue

            # parse
            for key, value in output_json.items():
                if ontology_prefix in key:
                    list_result.append((name, key))
                    #Cutting things off at one
                    break

        if sort_by_ontology:
            list_result.sort(key = lambda x: int(x[1].split(":")[1]))

        # return
        return list_result
  
def getpath_impl(j, fields, i):
    if(j is None or i>=len(fields)):
        return j
    field = fields[i]
    jNext = j[field] if field in j else None
    return getpath_impl(jNext, fields, i+1)

def getpath(j, fields):
    return getpath_impl(j, fields, 0)