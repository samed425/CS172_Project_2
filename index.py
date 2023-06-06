import logging, sys
logging.disable(sys.maxsize)

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

def index(input_dir, index_dir):
    lucene.initVM()
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    index_dir = SimpleFSDirectory(Paths.get(index_dir))
    writer = IndexWriter(index_dir, config)

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r') as file:
            json_data = json.load(file)

            for key, json_object in json_data.items():
                doc = Document()

                # Extract fields from the JSON object
                id = json_object.get('id', '')
                subreddit = json_object.get('subreddit', '')
                title = json_object.get('title', '')
                author = json_object.get('author', '')
                time = json_object.get('time', '')
                permalink = json_object.get('permalink', '')
                #sublink = json_object.get('sublink', '')
                #sublink_title = json_object.get('sublink-title', '')
                #sublink_body = json_object.get('sublink-body', '')
                body = json_object.get('body', '')
                #num_comments = json_object.get('numComments', '')
                #comments = json_object.get('comments', '')
                score = json_object.get('score', '')
                upvote = json_object.get('upvoteRatio', '')
                #upvote_ratio = json_object.get('upvoteRatio', '')

                 # Create Lucene fields and add them to the document
                doc.add(StringField('id', id, Field.Store.YES))
                doc.add(StringField('subreddit', subreddit, Field.Store.YES))
                doc.add(StringField('title', title, Field.Store.YES))
                doc.add(StringField('author', author, Field.Store.YES))
                doc.add(StringField('time', time, Field.Store.YES))
                doc.add(StringField('permalink', permalink, Field.Store.YES))
                doc.add(StringField('upvote', upvote, Field.Store.YES))
                #doc.add(StringField('sublink', sublink, Field.Store.YES))
                #doc.add(StringField('sublink-title', sublink_title, Field.Store.YES))
                #doc.add(StringField('sublink-body', sublink_body, Field.Store.YES))
                doc.add(TextField('body', body, Field.Store.YES))
                #doc.add(StringField('numComments', num_comments, Field.Store.YES))
                #doc.add(TextField('comments', comments, Field.Store.YES))
                doc.add(StringField('score', score, Field.Store.YES))
                #doc.add(StringField('upvoteRatio', upvote_ratio, Field.Store.YES))
                writer.addDocument(doc)

    writer.commit()
    writer.close()

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

    return topkdocs


index('input/', 'indexNew')
print(retrieve('indexNew', 'programming'))
