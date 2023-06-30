from fastapi import FastAPI, HTTPException
from typing import List
from Models.sentences import Sentence
from Models.stats import StatsUser
from Models_IA.service import IAservices
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, paginate

from Repository.main import FireRepository

app = FastAPI()

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:4200",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
repo = FireRepository()


# Resto del código de tu aplicación FAST API

@app.post("/subir/{user_id}")
def set_comentarios(user_id,comentarios:List[Sentence]):
    repo.set_prediciones(user_id,comentarios)
    stats = StatsUser()
    repo.set_stats(user_id,stats)
    return HTTPException(status_code=200, detail="Comentarios subidos")


@app.get("/detTemas/{user_id}/{numTemas}")
def text_topics(user_id,numTemas : int):
    model =  IAservices()
    comentarios = repo.get_predicciones(user_id)
    resultados, user_stats = model.topic_modeling(comentarios,user_id,numTemas)
    json_resultados = jsonable_encoder(resultados)
    repo.update_predicciones(user_id,resultados)
    repo.update_stats(user_id,user_stats)
    return json_resultados

@app.get("/temas/{user_id}/{numwords}")
def get_text_topics(user_id,numwords:int):
    model = IAservices()
    resultados = model.get_topics(user_id,numwords)
    json_resultados = jsonable_encoder(resultados)
    return json_resultados

@app.post("/temas/comentarios/{user_id}/{numwords}")
def get_temas_by_comentarios(user_id,numwords:int, ids:List[str],filtro:List[int]):
    model = IAservices()
    temas = model.get_topics(user_id,numwords)
    return repo.get_temas_by_comentarios(user_id,ids,temas,filtro)

@app.get("/canttemas/{user_id}")
def get_text_topics(usert_id):
    model = IAservices()
    resultados = model.get_num_topics(usert_id)
    json_resultados = jsonable_encoder(resultados)
    return json_resultados

@app.get("/stats/{user_id}")
def text_clasificador(user_id):
    return repo.get_stats(user_id)

# Obtener todas las oraciones
@app.get("/comentarios/{user_id}", response_model=List[Sentence])
def get_sentences(user_id: str):
    sentences = repo.get_predicciones(user_id)
    return sentences

# Obtener una oración por su ID
@app.get("/comentarios/{user_id}/{sentence_id}", response_model=Sentence)
def get_sentence(user_id: str,sentence_id: str):
    sentence = repo.get_prediccion(user_id,sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Comentarios no encontrados")
    return sentence

# Actualizar oraciones existentes
@app.put("/comentarios/{user_id}")
def update_sentences(user_id: str ,sentences: List[Sentence]):
    updated_sentences = repo.update_predicciones(user_id,sentences)
    if not updated_sentences:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    return updated_sentences

# Eliminar oraciones
@app.delete("/delete/{user_id}/{sentence_id}")
def delete_sentences(user_id: str, sentence_id: str):
    deleted = repo.deled_prediccion(user_id, sentence_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")