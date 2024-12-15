from math import ceil
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import List
from Models.infoGrafProducto import InfoGrafProducto
from fastapi.encoders import jsonable_encoder
from Models.sentences import Sentence
from Models.stats import StatsUser, BaseStats

from google.cloud.firestore import FieldFilter
from Models.request.filtroComentario import  FiltroSentences, InfoGrafGeneral


class FireRepository():

    cred = credentials.Certificate("credenciales/topics-ts-firebase-adminsdk-17azr-65b7afd9d5.json")
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    
    def get_stats(self,user_id):
        return self.db.collection('usuarios').document(user_id).get().to_dict() 
        
    def set_stats(self,user_id,stats:StatsUser):
        return self.db.collection('usuarios').document(user_id).set(stats.dict())
                
    def update_stats(self,user_id,stats:StatsUser):
        # Convierte el objeto StatsUser a un diccionario serializable
        stats_dict = jsonable_encoder(stats)        
        # Actualiza el documento en Firestore
        self.db.collection('usuarios').document(user_id).update(stats_dict)
    
    def update_base_stats(self,user_id,stats:BaseStats):
        # Convierte el objeto StatsUser a un diccionario serializable
        stats_dict = jsonable_encoder(stats)        
        # Actualiza el documento en Firestore
        self.db.collection('usuarios').document(user_id).update(stats_dict)
        
    def set_prediciones(self,user_id,comentarios: List[Sentence]):
        batch = self.db.batch()
        sentences_collection = self.db.collection('usuarios').document(user_id).collection('comentarios')  # Se obtiene una referencia de documento para la colección

        for comentario in comentarios:
            doc_ref = sentences_collection.document(comentario.id)  # Obtener una referencia de documento única para cada objeto Sentence
            batch.set(doc_ref, comentario.dict())

        batch.commit()
        return sentences_collection.id

    def get_predicciones(self, user_id, filtro: FiltroSentences  = None):
        sentences = []
        docs = self.db.collection('usuarios').document(user_id).collection('comentarios')
        
        if filtro:
            if len(filtro.listId)>0: docs = docs.where(filter = FieldFilter('id', 'in', filtro.listId))
            if filtro.fechaIni: docs = docs.where(filter = FieldFilter('fecha', '>=', filtro.fechaIni))
            if filtro.fechaFin: docs = docs.where(filter = FieldFilter('fecha', '<=', filtro.fechaFin))
            if len(filtro.temasId)>0: docs = docs.where(filter = FieldFilter('tema', 'in', filtro.temasId))
        
        if filtro and filtro.min_info: 
            docs = docs.select(['id','tema']).get()
        else:
            docs = docs.get()
            
        for doc in docs:
            sentence_data = doc.to_dict()  # Obtener los datos del documento como un diccionario
            sentence = Sentence(**sentence_data)  # Crear una instancia de Sentence usando los datos del documento            
            sentences.append(sentence)

        return sentences

    def get_prediccion(self,user_id,coment_id):
        collection_ref = self.db.collection('usuarios').document(user_id).collection('comentarios')
        return collection_ref.document(coment_id).get().to_dict() 

    def update_predicciones(self,user_id: str, comentarios: List[Sentence]):
        # batch = self.db.batch()

        # for sentence in comentarios:
        #     # Excluir el campo 'id' del diccionario de datos
        #     sentence_data = sentence.dict(exclude={'id'})
        #     doc_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').document(sentence.id)
        #     batch.update(doc_ref, sentence_data)

        # batch.commit()
        # return comentarios
        MAX_BATCH_SIZE = 500  # Tamaño máximo del lote

        # Dividir los comentarios en lotes más pequeños
        num_batches = ceil(len(comentarios) / MAX_BATCH_SIZE)
        batches = [comentarios[i:i+MAX_BATCH_SIZE] for i in range(0, len(comentarios), MAX_BATCH_SIZE)]

        for batch in batches:
            batch_update = self.db.batch()

            for sentence in batch:
                sentence_data = sentence.dict(exclude={'id'})
                doc_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').document(sentence.id)
                batch_update.update(doc_ref, sentence_data)

            batch_update.commit()

        return comentarios

    def deled_prediccion(self,user_id,coment_id):
        comment_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').document(coment_id)
        comment_doc = comment_ref.get()

        if comment_doc.exists:
            comment_ref.delete()
            return True
        else:
            return False

    def delete_user(self, user_id):
        # Obtén una referencia al documento principal
        user_ref = self.db.collection('usuarios').document(user_id)

        # Verifica si el documento existe
        if user_ref.get().exists:
            # Elimina las subcolecciones usando lotes
            self._delete_subcollections_in_batches(user_ref)

            # Elimina el documento principal
            user_ref.delete()
            return True
        else:
            return False

    def _delete_subcollections_in_batches(self, document_ref):
        # Obtén todas las subcolecciones
        subcollections = document_ref.collections()

        for subcollection in subcollections:
            while True:
                # Obtén hasta 500 documentos de la subcolección
                docs = list(subcollection.limit(500).stream())

                if not docs:
                    break  # Si no hay más documentos, termina el ciclo

                # Inicia un batch
                batch = self.db.batch()

                # Añade cada documento al batch para eliminar
                for doc in docs:
                    batch.delete(doc.reference)

                # Ejecuta el batch
                batch.commit()
    
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
    
###### SET INFOR

    async def clear_and_set_info(self, user_id: str, coll : str, list_info: InfoGrafGeneral):
        # Obtiene la referencia de la subcolección
        subcollection_ref = self.db.collection('usuarios').document(user_id).collection(coll)

        # 1. Elimina todos los documentos en la subcolección
        await self._clear_subcollection(subcollection_ref)
        
        body = list_info.dict()
        subcollection_ref.add(body)
        
        return f"Se inserto informacion de {coll}"

    async def _clear_subcollection(self, subcollection_ref):
        # Obtiene todos los documentos de la subcolección
        docs = subcollection_ref.stream()
        # Elimina cada documento encontrado
        for doc in docs:
            doc.reference.delete()
            