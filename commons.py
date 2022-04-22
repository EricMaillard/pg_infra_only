import requests
import json
import os

settings = {}
head = {}
token_query_param = ''

# load settings file named 'settings.json'
def load_settings(config_file_path):
    global settings
    global head
    global token_query_param
    global ssl_verify
    config_file_name = config_file_path + os.sep + "settings.json"
    with open(config_file_name, encoding='utf-8') as f:
         settings = json.load(f)

    head = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    if settings.get('use_via_mission_control') != None:
        if (settings['use_via_mission_control'] == True):
            head['X-CSRFToken'] = settings['X-CSRFToken']
            head['Cookie'] = settings['Cookie']

    ssl_verify = True
    if settings.get('ssl_verify') != None:
        ssl_verify = settings.get('ssl_verify')
    token_query_param = '?api-token='+settings['dynatrace_api_token']

def dynatrace_get(uri, query_parameters=None):
    jsonContent = None
    response = None
    if query_parameters == None:
        response = requests.get(uri+token_query_param, headers=head, verify=ssl_verify)
    else:
        response = requests.get(uri+token_query_param+query_parameters, headers=head, verify=ssl_verify)
    # For successful API call, response code will be 200 (OK)
    if(response.ok):
        if(len(response.text) > 0):
            jsonContent = json.loads(response.text)
    else:
        jsonContent = json.loads(response.text)
        print(jsonContent)
        errorMessage = ""
        if(jsonContent["error"]):
            errorMessage = jsonContent["error"]["message"]
            print("Dynatrace API returned an error: " + errorMessage)
        jsonContent = None
        raise Exception("Error", "Dynatrace API returned an error: " + errorMessage)

    return jsonContent

def dynatrace_post(uri, query_parameters, payload):

    jsonContent = None
    if query_parameters == None:
        response = requests.post(uri+token_query_param, headers=head, verify=ssl_verify, json=payload)
    else:
        response = requests.post(uri+token_query_param+query_parameters, headers=head, verify=ssl_verify, json=payload)
    # For successful API call, response code will be 200 (OK)
    if(response.ok):
        if(len(response.text) > 0):
            jsonContent = json.loads(response.text)
    else:
        jsonContent = json.loads(response.text)
        print(jsonContent)
        errorMessage = ""
        if (jsonContent["error"]):
            errorMessage = jsonContent["error"]["message"]
            print("Dynatrace API returned an error: " + errorMessage)
        jsonContent = None
        raise Exception("Error", "Dynatrace API returned an error: " + errorMessage)

    return jsonContent

def dynatrace_post_row_text(uri, query_parameters, payload):
    headers = {
        'Content-Type': 'text/plain; charset=UTF-8'
    }
    if settings.get('use_via_mission_control') != None:
        if (settings['use_via_mission_control'] == True):
            headers['X-CSRFToken'] = settings['X-CSRFToken']
            headers['Cookie'] = settings['Cookie']
    jsonContent = None
    if query_parameters == None:
        response = requests.post(uri+token_query_param, headers=headers, verify=ssl_verify, data=payload)
    else:
        response = requests.post(uri+token_query_param+query_parameters, headers=headers, verify=ssl_verify, data=payload)
    # For successful API call, response code will be 200 (OK)
    if not response.ok:
        print(response.text)
        raise Exception("Error on request "+uri, "Dynatrace API returned an error: " + response.text)

def dynatrace_put(uri, query_parameters, payload):

    jsonContent = None
    if query_parameters == None:
        response = requests.put(uri+token_query_param, headers=head, verify=ssl_verify, json=payload)
    else:
        response = requests.put(uri+token_query_param+query_parameters, headers=head, verify=ssl_verify, json=payload)
    # For successful API call, response code will be 200 (OK)
    if(response.ok):
        if(len(response.text) > 0):
            jsonContent = json.loads(response.text)
    else:
        jsonContent = json.loads(response.text)
        print(jsonContent)
        errorMessage = ""
        if (jsonContent["error"]):
            errorMessage = jsonContent["error"]["message"]
            print("Dynatrace API returned an error: " + errorMessage)
        jsonContent = None
        raise Exception("Error", "Dynatrace API returned an error: " + errorMessage)

    return jsonContent

def dynatrace_delete(uri, query_parameters=None):

    jsonContent = None
    if query_parameters == None:
        response = requests.delete(uri+token_query_param, headers=head, verify=ssl_verify)
    else:
        response = requests.delete(uri+token_query_param+query_parameters, headers=head, verify=ssl_verify)
    # For successful API call, response code will be 200 (OK)
    if(response.ok):
        if(len(response.text) > 0):
            jsonContent = json.loads(response.text)
    else:
        jsonContent = json.loads(response.text)
        print(jsonContent)
        errorMessage = ""
        if (jsonContent["error"]):
            errorMessage = jsonContent["error"]["message"]
            print("Dynatrace API returned an error: " + errorMessage)
        jsonContent = None
        raise Exception("Error", "Dynatrace API returned an error: " + errorMessage)

    return jsonContent

def dynatrace_get_with_next_page_key(uri, query_parameters, array_key):
    PAGE_SIZE = '&pageSize=1000'
    jsonContent = None
    response = None
    if query_parameters == None:
        params = PAGE_SIZE
    else:
        params = query_parameters + PAGE_SIZE
    # For successful API call, response code will be 200 (OK)
    metric_list = []
    data = dynatrace_get(uri, params)
    metrics = data.get(array_key)

    for metric in metrics:
        metric_list.append(metric)

    NextPageKey = data.get('nextPageKey')
    if NextPageKey != None:
        while (True):
            NEXT_PAGE_KEY = '&nextPageKey='+NextPageKey
            params = NEXT_PAGE_KEY
            data =  dynatrace_get(uri, params)
            NextPageKey = data.get('nextPageKey')
            metrics = data.get(array_key)
            for metric in metrics:
                metric_list.append(metric)
            if NextPageKey == None:
                break

    return metric_list
