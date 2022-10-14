from cProfile import label
from cmath import nan
import pandas as pd
import numpy as np
import streamlit as st
import re
import statistics
import spacy

import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# HELP FUNCTIONS
def makeItalic(s):
    return "*"+str(s)+"*"
def makeBold(s):
    return "**"+str(s)+"**"
def tagDuplicate(col):

    if(len(col.unique()) != 1):
        return ['color: red' for c in col]
    else:
        return ['color: green' for c in col] 


def extractNumber(s):
    lst = re.findall(r"[-+]?\d*\.\d+|\d+", str(s))
    if len(lst)> 0:
        return max([float(i) for i in lst])
    else:
        return nan

def transformColumnToNumberCluster(df, col, n, type):
    df['extracted'] = ""
    if type == "Ankerpunten":
        df['extracted'] = df.apply(lambda row: extractNumber(row[col]), axis=1)
        filtered_df = df['extracted'][df['extracted'].notnull()]
        model = KMeans(n_clusters=n)
        cluster_labels = model.fit_predict(filtered_df.values.reshape(-1,1))
        # st.write(model.cluster_centers_)

        cluster_labelsTemp = [int(x) for x in model.cluster_centers_]
        cluster_labelsTemp.sort()
        
        cutOffMap = {}
        cutOffMap[-1] = "Niet ingevuld"

        new_cluster_labelsTemp = []
        for idx, l in enumerate(cluster_labelsTemp):
            if l != cluster_labelsTemp[-1]:
                new_cluster_labelsTemp.append( int((l + cluster_labelsTemp[idx+1]) /2) )



        for idx, label in enumerate(new_cluster_labelsTemp):

            if label == new_cluster_labelsTemp[0]:
                cutOffMap[idx] = "Tot " + str(label) 
                nextLabel = new_cluster_labelsTemp[idx+1]
                cutOffMap[idx+1] = "[ " + str(label) + " - " + str(nextLabel) + " ]" 
            else:
                if label == new_cluster_labelsTemp[-1]:
                    cutOffMap[idx+1] = "Vanaf " + str(label)
                else:
                    nextLabel = new_cluster_labelsTemp[idx+1]
                    cutOffMap[idx+1] = "[ " + str(label) + " - " + str(nextLabel) + " ]"


        


        df["Grouped " + str(col)] = " "
        df["Grouped " + str(col)][df['extracted'].notnull()] = cluster_labels
        df["Grouped " + str(col)][df['extracted'].isnull()] = -1

        df["Grouped " + str(col)] = df.apply(lambda row: cutOffMap[row["Grouped " + str(col)]], axis=1)

        return df, list(cutOffMap.values())

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def transformColumnToSemanticCluster(df, col, n):
    nlp = spacy.load('en_core_web_lg')
    
    uniqueVals = df[col][df[col].notnull()].unique()

    l = len(uniqueVals)
    similarityMap = {}

    for idx1, record1 in enumerate(uniqueVals):
        print(str(idx1) + " / "+ str(l))
        columnSim = []
        for _, record2 in enumerate(uniqueVals):
            columnSim.append(nlp(record1).similarity(nlp(record2)))
        similarityMap[record1] = columnSim
    
    simDF = pd.DataFrame(similarityMap)
    model = KMeans(n_clusters=n)
    cluster_labels = model.fit_predict(simDF)
    simDF["class"] = cluster_labels
    simDF["Name"]= uniqueVals

    mapToReturn = simDF.groupby(['class'])['Name'].apply(lambda grp: list(grp.value_counts().index)).to_dict()

    df["Grouped " + str(col)] = "Niet ingevuld"  
    for key, value in mapToReturn.items():
        df["Grouped " + str(col)][df[col].isin(value)]= "Groep " + str(key)

    return df, mapToReturn

    



            




# Toevoegen van Name parameter zorgt dat cache wordt weggegooid bij inladen van nieuwe file (want deze zal dezelfde key hebben)
# @st.cache(allow_output_mutation=True)
# def createDataFrameFromDataset(key, name):
#     return pd.read_csv(st.session_state[key]) 

def createDataFrameFromDataset(uploaded):
    # return pd.read_csv(uploaded)
    return pd.read_csv(uploaded, delimiter=',')



def createPaginering(key, colstoUse, N):
    # A variable to keep track of which product we are currently displaying
    if key not in st.session_state:
        st.session_state[key] = 0
    

    last_page = len(colstoUse) // N

    # Add a next button and a previous button
    prev, _, tussen, _ ,next = st.columns([1,5,2,5,1])

    if next.button("Volgende resultaten"):
        if st.session_state[key] + 1 > last_page:
            st.session_state[key] = 0
        else:
            st.session_state[key] += 1

    if prev.button("Vorige resultaten"):
        if st.session_state[key] - 1 < 0:
            st.session_state[key] = last_page
        else:
            st.session_state[key] -= 1
    
    with tussen:
        st.write( str(st.session_state[key] +1) + "/"+ str(last_page +1) +" (" + str(len(colstoUse)) +" resultaten)")

    # Get start and end indices of the next page of the dataframe
    start_idx = st.session_state[key] * N 
    end_idx = (1 + st.session_state[key]) * N

    # Index into the sub dataframe
    return colstoUse[start_idx:end_idx]