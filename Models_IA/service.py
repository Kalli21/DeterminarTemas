
from Models.sentences import Sentence
from Models.stats import BaseStats
from Models_IA.DetTemas import determinador_temas
import numpy as np
import ast

class IAservices():

    def topic_modeling(self,comentarios,username,numTemas, ini_stats: BaseStats = None):
        model =  determinador_temas()
        com_text = self._trans_comentarios(comentarios)
        arr_coment = np.array(com_text)
        result_np = model.crear_modelo(arr_coment,cant_topics=numTemas)  
        model.guardar_modelo(username)       
        
        if ini_stats:
            stats = BaseStats(**ini_stats)
        else:
            stats = BaseStats()
        
        i=0
        for c in comentarios:
            c.temas = self._trans_list_dic(result_np[i])
            c.tema = int(max(c.temas, key=c.temas.get))      
            i+=1
        stats.total += i    
        return comentarios, stats
    
    def get_topics(self,username,numwords):
        model = determinador_temas()
        model.cargar_modelo(username)
        result = model.get_topics(numwords)
        
        aux_dic = {}
        
        if len(result) != 0:
            aux_dic = self._trans_list_dic_str(result)
        
        return aux_dic
    
    def get_num_topics(self,username):
        model = determinador_temas()
        model.cargar_modelo(username)
        return model.get_numero_topicos()
    
# metodos privados            
    def _trans_list_dic(self,lista_tuplas):
        diccionario = {}
        for par in lista_tuplas:
            clave = par[0]
            valor = par[1]
            diccionario[str(clave)] = str(valor)
        return diccionario
    
    def _trans_str_dic(self,list_str,separador):    
        result_dict = {}

        for group in list_str:
            key_value = group.split(separador)
            key = key_value[0]
            value = ast.literal_eval(key_value[1].strip())
            result_dict[key] = value

        return result_dict
    
    def _trans_list_dic_str(self,lista_Tuplas):
        result_dict = {}

        for item in lista_Tuplas:
            groups = item[1].split(" + ")
            val = self._trans_str_dic(groups,"*")
            result_dict[item[0]] = val
        return result_dict
    
    def _trans_comentarios(self,comentarios):
        list_text = []
        for c in comentarios:
            list_text.append(c.text)
        return list_text