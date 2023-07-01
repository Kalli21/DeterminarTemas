import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from gensim import models
from gensim import corpora
import os
import math

import numpy as np

class DeterminadorTemas:
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.model = None
    
    def _process_text(self, text):
        text = re.sub('[^A-Za-z]', ' ', text.lower())
        tokenized_text = word_tokenize(text)
        clean_text = [
            self.stemmer.stem(word) for word in tokenized_text
            if word not in stopwords.words('english')
        ]
        return clean_text    
    

    def crear_modelo(self, comentarios, cant_topics=20):
        processed_comments = [self._process_text(comment) for comment in comentarios]
        dictionary = corpora.Dictionary(processed_comments)
        corpus = [dictionary.doc2bow(text) for text in processed_comments]
        
        self.model = models.ldamodel.LdaModel(corpus, num_topics=cant_topics, id2word=dictionary, passes=15)
        
        distribuciones_de_topicos = [self.model.get_document_topics(documento) for documento in corpus]
        return distribuciones_de_topicos
        
    def guardar_modelo(self, username):
        if self.model:
            ruta_carpeta_usuario = os.path.join("Models_IA", "DetTemas", username)
            
            if not os.path.exists(ruta_carpeta_usuario):
                os.makedirs(ruta_carpeta_usuario)
            else:
                for archivo in os.listdir(ruta_carpeta_usuario):
                    archivo_path = os.path.join(ruta_carpeta_usuario, archivo)
                    if os.path.isfile(archivo_path):
                        os.remove(archivo_path)
                        
            ruta_modelo_lda = os.path.join(ruta_carpeta_usuario, "modelo_lda_guardado")
            self.model.save(ruta_modelo_lda)
            return True
        else:
            return False
        
    def cargar_modelo(self, username):
        ruta_carpeta_usuario = os.path.join("Models_IA", "DetTemas", username)
            
        if not os.path.exists(ruta_carpeta_usuario):
            return False
        else:
            ruta_modelo_lda = os.path.join(ruta_carpeta_usuario, "modelo_lda_guardado")
            self.model = models.LdaModel.load(ruta_modelo_lda)
            return True
        
    def distribucion_temas(self, comentarios):
        if self.model:
            text_procesado = [self._process_text(comment) for comment in comentarios]
            dictionary = self.model.id2word
            
            nuevo_corpus = [dictionary.doc2bow(texto) for texto in text_procesado]

            distribuciones_de_topicos = [self.model.get_document_topics(documento) for documento in nuevo_corpus]
            return distribuciones_de_topicos
        else:
            return False
        
    def get_numero_topicos(self):
        if self.model:
            return self.model.num_topics
        else:
            return -1
    
    def get_topics(self, numwords):
        if self.model:
            topics = self.model.print_topics(num_words=numwords)
            return topics
        else:
            return []
