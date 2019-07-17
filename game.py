import os
from array import *
# s
import numpy as np
import pickle
import random
from collections import defaultdict
from joblib import dump, load
import datetime

DATA_FOLDER_NAME = 'Data'
Dataset = {}


def read_file(name):
    snapshot = defaultdict(list)
    file = open(DATA_FOLDER_NAME + '/' + str(name), 'r', encoding='utf-8')
    file.readline()
    file.readline()
    file.readline()
    file.readline()
    read = True
    while read:
        data = file.readline()
        if data == '':
            read = False
        else:
            splitted = data.split()
            snapshot[int(splitted[0])].append(splitted[1])
    return snapshot


def Neighbors(node, snapshot):
    return list(Dataset[snapshot][node])


def Degree(node, G):
    return len(Neighbors(node, G))


def GainS_v(node,c, S, G):
    Js = []
    for j in S[G]:
        if c in S[G][j] :
            pass
        elif j in Neighbors(node, G):
            Js.append(j)
    return Js


def GainFunc(Ic, MaxExterD, TwoM, Js, neighbors, degree, G):
    sigma = 0
    for j in Js:
        if j in neighbors:
            sigma = sigma + (1 - ((degree * Degree(j, G)) / TwoM))
    # print('Ic , MaxExterD , degree' ,Ic , MaxExterD , degree)
    print('sigma :', sigma)
    if Ic !=0 :
        return (Ic / (MaxExterD * degree)) + (1 / (Ic + MaxExterD))*sigma
    else:
        return (1 / (Ic + MaxExterD))*sigma


def ClusteringCoefficient(Vneighbors, snapshot):
    k = len(Vneighbors)
    if k> 1:
        edges = 0
        for node in Vneighbors:
            for n in Vneighbors:
                if node in Neighbors(n, snapshot):
                    edges = edges + 1
        # print('k:', k , 'edges:', edges)
        edges =edges /2
        return edges / (k * (k - 1))
    else:
        return 1


def LossS_v(node,c, S, G, MI):
    Js = list(S[G].keys())
    if MI != 0:
        Js.remove(MI)
    for j in Js:
        if j not in Neighbors(node,G):
            Js.remove(j)

    return Js


def LossFuncs(Ic, MaxExterD, TwoM, Js, neighbors, degree, G):
    CC = ClusteringCoefficient(neighbors, G)
    sigma = 0
    for j in Js:
        if j in neighbors:
            sigma = sigma + (1 - ((degree * Degree(j, G)) / TwoM))
    print(f' CC :{CC} Ic : {Ic} MaxExterD :{MaxExterD} sigma :{sigma}')
    return (1 - CC) + (1 / (Ic + MaxExterD))*(sigma)


if __name__ == "__main__":
    # for root, dirs, files in os.walk(DATA_FOLDER_NAME):
    #     for filename in files:
    #         snapshot = read_file(filename)
    #         Dataset[filename]=snapshot
    #
    # pickle.dump(Dataset, open("DatasetFile.p", "wb"))

    Dataset = pickle.load(open("DatasetFile.p", "rb"))
    print('dataset been read')
    # print (Dataset['as19991211.txt'][50][0]) //Dataset['as19991211.txt'][v][v])
    Snapshots = list(Dataset.keys())
    nonequilibrium = []
    S = {}
    # Graphs={}
    # for snapshot in Snapshots:
    #     Graphs[snapshot] = nx.Graph(snapshot=snapshot)
    #     for v in Dataset[snapshot]:
    #         for v2 in Dataset[snapshot][v]:
    #             Graphs[snapshot].add_node(v)
    #             Graphs[snapshot].add_node(v2)
    #             # print(v ,' and ', v2)
    #             Graphs[snapshot].add_edge(v, v2)
    # pickle.dump(Graphs, open("Graphs.p", "wb"))
    # print('dumped')
    # print( Graphs['as19991211.txt'])

    for i, G in enumerate(Snapshots):
        print(f'playing game for snapshot {i}')
        communities = set()
        VertexesOfG = list(Dataset[Snapshots[i]].keys())
        VertexesOfPreviousG = list(Dataset[Snapshots[i - 1]].keys())
        VertexS = defaultdict(list)
        TwoM = 0
        for v in VertexesOfG:
            if v not in communities:
                communities.add(v)
            TwoM = TwoM + len(Dataset[G][v])
            if G == Snapshots[0]:
                VertexS[v].append(v)
                S[G] = VertexS
                nonequilibrium.append(v)
            else:
                if v in VertexesOfPreviousG:
                    pass
                else:
                    nonequilibrium.append(v)
                    for n in Neighbors(v, G):
                        communities.add(n)
                        VertexS[n].append(n)
                        S[G] = VertexS
                        nonequilibrium.append(n)
        # print('nonequilibrium lengh:  ', len(nonequilibrium))

        while nonequilibrium:
            # print('nonequilibrium lengh:  ', len(nonequilibrium))
            index = random.randint(0, len(nonequilibrium) - 1)
            node = nonequilibrium[index]
            neighbors = Neighbors(node, G)
            degree = Degree(node, G)
            MyCommunities = S[G][node]
            isolated =True
            for v in VertexesOfG:
                for c in MyCommunities:
                    if c in S[G][v]:
                        if v != node:
                            # print('not isolated')
                            isolated=False
                            break
            if isolated:
                CurrentUtility =0
            else:
                # print('hereeeeeeeeeeeee')
                NodeIc = 0
                NodeExterD = {}
                for n in neighbors:
                    for c in S[G][n]:
                        if c in MyCommunities:
                            NodeIc = NodeIc + 1
                            break
                        else:
                            if c in NodeExterD.keys():
                                NodeExterD[c] = int(NodeExterD[c] + 1)
                            else:
                                NodeExterD[c] = 0
                MaxExterD = 0
                mostIntemate = 0
                for key in NodeExterD.keys():
                    if NodeExterD[key] > MaxExterD:
                        MaxExterD = NodeExterD[key]
                        mostIntemate = key
                # print(f'MaxExterD :{MaxExterD} mostIntemate : {mostIntemate}')
                nodeCurrentCummunity=S[G][node]
                CurrentGainJs = GainS_v(node ,nodeCurrentCummunity, S, G)
                CurrentLossJs = LossS_v(node ,nodeCurrentCummunity, S, G, mostIntemate)
                CurrentGainVc = GainFunc(NodeIc, MaxExterD, TwoM, CurrentGainJs, neighbors, degree, G)
                CurrentLossVc = LossFuncs(NodeIc, MaxExterD, TwoM, CurrentLossJs, neighbors, degree, G)
                CurrentUtility = CurrentGainVc - CurrentLossJs
            for C in communities:
                Ic = 0
                ExterD = {}
                # print(f'C : {C}')
                ExterD[C] = 0
                for n in neighbors:
                    if C in S[G][n]:
                        if C in MyCommunities:
                            Ic = Ic + 1
                        else:
                            ExterD[C] = ExterD[C] + 1



                MaxExterD = 0
                mostIntemate = 0
                # print(f'ExterD : {ExterD}')
                for key in ExterD.keys():
                    if ExterD[key] > MaxExterD:
                        MaxExterD = ExterD[key]
                        mostIntemate = key
                if Ic == 0 and MaxExterD ==0:
                    pass
                else:
                    GainJs = GainS_v(node,C, S, G)
                    LossJs = LossS_v(node,C, S, G, mostIntemate)
                    # print('(node , Ic, MaxExterD, TwoM,  degree, neighbors) \n' ,node, Ic, MaxExterD, TwoM, degree,neighbors )
                    GainVc = GainFunc(Ic, MaxExterD, TwoM, GainJs, neighbors, degree, G)
                    LossVc = LossFuncs(Ic, MaxExterD, TwoM, LossJs, neighbors, degree, G)
                    Utility = GainVc - LossVc
                    print(f'Utility :{Utility} GainVc : {GainVc }  LossVc: {LossVc} CurrentUtility : {CurrentUtility}')
                    if CurrentUtility < Utility:
                        S[G][node].append(C)
                        CurrentUtility = Utility
                        print(f'{node} joined community {C} ')

            nonequilibrium.remove(node)
        pickle.dump(S[G], open(f"snapshot{i}.p", "wb"))
    print('done')
