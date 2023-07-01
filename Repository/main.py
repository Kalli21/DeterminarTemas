import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import List
from Models.infoGrafProducto import InfoGrafProducto

from Models.sentences import Sentence
from Models.stats import StatsUser


class FireRepository():

    cred = credentials.Certificate("credenciales/topics-ts-firebase-adminsdk-17azr-65b7afd9d5.json")
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    
    def get_stats(self,user_id):
        return self.db.collection('usuarios').document(user_id).get().to_dict() 
        
    def set_stats(self,user_id,stats:StatsUser):
        return self.db.collection('usuarios').document(user_id).set(stats.dict())
        
        
    def update_stats(self,user_id,stats:StatsUser):
        return self.db.collection('usuarios').document(user_id).update(stats.dict())
        

    def set_prediciones(self,user_id,comentarios: List[Sentence]):
        batch = self.db.batch()
        sentences_collection = self.db.collection('usuarios').document(user_id).collection('comentarios')  # Se obtiene una referencia de documento para la colección

        for comentario in comentarios:
            doc_ref = sentences_collection.document(comentario.id)  # Obtener una referencia de documento única para cada objeto Sentence
            batch.set(doc_ref, comentario.dict())

        batch.commit()
        return sentences_collection.id

    def get_predicciones(self,user_id):
        sentences = []
        collection_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').get()

        for doc in collection_ref:
            sentence_data = doc.to_dict()  # Obtener los datos del documento como un diccionario
            sentence = Sentence(**sentence_data)  # Crear una instancia de Sentence usando los datos del documento
            sentences.append(sentence)

        return sentences

    def get_prediccion(self,user_id,coment_id):
        collection_ref = self.db.collection('usuarios').document(user_id).collection('comentarios')
        return collection_ref.document(coment_id).get().to_dict() 

    def update_predicciones(self,user_id: str, comentarios: List[Sentence]):
        batch = self.db.batch()

        for sentence in comentarios:
            # Excluir el campo 'id' del diccionario de datos
            sentence_data = sentence.dict(exclude={'id'})
            doc_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').document(sentence.id)
            batch.update(doc_ref, sentence_data)

        batch.commit()
        return comentarios


    def deled_prediccion(self,user_id,coment_id):
        comment_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').document(coment_id)
        comment_doc = comment_ref.get()

        if comment_doc.exists:
            comment_ref.delete()
            return True
        else:
            return False

    
    def get_temas_by_comentarios(self,user_id,ids,temas,filtro):
        resp = InfoGrafProducto()
        listTemas = []
        listIds = []
        listComents = []    
        
        if not filtro or len(filtro) == 0:
            filtro = list(range(len(temas))) 
        
        for i in ids:
            coment = self.get_prediccion(user_id, i)
            if coment:
                coment_temas = coment.get('temas')
                diccionario_numeros = {clave: float(valor) for clave, valor in coment_temas.items()}
                if diccionario_numeros:
                    clave_max = max(diccionario_numeros, key=diccionario_numeros.get)
                else:
                    # Manejo de la secuencia vacía, según sea apropiado para tu aplicación
                    clave_max = -1
                if int(clave_max) in filtro:
                    if clave_max not in listIds:                    
                        listIds.append(clave_max)
                    listComents.append(coment['id'])
        for i in listIds:
            listTemas.append(temas[int(i)])

        resp.temas = listTemas
        resp.comentariosId = listComents
        return resp
