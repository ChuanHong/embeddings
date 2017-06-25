# -*- coding: utf-8 -*-

# input to hole is a bin file. converting to bin file
# Save a dictionary into a pickle file.
import pickle


data={}

f=open("entity2id.txt","r")
entity_dict={}


entities=[]

for line in f:
    line=line.strip()
    tokens=line.split()
    entity_dict[tokens[0]]=int(tokens[1])
    entities.append(tokens[0].decode('utf-8'))
    
data[u'entities']=entities
    
    
f=open("relation2id.txt","r")
relation_dict={}


relation=[]

for line in f:
    line=line.strip()
    tokens=line.split("\t")
    stri="$$"+tokens[0]+"$$"
    print stri
    relation_dict[tokens[0].strip()]=int(tokens[1])  
    relation.append(tokens[0].decode('utf-8'))
    
    
data[u'relations']=relation


f=open("test.txt")
test_sub=[]

for line in f:
    line=line.strip()
    line_tokens=line.split()
    e1=line_tokens[0]
    e2=line_tokens[1]
    r=line_tokens[2]
    
    test_sub.append((entity_dict[e1],entity_dict[e2],relation_dict[r]))
    
data[u'test_subs']=test_sub
    

f=open("train.txt")
train_sub=[]

for line in f:
    line=line.strip()
    line_tokens=line.split()
    e1=line_tokens[0]
    e2=line_tokens[1]
    r=line_tokens[2]
    
    train_sub.append((entity_dict[e1],entity_dict[e2],relation_dict[r]))
    
data[u'train_subs']=train_sub


f=open("valid.txt")
valid_sub=[]

for line in f:
    line=line.strip()
    line_tokens=line.split()
    e1=line_tokens[0]
    e2=line_tokens[1]
    r=line_tokens[2]
    
    valid_sub.append((entity_dict[e1],entity_dict[e2],relation_dict[r]))
    
data[u'valid_subs']=valid_sub


pickle.dump( data, open( "FB15K.bin", "wb" ) )

