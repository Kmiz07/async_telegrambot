import json,os,machine
path="datos.json"
#configuracion={}
def crea(dic_datos):#rellena archivo de configuracion desde un diccionario
    global path
    with open(path,'w')as archivo:
        json.dump(dic_datos,archivo)
        
if not path in os.listdir():crea({})
    
def recupera():#retorna un diccionario con las variables y sus valores
    global path
    with open(path) as archivo:
        return json.load(archivo)
def lee(nombre):#retorna el valor correspondiente al key
    dic_datos=recupera()
    if nombre in dic_datos.keys():
        return dic_datos[nombre]
    else:
        return None
        
    
def entra(nombre,valor):#añade una variable y su valor al diccionario
    dic_datos=recupera()
    dic_datos[nombre]=valor
    crea(dic_datos)
    
def elimina(nombre):#elimina una key y su valor
    dic_datos=recupera()
    if nombre in dic_datos.keys():
        del dic_datos[nombre]
        crea(dic_datos)
    
def lista():#imprime el diccionario con los keys y valores
    print(recupera())

def reinicia(): #reinicia el sistema
    machine.reset()

def guarda(texto):#rellena el archivo de configuracion desde un texto
    global path
    try:
        prueba=json.loads(texto)
        with open(path,'w')as archivo:
            archivo.write(texto)
        return True 
    except Exception as exc:
        return False 
