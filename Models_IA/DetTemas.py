import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize #Libreria para la tokenizacion de las palabras
from nltk.corpus import stopwords #Librerias para ls stopwords o palabras sin significado
from nltk.stem.porter import PorterStemmer

from gensim import models
from gensim import corpora
import os

import multiprocessing
import math

total_cores = multiprocessing.cpu_count()
half_cores = math.floor(total_cores / 2)

os.environ['OMP_NUM_THREADS'] = str(half_cores)

import multiprocessing
from multiprocessing import Pool


class determinador_temas:    
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.model = None
    
    def _process_text(self,text):
        
        # eliminamos caracteres especiales
        text = re.sub('[^A-Za-z]', ' ', text.lower())

        tokenized_text = word_tokenize(text)

        #Removemos los stopwords y reducimos las palabras a su raiz
        clean_text = [
            self.stemmer.stem(word) for word in tokenized_text
            if word not in stopwords.words('english')
        ]

        return clean_text    
    

    def _procesador_multicor(self,comentarios):

        with Pool() as pool:
            processed_comments = pool.map(self._process_text, comentarios)

        return processed_comments
    
    def crear_modelo(self,comentarios,cant_topics=20):
        
        processed_comments = self._procesador_multicor(comentarios)
        dic = corpora.Dictionary(processed_comments)
        corpus = [dic.doc2bow(text) for text in processed_comments]
        
        self.model = models.ldamodel.LdaModel(corpus, num_topics=cant_topics, id2word=dic, passes=15)
        
        # obtener las distribuciones de tópicos de los  documentos
        distribuciones_de_topicos = [self.model.get_document_topics(documento) for documento in corpus]
        return distribuciones_de_topicos
        
    def guardar_modelo(self,username):
        
        if self.model :            
        
            ruta_carpeta_usuario = os.path.join("Models_IA", "DetTemas", username)
            
            # Valida si la carpeta del usuario existe
            if not os.path.exists(ruta_carpeta_usuario):
                # Crea la carpeta del usuario si no existe
                os.makedirs(ruta_carpeta_usuario)
            else:
                # Elimina el contenido de la carpeta si ya existe
                for archivo in os.listdir(ruta_carpeta_usuario):
                    archivo_path = os.path.join(ruta_carpeta_usuario, archivo)
                    if os.path.isfile(archivo_path):
                        os.remove(archivo_path)
                        
            ruta_modelo_lda = os.path.join(ruta_carpeta_usuario, "modelo_lda_guardado")
            self.model.save(ruta_modelo_lda)
            #se guardo con exito el modelo
            return True
        else:
            #el modelo no existe
            return False
        
    def cargar_modelo(self,username):
        
        ruta_carpeta_usuario = os.path.join("Models_IA", "DetTemas", username)
            
        # Valida si la carpeta del usuario existe
        if not os.path.exists(ruta_carpeta_usuario):
            #no existe la carperta, no hay modelo guardado
            return False
        else:
            ruta_modelo_lda = os.path.join(ruta_carpeta_usuario, "modelo_lda_guardado")
            self.model = models.LdaModel.load(ruta_modelo_lda)
            #se cargo el modelo con exito
            return True
        
    def distribucion_temas(self,comentarios):
        if self.model:
            text_procesado = self._procesador_multicor(comentarios)
            diccionario = self.model.id2word
            
            # crear un nuevo corpus utilizando el mismo diccionario
            nuevo_corpus = [diccionario.doc2bow(texto) for texto in text_procesado]

            # obtener las distribuciones de tópicos de los nuevos documentos
            distribuciones_de_topicos = [self.model.get_document_topics(documento) for documento in nuevo_corpus]
            return distribuciones_de_topicos
        else:
            #no hay modelo cargado
            return False
        
    def get_numero_topicos(self):
        if self.model:
            return self.model.num_topics
        else:
            return -1
    
    def get_topics(self,numwords):
        if self.model:
            # Obtener los temas como una lista de tuplas (tópico, palabras_principales)
            topics = self.model.print_topics(num_words=numwords)

            # Convertir los temas en una lista
            # lista_temas = [topic[1] for topic in topics]
            
            return topics
        else:
            return []