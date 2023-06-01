import json
import sys
import lucene
import os

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from java.nio.file import Paths

def index_json_objects(input_dir, index_dir):
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
                num_comments = json_object.get('numComments', '')
                comments = json_object.get('comments', '')
                score = json_object.get('score', '')
                upvote_ratio = json_object.get('upvoteRatio', '')

                 # Create Lucene fields and add them to the document
                doc.add(StringField('id', id, Field.Store.YES))
                doc.add(StringField('subreddit', subreddit, Field.Store.YES))
                doc.add(StringField('title', title, Field.Store.YES))
                doc.add(StringField('author', author, Field.Store.YES))
                doc.add(StringField('time', time, Field.Store.YES))
                doc.add(StringField('permalink', permalink, Field.Store.YES))
                #doc.add(StringField('sublink', sublink, Field.Store.YES))
                #doc.add(StringField('sublink-title', sublink_title, Field.Store.YES))
                #doc.add(StringField('sublink-body', sublink_body, Field.Store.YES))
                doc.add(TextField('body', body, Field.Store.YES))
                doc.add(StringField('numComments', num_comments, Field.Store.YES))
                doc.add(TextField('comments', comments, Field.Store.YES))
                doc.add(StringField('score', score, Field.Store.YES))
                doc.add(StringField('upvoteRatio', upvote_ratio, Field.Store.YES))
                writer.addDocument(doc)

    writer.commit()
    writer.close()

index_json_objects('input', 'index')