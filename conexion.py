import confjson,gc,utime,uPYbot
import machine, esp32, ure
from machine import Pin
from utime import sleep
import asyncio
#######################################################################################
#             EVENTOS BOT (Nombres de eventos definidos al declarar el Bot            #
#######################################################################################

configuracion=confjson.recupera()  
continua=True
async def evento_recepcion(datos_recibidos, miBot):
#         Si dattos_recibidos es None en archivo deberia haber el contenido de un archivo
#     pass
#         Esta funcion funciona como un evento de recepcion de get_updates.
#         En datos_recibidos, recibimos un objeto mensaje con la siguiente estructura:
#         ok = boolean que define si la respuesta fue satisfactoria.
#         vacio = boolean que dice si el mensaje es vacio 
#         indice = indice del mensaje
#         remite = nombre del remitente
#         remite_id = id del remitente
#         texto = texto del mensaje
#         chat_id = id del canal
#         chat_titulo = si venia de un canal, el titulo del mismo       
#         tipo = sera private si es mensaje privado o supergroup si viene de un canal
#         tiempo = puntero del tiempo del momento de la creacion del mensaje. esta definido desde el 1 de 1 de 2000, normalmente marcara 30 años mas
#         en miBot nos llega una referencia al bot creado.
    if datos_recibidos:
        print(f'recibido->  {datos_recibidos.texto}<<<')
        print(f'esArchivo = {datos_recibidos.esArchivo}')
        if datos_recibidos.esArchivo:
            print(f' el archivo es:\n{datos_recibidos.cont_archivo}')
        elif datos_recibidos.texto == 'getID':
            await miBot.send_message(datos_recibidos.remite_id,f'El id del canal {datos_recibidos.chat_titulo} es {datos_recibidos.chat_id}')
    

    
    
################################################################################################
#                                 FIN EVENTOS BOT                                              #
################################################################################################
async def main():
    Bot=uPYbot.uBot(configuracion['Telegram_Bot'],'api.telegram.org', evento_recepcion)
    Bot.send_message(configuracion['Chat_Id'],'Se ha iniciado programa')
    asyncio.create_task(Bot.inicia())
    while continua:
        #este es el bucle de programa.
        await asyncio.sleep(0)
    




                    




