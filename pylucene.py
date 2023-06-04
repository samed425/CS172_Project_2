import logging, sys
logging.disable(sys.maxsize)

import json
import lucene
import os
import ast
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity


def create_index(index_dir, input_dir):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    store = SimpleFSDirectory(Paths.get(index_dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    metaType = FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)

    contextType = FieldType()
    contextType.setStored(True)
    contextType.setTokenized(True)
    contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        document = []
        with open(file_path, 'r') as file:
            document = json.load(file)
            for sample in document:
                id = sample['id']
                subreddit = sample['subreddit']
                title = sample['title']
                author = sample['author']
                time = sample['time']
                permalink = sample['permalink']
                body = sample['body']

                doc = Document()
                doc.add(Field('id', str(id), contextType))
                doc.add(Field('subreddit', str(subreddit), contextType))
                doc.add(Field('title', str(title), contextType))
                doc.add(Field('author', str(author), contextType))
                doc.add(Field('time', str(time), contextType))
                doc.add(Field('permalink', str(permalink), contextType))
                doc.add(Field('body', str(body), contextType))
                writer.addDocument(doc)
    writer.close()


def retrieve(storedir, query):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    parser = QueryParser('body', StandardAnalyzer())
    parsed_query = parser.parse(query)

    topDocs = searcher.search(parsed_query, 10).scoreDocs
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            "title": doc.get("title"),
            #"subreddit": doc.get("subreddit"),
            #"author": doc.get("author"),
            #"timestamp": doc.get("time"),
            #"permalink": doc.get("permalink"),
            #"text": doc.get("body")
        })
    
    print(topkdocs)



lucene.initVM(vmargs=['-Djava.awt.headless=true'])
create_index('sample_lucene_index/', 'input/')

#retrieve('index', 'test')


