from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
import logging, sys
logging.disable(sys.maxsize)
from django.conf import settings
import json
import lucene
import os
import ast
 
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity
from java.nio.file import Paths


def mainPageRender(request):
    query = request.POST.get('query')
    print(query)
    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()
    if query == None:
        #rendering empty page when there's no page to display
        return render(request, 'index.html', context={'posts': []})
    else:
        print(query)
    #setting values for ordering based on
    orderRel = request.POST.get('relevance') == '1'
    orderUpvote = request.POST.get('Upvote') == '1'
    orderDate = request.POST.get('date') == '1'
    posts = FindPosts(query, orderRel, orderUpvote, orderDate)
    #Render the result of the query
    return render(request, 'index.html', context={'posts': posts})


#Finding the top 10 search result
def FindPosts(query, orderRel, orderUpvote, orderDate):
    if query == None or IsSpace(query):
        return []
    static_folder = os.path.join(settings.BASE_DIR, 'indexNew')
    posts = retrieve(static_folder, query)
    posts = Wrapper(posts, orderRel, orderUpvote, orderDate)
    print('Unsorted list:--------\n\n',posts, '\n\n')
    sorted_list = sorted(posts, key=lambda x: x[1], reverse=True)
    print('Sorted list:--------\n\n',sorted_list, '\n\n')
    posts = [t[0] for t in sorted_list]
    print(posts, '\n\n')
    return posts

#Checking if the query is empty
def IsSpace(text):
    for i in text:
        if i != ' ':
            return False
    return True

def Wrapper(rawPosts,orderRel, orderUpvote, orderDate):
    newPosts = []
    maxUpvote = 0
    maxDate = 0
    maxRelev = 0
    for i in rawPosts:
        if maxDate < float(i['timestamp']):
            maxDate =float(i['timestamp'])
        if maxRelev < i['BM25']:
            maxRelev = i['BM25']
        if maxUpvote < float(i['upvote']):
            maxUpvote = float(i['upvote'])
    for post in rawPosts:
        newPosts.append((post['permalink'], post['BM25'] * orderRel/maxRelev + float(post['timestamp'])* orderDate/maxDate + float(post['upvote']) * orderUpvote/ maxUpvote))
    return newPosts

def retrieve(storedir, query):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))

    parser = QueryParser('body', StandardAnalyzer())
    parsed_query = parser.parse(query)
    count = 0
    list = []
    topDocs = searcher.search(parsed_query, 1000).scoreDocs
    topkdocs = []
    for hit in topDocs:
        if (hit.score in list):
            continue
        else:
            list.append(hit.score)
            count = count + 1
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "BM25": hit.score,
            "title": doc.get("title"),
            #"subreddit": doc.get("subreddit"),
            #"author": doc.get("author"),
            "timestamp": doc.get("time"),
            "permalink": doc.get("permalink"),
            "upvote" : doc.get("upvote")
            #"text": doc.get("body")
        })
        if count == 10:
            break

    #print (topkdocs)
    #print('Top 10 Documents: ')
    #for i in range(len(topkdocs)):
        #position = i + 1
        #print(str(position) + ') ' + str(topkdocs[i]))
    return topkdocs

