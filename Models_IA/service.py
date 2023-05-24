
from Models.sentences import Sentence
from Models_IA.DetTemas import determinador_temas
import numpy as np
import ast

class IAservices():

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
    
    def topic_modeling(self,comentarios,ids,username,numTemas):
        model =  determinador_temas()
        arr_coment = np.array(comentarios)
        result_np = model.crear_modelo(arr_coment,cant_topics=numTemas)  
        model.guardar_modelo(username)       
        
        result = []
        i=0
        for c in comentarios:
            coment = Sentence(text = c)
            coment.id = ids[i]
            coment.temas = self._trans_list_dic(result_np[i])            
            i+=1
            result.append(coment)
        return result
    
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
            