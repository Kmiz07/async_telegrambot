import confjson, asyncio, network, utime, conexion
valores= confjson.recupera()
red= valores['ST_SSID']
print(f'red: {red}')
clave= valores['ST_PASSW']
print(f'clave:{clave}')
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(red, clave)
inicio_wifi=utime.time()
while wifi.isconnected() == False:
    if utime.time()-15 > inicio_wifi: break
if wifi.isconnected():
    print('conectado')
    asyncio.run(conexion.main())
else:
    print('no conectado')

