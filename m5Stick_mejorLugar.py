


from m5stack import * 
from m5ui import *
from uiflow import *
import wifiCfg
import espnow
from m5mqtt import M5mqtt
import hat
import json
import unit
import machine
import urequests
import machine
from micropython import const
import ntptime

#Variables a configurar:
ssid = "xxxx"
password_wifi = "xxxx"


setScreenColor(0x555555)
macAddr = None
id_client_control = None
id_client_business = None
business_topic_p = None
business_topic_s = None
sensorData = None
mensaje = None

wifiCfg.wlan_sta.active(True)
wifiCfg.doConnect(ssid, password_wifi)
label0 = M5TextBox(78, 0, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label1 = M5TextBox(61, 0, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label2 = M5TextBox(44, 0, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label3 = M5TextBox(26, 0, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=90)

espnow.init()
while (not wifiCfg.wlan_sta.isconnected()):
    wifiCfg.doConnect(ssid, password_wifi)
ntp = ntptime.client(host='es.pool.ntp.org', timezone=1)
rtc.setTime((ntp.year()), (ntp.month()), (ntp.day()), (ntp.hour()), (ntp.minute()), (ntp.second()))
hat_env0 = unit.get(unit.ENV2, unit.PORTA)
espnow.init()
macAddr = str((espnow.get_mac_addr()))
macAddr = macAddr.replace(':', '').upper()
id_client_control = macAddr
id_client_business = "b_"+id_client_control
frec=1

#traza
t = 'temp/hum:'+str(hat_env0.temperature)+' '+str(hat_env0.humidity)
label0.setText(t)
wait(2)

business_topic_p = "business/TEAM_9/ENT/server"
business_topic_s = "business/TEAM_9/ENT/device/"+id_client_business

label3.setText('Traza antes m5mqtt')
m5mqtt = M5mqtt(str(id_client_business), 'iothub02.onesaitplatform.com', 8883, str(id_client_control), 'RtjK5wCe', 30, ssl = True)
label3.setText('2Traza antes suscripcion2')
wait(1)


def fun_business_c2d_(topic_data):  
  global m5mqtt,business_topic_p,gps0,macAddr,frec
  #Proceso del comando Cloud-2-Device
  label1.setText(str(topic_data))
  wait(0.2)
  jsonTopic_data=json.loads(topic_data)
  frec=jsonTopic_data["frec"]
   #Ejemplo, función de Echo del mensaje mandado
  mensaje_echo = {'deviceId':macAddr,'timestamp':ntp.formatDatetime('-', ':'),'payload':jsonTopic_data}
  wait(0.2)
  m5mqtt.publish(str(business_topic_p),json.dumps(mensaje_echo))


def fun_business_d2c_(topic_data):  
  global m5mqtt,business_topic_p
  #Proceso del comando Cloud-2-Device
  label1.setText(str(topic_data))
  m5mqtt.publish(str(business_topic_p),str((json.dumps(topic_data))))

m5mqtt.subscribe(business_topic_s, fun_business_c2d_)
label3.setText('Traza antes start')
wait(2)
m5mqtt.start()
wait(2)


while True:
    #label3.setText('Traza 1 while')
    #sensorData = {'hum':(hat_env0.humidity),'temp':(hat_env0.temperature),'press':(hat_env0.pressure),'light':(pir0.state)}
    sensorData = {'pres':(hat_env0.pressure),'hum':(hat_env0.humidity),'temp':(hat_env0.temperature)}
    #label2.setText(str(id_client_business))
    #label3.setText(str(business_topic_p))
    mensaje = {'deviceId':macAddr,'frec':frec,'timestamp':ntp.getTimestamp()}
    mensaje.update(sensorData)
    
    #Proceso del envio de datos Device-2-Cloud
    fun_business_d2c_(mensaje)
    wait(1)

    label0.setText('Publicando...')
    label2.setText(str(sensorData))
    label3.setText(ntp.formatDatetime('-',':'))#traza

    M5Led.on()
    wait(0.5)
    M5Led.off()
    #mensaje.clear()
    #sensorData.clear()
    #wait(frec-0.5)
  
    while (not wifiCfg.wlan_sta.isconnected()):
        wifiCfg.doConnect(ssid, password_wifi)




















