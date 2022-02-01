from ast import arg
from simpletransformers.classification import ClassificationModel
import pandas as pd
import sklearn
from sklearn.metrics import f1_score, precision_score, recall_score
import os
import json
import requests


# url = 'http://amf2.arg.tech/segmenter-01'
# files = {'file': open('data.json', 'rb')}

# r = requests.post(url, files=files)




def get_argument_relations(filename):
    print("--------------------------------------")
    print("running")

    with open(filename) as json_file:
    
        arg_map = json.load(json_file)
        print(arg_map)
        counter = 0
        loop_counter = 0
        t1 = None
        t2 = None
        i_nodes = []

        dataset = pd.DataFrame(columns=['t1', 't2'])

        for node in arg_map['nodes']:

            if node['type'] == 'I':
                i_nodes.append(node)
                
                if (len(i_nodes) > 1):
                    t1 = i_nodes[counter-1]['text']
                    t2 = i_nodes[counter]['text']

                    dataset = dataset.append({'t1': t1, 't2': t2}, ignore_index=True)
                    dataset = dataset.append({'t1': t2, 't2': t1}, ignore_index=True)

                counter += 1
            loop_counter += 1

        # RUN DATA THROUGH MODEL

        model = ClassificationModel('roberta', 'trained_models/roberta-model-trained/checkpoint-15500-epoch-50', num_labels=4, use_cuda=False, args={'silent':True})

        data_df = pd.DataFrame.from_dict(dataset)
        data_df.columns = ['text_a', 'text_b']

        rel_dataset = pd.DataFrame(columns=['t1', 't2', 'rel'])
        for index, row in data_df.iterrows():
            prediction, raw_outputs = model.predict([[row['text_a'],row['text_b'] ]])
            if prediction[0] == 0:
                pred = "RA"
            elif prediction[0] == 1:
                pred = ('CA')
            elif prediction[0] == 2:
                pred = ('MA')
            elif prediction[0] == 3:
                pred = ('NO')
            
            rel_dataset = rel_dataset.append({'t1': row['text_a'], 't2': row['text_b'], 'rel': pred}, ignore_index=True)




        json_data = arg_map
        nodeID = 800000
        edgeID = 900000
        new_node = ''
        for index, row in rel_dataset.iterrows():
            node1_id = ''
            node2_id = ''
            if (row['rel'] == 'RA'):
                print('RA')                    
                new_node = {'nodeID': nodeID, 'text': "Default Inference", 'type': "RA", 'timestamp': "", 'scheme': "Default Inference", 'schemeID': "72"}
                # json_data["nodes"].append(new_node)
                nodeID += 1
            elif (row['rel'] == 'CA'):
                print('CA')   
                new_node = {'nodeID': nodeID, 'text': "Default Conflict", 'type': "CA", 'timestamp': "", 'scheme': "Default Conflict", 'schemeID': "71"}
                # json_data["nodes"].append(new_node)
                nodeID += 1
            elif (row['rel'] == 'MA'):
                print('MA')   
                new_node = {'nodeID': nodeID, 'text': "Default Rephrase", 'type': "MA", 'timestamp': "", 'scheme': "Default Rephrase", 'schemeID': "144"}
                # json_data["nodes"].append(new_node)
                nodeID += 1
            else:
                continue

            print(row)
            

            for node in json_data['nodes']:
                if node['text'] == row['t1']:
                    node1_id = node['nodeID']
                elif node['text'] == row['t2']:
                    node2_id = node['nodeID']
                
            # for node in json_data['nodes']:
            #     if node['type'] == 'RA' or node['type'] == 'CA' or node['type'] == 'MA':
            dont_add = False

            for node in json_data['nodes']:
                if node['type'] == 'RA' or node['type'] == 'CA' or node['type'] == 'MA':
                    for edge in json_data['edges']:
                        if edge['toID'] == node['nodeID'] and edge['fromID'] == node1_id:
                            for edge in json_data['edges']:
                                if edge['fromID'] == node['nodeID'] and edge['toID'] == node2_id:
                                    dont_add = True


                
            
            if new_node != '' and dont_add == False:
                json_data["nodes"].append(new_node)

                new_edge1 = {"edgeID":edgeID, "fromID":node1_id,"toID":new_node['nodeID'],"formEdgeID":'null'}
                edgeID += 1
                new_edge2 = {"edgeID":edgeID,"fromID":new_node['nodeID'],"toID":node2_id,"formEdgeID":'null'}
                edgeID += 1

                json_data["edges"].append(new_edge1)
                json_data["edges"].append(new_edge2)

        result = json.dumps(json_data)

        return result
            

# if __name__ == '__main__':
#     get_argument_relations()