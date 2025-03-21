import network,gc,utime,ujson,machine
import usocket as Socket
import ssl, uerrno
import ubinascii
import uos,asyncio

class uBot():
    def chip_reset(self):
        self.resetear=True
    class Mensaje():
            esArchivo = False
            cont_archivo = None
            ok = False
            vacio = True 
            indice = 0
            remite = '' 
            remite_id = 0
            isBot = False
            mensaje_id = 0
            texto = ''
            chat_id = 0
            chat_titulo = ''        
            tipo = ''
            tiempo = 0        
    def usock_ssl(self):
#         inicia un socket ssl. si todo va bien retorna el socket, sino retorna None
        if network.WLAN(network.STA_IF).isconnected():
            addr = Socket.getaddrinfo(self.host, 443)[0][-1]
            s0 = Socket.socket()
            s0.connect(addr)
            s0.setblocking(False)
            s = ssl.wrap_socket(s0)
            return s
        else:
            return None
    
    def __init__(self, token, host, funcion):
#         inicia un bot. precisa el token de telegram  y una funcion
#         la funcion 'funcion' es la que sera llamada cuando se reciban datos

        self.token = token
        self.host = host
        self.datos_recibidos = ''
        self.funcion = funcion
        self.id_update = 0
        self.usock = self.usock_ssl()
        #print(self.usock)
        self.timeout = 50
        self.limit = 1
        self.puntero_tiempo = utime.time()
        self.resetear = False
    async def busca_archivo(self,id_archivo):
        peticion=b'GET /bot%s/getFile?file_id=%s HTTP/1.1\r\nHost: api.telegram.org\r\n\r\n'%(self.token, id_archivo)
        self.usock.write(peticion)
    async def pide_archivo(self,path):
        
        peticion = b'GET /file/bot%s/%s HTTP/1.1\r\nHost: api.telegram.org\r\n\r\n'%(self.token, path)
        print(peticion)
        self.usock.write(peticion)

    async def send_message(self,id_canal,mensaje):
#         envia mensaje de texto al canal/usuario elegido
        peticion = b'GET /bot%s/sendMessage?chat_id=%s&parse_mode=HTML&text=%s HTTP/1.1\r\nHost: api.telegram.org\r\n\r\n' %(self.token, id_canal, mensaje)      
        self.usock.write(peticion)
        data = self.usock.read()
        bufer=b'' 
        while data:
            bufer += data
            data = self.usock.read()
        return bufer
     
    def procesa_entrada(self,bufer_de_entrada):
#         procesa la cabecera y retorna el json de la respuesta de servidor
        #print(bufer_de_entrada)
        Archivo = False
        lineas=bufer_de_entrada.decode().split('\n')
        #print(lineas)
        fin_cabecera =0 #para asegurar que fue el fin de cabecera
        for linea in lineas:
            partes_de_linea = linea.split(' ')
            #print(f'---->{partes_de_linea}')
            if partes_de_linea[0] == 'ETag:':
                Archivo = True
            if partes_de_linea[0] == 'HTTP/1.1':
                codigo_pagina = partes_de_linea[1]
                #print('codigo pagina = ',codigo_pagina)
            if partes_de_linea[0] == 'Content-Length:':
                longitud_respuesta = int(partes_de_linea[1])
                print('longitud de respuesta = ',str(longitud_respuesta))
            if partes_de_linea[0] == '':
                #print(f'fc:{fin_cabecera}')
                fin_cabecera +=1
                if fin_cabecera == 1:
#                     retorna la informacion interesante para el bot(el json del mensaje)
                    contenido = self.usock.read(longitud_respuesta)
                    if Archivo:
                        #print('------------------------------es archivo---------------------------------------')
                        contenido=b'#'+contenido
                        Archivo = False
                    return contenido
            else:
                fin_cabecera = 0
                
    async def inicia(self):
#         comienza la comunicacion con telegram y espera mensajes
        esperando_update = False
        while True:
            if esperando_update == False:
                try:
                    gc.collect()
                    self.puntero_tiempo = utime.time()#marca tiempo de peticion para comprobar correcto timeout
                    peticion = b"GET /bot%s/getUpdates?offset=%s&timeout=%s&limit=%s  HTTP/1.1\r\nHost: api.telegram.org\r\n\r\n" %(self.token, str(self.id_update), str(self.timeout), str(self.limit))                       
                    #print(peticion)
                    self.usock.write(peticion)
                    esperando_update=True#Ahora si esta esperando update
                except OSError as exc:
                    print(f'error en inicia: {exc.args[0]}')
                    print('error enviando peticion')
                    self.usock = self.usock_ssl()
                    esperando_update = False
                    print('------------------------------------------------------------------error de envio--------------------------------------------------------------')
                    self.usock.write(peticion)
 
            try:
                data = self.usock.readline()
                bufer = b''
                while True:
                    #print(f'data:{data}')
                    if data == b'' or data == b'\r\n' or data == None:
                        break
                    bufer += data
                    data = self.usock.readline()
                #print(f'bufer:{bufer}')
                if bufer != b'':
                    mensaje_util = self.procesa_entrada(bufer)
                    if mensaje_util.decode()[0] == '#':
                        mensaje_util = mensaje_util[1:]
                        #print(f'contenido de archivo: {mensaje_util}')#enviar a evento
                        arch_obj=self.Mensaje()
                        arch_obj.esArchivo = True
                        arch_obj.cont_archivo = mensaje_util
                        asyncio.create_task(self.funcion(arch_obj, self))
                        bufer=b''
#                     print('-------------------respuesta------------------------',utime.time())
                    #print(f'\n{mensaje_util}\n')
#                     print('--------------------------------------------------')
                    else:
                        bufer = mensaje_util
            except OSError as exc:
                print('error recibiendo datos')
                machine.reset()            
            if bufer != b'' and bufer != None:
                try:
                    retorno = self.obj_msg(ujson.loads(bufer))
                except:
                    print('fallo en json')
                    retorno.vacio = True
                esperando_update= False
                if retorno.vacio == False:
                    print(f'retorno vacio. ID: {retorno.indice}')
                    if retorno.indice != 0:
                        self.id_update = retorno.indice + self.limit
                    asyncio.create_task(self.funcion(retorno, self))#llama al evento de recepcion de datos
            if utime.time() - 55 > self.puntero_tiempo:#si se desbordo oftime.... se resetea el chip(por desarrollar este punto)
                self.usock = self.usock_ssl()
                esperando_update = False
                print('----------------------------------------------------------------------timeout-------------------------------------------------------------------------')
            await asyncio.sleep(0)

            
    
    def obj_msg(self,x):
        print(f'mensaje: {x}')
        
        mensaje=self.Mensaje()
        try:
            mensaje.ok = x['ok']
            resultado=x['result']
            if isinstance(x['result'],list):
                if resultado != []:
                    mensaje.vacio = False
                    resultado = x['result'][0]
                    mensaje.indice = resultado['update_id']
                    if 'message' in resultado.keys():
                        resultado = resultado['message']
                        mensaje.remite = resultado['from']['username']
                        mensaje.remite_id = resultado['from']['id']
                        mensaje.isBot = resultado['from']['is_bot']
                    if 'channel_post' in resultado.keys():
                        resultado = resultado['channel_post']
                        mensaje.remite = resultado['sender_chat']['title']
                        mensaje.remite_id = resultado['sender_chat']['id']
                        mensaje.isBot = False
                    mensaje.mensaje_id = resultado['message_id']
                    if 'text' in resultado.keys():
                        mensaje.texto = resultado['text']
                    if 'document' in resultado.keys():
                        mensaje.texto = resultado['document']['file_id']
                        asyncio.create_task(self.busca_archivo(mensaje.texto))
                    mensaje.tipo = resultado['chat']['type']
                    mensaje.tiempo = resultado['date']
                    mensaje.chat_id = resultado['chat']['id']
                    if mensaje.tipo == 'private' or mensaje.tipo =='bot_command':
                        mensaje.chat_titulo = resultado['chat']['username']
                    if mensaje.tipo == 'supergroup' or mensaje.tipo == 'group':
                        mensaje.chat_titulo = resultado['chat']['title']
                else:
                    mensaje.vacio=True
            else:#estos son mis envios o recepcion de archivos
                if 'file_path' in resultado.keys():
                    asyncio.create_task(self.pide_archivo(resultado['file_path']))
                else:    
                    mensaje.mensaje_id = resultado['message_id']
                    mensaje.tipo = 'enviado'
                    mensaje.texto = resultado['text']
                    if mensaje.tipo == 'private' or mensaje.tipo =='bot_command':
                            mensaje.chat_titulo = resultado['chat']['username']
                    if mensaje.tipo == 'supergroup' or mensaje.tipo == 'group':
                            mensaje.chat_titulo = resultado['chat']['title']
        except:
            print('problema con json')
            pass
        return mensaje

    async def envia_archivo_multipart(self,canal_id,arch,comando,nombre,comentario=''):
        limite = ubinascii.hexlify(uos.urandom(16)).decode('ascii')
        cadenados = b'--'
        cadenados += limite
        cadenados += '\r\n'
        cadenados += b'content-disposition: form-data; name= "chat_id"\r\n\r\n'
        cadenados += canal_id
        cadenados += b'\r\n--'
        cadenados += limite
        cadenados += b'\r\n'
        if comentario != '':
            cadenados += b'content-disposition: form-data; name= "caption"\r\n\r\n'
            cadenados += comentario
            cadenados += b'\r\n--'
            cadenados += limite
            cadenados += b'\r\n'    
        cadenados += b'content-disposition: form-data; name= "'
        cadenados += nombre
        cadenados += b'"; filename= "file.jpg"\r\n'
        cadenados += b'Content-Type: image-jpeg\r\n\r\n'
        cadenatres= b'\r\n--'
        cadenatres += limite
        cadenatres += b'--\r\n'
        gc.collect()
        x = uos.stat(arch)
        tamarch = x[6]
        Tamanyo_total=str(tamarch+len(cadenados)+len(cadenatres))
        archivo = ""
        gc.collect()
        cadenainicio = b'POST /bot'
        cadenainicio += self.token
        cadenainicio += b'/'
        cadenainicio += comando
        cadenainicio += b' HTTP/1.1\r\n'
        cadenainicio += b'Host: api.telegram.org\r\n'
        cadenainicio += b'User-Agent: KmiZbot/v1.0\r\n'
        cadenainicio += b'Accept: */*\r\n'
        cadenainicio += b'Content-Length: '
        cadenainicio += Tamanyo_total
        cadenainicio += b'\r\n'
        cadenainicio += b'Content-Type: multipart/form-data; boundary='
        cadenainicio += limite
        cadenainicio += b'\r\n\r\n'
        self.usock.write(cadenainicio)                                                  
        self.usock.write(cadenados)                                                      
        f = open(arch, "rb")
        contenido = bytearray(f.read(512),'utf-8')
        while contenido:
            self.usock.write(contenido)
            contenido = bytearray(f.read(512),'utf-8')
            gc.collect()
            await asyncio.sleep(0)
        f.close()
        self.usock.write(cadenatres)
        gc.collect()
        data = self.usock.readline()
        while data:
#             if '200 OK' in data:break
            data = self.usock.readline()
            await asyncio.sleep(0)
        
        print(f'{'_'*90}\r\n{'_'*43}data{'_'*43}\r\n{data}\r\n{'_'*90}')

    