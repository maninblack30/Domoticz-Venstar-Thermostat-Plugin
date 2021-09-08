# Venstar Thermostat Local API
#
# Author: getSurreal
#
"""
<plugin key="Venstar" name="Venstar Thermostat Local API" author="getSurreal" version="1.0" wikilink="http://www.domoticz.com/wiki/plugins/venstar.html" externallink="http://venstar.com/">
    <params>
        <param field="Address"  label="Address"  width="200px" required="true"  default="192.168.1.x"/>
        <param field="Port"     label="Port"     width="200px" required="true" default="80"/>

        <param field="Mode1"    label="Polling Period (seconds)" width="200px" required="true" default="60"/>
        
        <param field="Mode2"    label="Humidity Control"    width="75px">
            <options>
                <option label="Yes"  value="True"/>
                <option label="No" value="False"  default="true" />
            </options>
        </param>

        <param field="Mode3"    label="Create Status Tracking Devices"    width="75px">
            <options>
                <option label="Yes"  value="True"/>
                <option label="No" value="False"  default="true" />
            </options>
        </param>

        <param field="Mode6"    label="Debug"    width="75px">
            <options>
                <option label="True"  value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
        
        
   </params>
</plugin>
"""
#        <param field="Username" label="Username" width="200px" required="false" default=""/>
#        <param field="Password" label="Password" width="200px" required="false" default=""/>


import Domoticz
import urllib.parse
import json
import base64
from datetime import datetime
import time


   
class BasePlugin:
    isConnected = False

    icons = {"venstar_fan_on": "venstar_fan_on icons.zip",
         "venstar_fan_off": "venstar_fan_off icons.zip",
         "venstar_cool": "venstar_cool icons.zip",
         "venstar_heat": "venstar_heat icons.zip"}

    modeUnit = 1
    fanModeUnit = 2
    heatSetpointUnit = 3
    coolSetpointUnit = 4
    dehumSetpointUnit = 5
    humSetpointUnit = 11
    tempUnit = 6
    tempHumUnit = 7
    humUnit = 8
    scheduleUnit = 9
    awayUnit = 10
    systemStateUnit = 12
    fanStateUnit = 13
    heatStatusUnit = 14
    coolStatusUnit = 15
    fanStatusUnit = 16



    def __init__(self):
        return

    def onStart(self):
        if Parameters['Mode6'] == 'Debug':
            Domoticz.Debugging(1)
            Domoticz.Debug("onStart called")
            DumpConfig()            
            DumpSettings()

        Domoticz.Debug("onStart called")
        Domoticz.Debug("Debug = " + Parameters["Mode6"])

         # load custom images
        for key, value in self.icons.items():
            Domoticz.Debug('adding ' + key + ' from file ' + value)
            if key not in Images:
                Domoticz.Image(value).Create()
                Domoticz.Debug("Added icon: " + key + " from file " + value)
        Domoticz.Debug("Number of icons loaded = " + str(len(Images)))
        for image in Images:
            Domoticz.Debug("Icon " + str(Images[image].ID) + " " + Images[image].Name)
       

        self.VenstarConn = Domoticz.Connection(Name="Venstar", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port=Parameters["Port"])
        self.VenstarConn.Connect()
        Domoticz.Heartbeat(int(Parameters["Mode1"]))

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):

        Domoticz.Debug("onConnect called")
        if (Status == 0):
            self.isConnected = True
            if (self.modeUnit not in Devices):
                #Options = "LevelActions:"+stringToBase64("||||")+";LevelNames:"+stringToBase64("Off|Heat|Cool|Auto")+";LevelOffHidden:ZmFsc2U=;SelectorStyle:MA=="
                Options = {"LevelActions": "||||",
                  "LevelNames": "Off|Heat|Cool|Auto",
                  "LevelOffHidden": "false",
                  "SelectorStyle": "1"}
                Domoticz.Device(Name="Mode",  Unit=self.modeUnit, TypeName="Selector Switch", Switchtype=18, Image=16, Options=Options).Create()
            if (self.fanModeUnit not in Devices):
                #Options = "LevelActions:"+stringToBase64("||||")+";LevelNames:"+stringToBase64("Auto|On")+";LevelOffHidden:ZmFsc2U=;SelectorStyle:MA=="
                Options = {"LevelActions": "||||",
                  "LevelNames": "Auto|On",
                  "LevelOffHidden": "false",
                  "SelectorStyle": "1"}
                Domoticz.Device(Name="Fan Mode",  Unit=self.fanModeUnit, TypeName="Selector Switch", Switchtype=18, Image=7, Options=Options).Create()
            if (self.heatSetpointUnit not in Devices): Domoticz.Device(Name="Heat Setpoint", Unit=self.heatSetpointUnit, Type=242, Subtype=1).Create()
            if (self.coolSetpointUnit not in Devices): Domoticz.Device(Name="Cool Setpoint", Unit=self.coolSetpointUnit, Type=242, Subtype=1, Image=16).Create()
            if(Parameters["Mode2"]):
                if (self.dehumSetpointUnit not in Devices): Domoticz.Device(Name="Dehum Setpoint", Unit=self.dehumSetpointUnit, Type=244, Subtype=73, Switchtype=7, Image=11).Create()
                if (self.humSetpointUnit not in Devices): Domoticz.Device(Name="Hum Setpoint", Unit=self.humSetpointUnit, Type=244, Subtype=73, Switchtype=7, Image=11).Create()
            if (self.tempUnit not in Devices): Domoticz.Device(Name="Temperature", Unit=self.tempUnit, TypeName="Temperature").Create()
            if (self.tempHumUnit not in Devices): Domoticz.Device(Name="Temp + Humidity", Unit=self.tempHumUnit, TypeName="Temp+Hum").Create()
            if (self.humUnit not in Devices): Domoticz.Device(Name="Humidity", Unit=self.humUnit, TypeName="Humidity").Create()
            if (self.scheduleUnit not in Devices): Domoticz.Device(Name="Schedule", Unit=self.scheduleUnit, TypeName="Switch", Image=13).Create()
            if (self.awayUnit not in Devices): Domoticz.Device(Name="Away Mode", Unit=self.awayUnit, TypeName="Switch").Create()
                
            if (self.systemStateUnit not in Devices): Domoticz.Device(Name="System State", Unit=self.systemStateUnit, Type=17, Switchtype=17, Image=Images['venstar_fan_off'].ID).Create()
            if (self.fanStateUnit not in Devices): Domoticz.Device(Name="Fan State", Unit=self.fanStateUnit, Type=17,  Switchtype=17, Image=Images['venstar_fan_off'].ID).Create()
            if(Parameters["Mode3"]):
                if (self.heatStatusUnit not in Devices): Domoticz.Device(Name="Heating Status", Unit=self.heatStatusUnit, TypeName="Custom").Create()
                if (self.coolStatusUnit not in Devices): Domoticz.Device(Name="Cooling Status", Unit=self.coolStatusUnit, TypeName="Custom").Create()
                if (self.fanStatusUnit not in Devices): Domoticz.Device(Name="Fan Status", Unit=self.fanStatusUnit, TypeName="Custom").Create()
        else:
            self.isConnected = False
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"])
            Domoticz.Debug("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+" with error: "+Description)

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")
    
        jsonStr = Data["Data"].decode("utf-8", "ignore")

        if "success" in jsonStr:
            return
        if "error" in jsonStr:
            Domoticz.Log(jsonStr)
            return

        data = json.loads(jsonStr) # parse json string to dictionary
        UpdateDevice(self.modeUnit,0,str(data['mode']*10))

        UpdateDevice(self.fanModeUnit,0,str(data['fan']*10))

        #calc humidity status
        
#       if(data['hum'] < 25):
#            humStat = 2 #dry
#        elif(data['hum'] > 60):
#            humStat = 3 #wet
#        elif(data['hum'] >= 25 and data['hum'] <= 60):
#            humStat = 1 #comfortable
#        else:
#            humStat = 0 #normal


        if (data['tempunits'] == 0): # If thermostat is in fahrenheit convert to celcius for domoticz
            
            UpdateDevice(self.heatSetpointUnit,0,str((data['heattemp'] -32)*5/9))
            UpdateDevice(self.coolSetpointUnit,0,str((data['cooltemp'] -32)*5/9))
            UpdateDevice(self.tempUnit,0,str((data['spacetemp']-32)*5/9))
            UpdateDevice(self.tempUnit,0,str((data['spacetemp']-32)*5/9)+";"+str(data['hum'])+";"+str(humStat))
        else:
            
            UpdateDevice(self.heatSetpointUnit,0,str(data['heattemp']))
            UpdateDevice(self.coolSetpointUnit,0,str(data['cooltemp']))
            UpdateDevice(self.tempUnit,0,str(data['spacetemp']))
            UpdateDevice(self.tempHumUnit,0,str(data['spacetemp'])+";"+str(data['hum'])+";"+str(humStat))

       if humidity control enabled, get hum set point
        if(Parameters["Mode2"]):            
           UpdateDevice(self.humSetpointUnit,2,str(data['hum_setpoint']) ) #nValue 2 to show percentage
           UpdateDevice(self.dehumSetpointUnit,2,str(data['dehum_setpoint']) ) #nValue 2 to show percentage
                            
        
        UpdateDevice(self.humUnit,data['hum'],"0")
        UpdateDevice(self.scheduleUnit,data['schedule'],"0")
        UpdateDevice(self.awayUnit,data['away'],"0")
        
        systemState = 'Idle'
        systemStateIcon = 'fan_off'

        if(data['state'] == 1):
            systemState = 'Heating'
            systemStateIcon = 'heat'
        elif (data['state'] == 2):
            systemState = 'Cooling'
            systemStateIcon = 'cool'
        elif (data['state'] == 3):
            systemState = 'Lockout'
        elif (data['state'] == 4):
            systemState = 'Error'

        UpdateDevice(self.systemStateUnit,0,systemState,systemStateIcon) 

        if(Parameters["Mode3"]):
            heatStatus = "0"
            coolStatus = "0"

            if(systemState == "Heating"):
                heatStatus="1"
            elif(systemState=="Cooling"):
                coolStatus = "1"
            

            UpdateDevice(self.heatStatusUnit,0,heatStatus)
            UpdateDevice(self.coolStatusUnit, 0, coolStatus)
            UpdateDevice(self.fanStatusUnit, 0, data['fanstate'])

        fanState = 'On' if data['fanstate'] == 1 else 'Off'
        fanStateIcon = 'fan_on' if data['fanstate'] == 1 else 'fan_off'

        UpdateDevice(self.fanStateUnit,0,fanState,fanStateIcon)
        
   


    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(int(Level)))
        Domoticz.Debug("mode:"+str(int(Devices[1].sValue))+", fan:"+str(Devices[2].nValue)+", heattemp:"+str(int(float(Devices[3].sValue)*9/5+32))+", cooltemp:"+str(int(float(Devices[4].sValue)*9/5+32)))

        domoTempUnits = Settings["TempUnit"] # 1=Farenheit,0=Celsius

        if (Unit == self.modeUnit): 
            mode_val = int(Level/10)
            UpdateDevice(Unit,0,Level)
        else:
            mode_val = int(int(Devices[1].sValue)/10)

        if (Unit == self.fanModeUnit): 
            fan_val = int(Level/10)
            UpdateDevice(Unit,0,Level)
        else:
            fan_val = int(int(Devices[2].sValue)/10)

        if (Unit == self.heatSetpointUnit): 
            heat_val = int(Level)
            heat_val_to_store = heat_val
            if(domoTempUnits == '1'):
                heat_val_to_store = (float(heat_val)-32)*5/9
            
            UpdateDevice(Unit,0,str(heat_val_to_store))
        else:
            heat_val = int(float(Devices[3].sValue)*9/5+32)

        if (Unit == self.coolSetpointUnit): 
            cool_val = int(Level)
            cool_val_to_store = cool_val
            if(domoTempUnits == '1'):
                cool_val_to_store = (float(cool_val)-32)*5/9
            UpdateDevice(Unit,0,str(cool_val_to_store))
        else:
            cool_val = int(float(Devices[4].sValue)*9/5+32)

        if (Unit <= self.coolSetpointUnit):

            params = 'mode='+str(mode_val)+'&fan='+str(fan_val)+'&heattemp='+str(heat_val)+'&cooltemp='+str(cool_val)
            headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
            self.VenstarConn.Send({'Verb':'POST', 'URL':'/control','Headers':headers, 'Data': str(params)})  
                  

        if (Unit == self.scheduleUnit): 
            if (Command == "On"):
                params = 'schedule=1';
                UpdateDevice(Unit,1,"0")

            elif (Command == "Off"):
                params = 'schedule=0';
                UpdateDevice(Unit,0,"0")

            headers = { 'Content-Type': 'application/x-www-form-urlencoded' }

            self.VenstarConn.Send({'Verb':'POST', 'URL':'/settings','Headers':headers, 'Data': params})

        if (Unit == self.awayUnit): 
            if (Command == "On"):
                params = 'away=1'
               
                UpdateDevice(Unit,1,"0")

            elif (Command == "Off"):
                params =  'away=0'
                UpdateDevice(Unit,0,"0")
            headers = { 'Content-Type': 'application/x-www-form-urlencoded'}

            self.VenstarConn.Send({'Verb':'POST', 'URL':'/settings','Headers':headers, 'Data': params})
        
        if(Unit == self.dehumSetpointUnit):
            if(Level >= 25 and Level <= 99):
                params = 'dehum_setpoint='+str(int(Level))+'&hum_setpoint='+str(int(float(Devices[11].sValue)))

                UpdateDevice(Unit,0,Level)

                headers = { 'Content-Type': 'application/x-www-form-urlencoded' }

                self.VenstarConn.Send({'Verb':'POST', 'URL':'/settings','Headers':headers, 'Data': params})

        if(Unit == self.humSetpointUnit): 
            if(Level >= 0 and Level <= 60):
                params = 'hum_setpoint='+str(int(Level))+'&dehum_setpoint='+str(int(float(Devices[5].sValue)))
                
                UpdateDevice(Unit,0,str(Level))
                
                headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
                #self.VenstarConn.Send(params, "POST", "/settings", headers)
                self.VenstarConn.Send({'Verb':'POST', 'URL':'/settings','Headers':headers, 'Data': params})


    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")
        self.isConnected = False

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        if (self.VenstarConn.Connected() == True):
            url = '/query/info'
            data = ''
            headers = { 'Content-Type': 'text/xml; charset=utf-8', \
                        'Connection': 'keep-alive', \
                        'Accept': 'Content-Type: text/html; charset=UTF-8', \
                        'Host': Parameters["Address"]+":"+Parameters["Port"], \
                        'User-Agent':'Domoticz/1.0', \
                        'Content-Length' : "%d"%(len(data)) }

            self.VenstarConn.Send({"Verb":"GET", "URL":url, "Headers": headers})

        else:
            self.VenstarConn.Connect()

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfig():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def DumpSettings():
    for x in Settings:
        Domoticz.Debug( "'" + x + "':'" + str(Settings[x]) + "'")
    return

def DumpImages():
    Domoticz.Debug("DumpImages called")
    for x in Images:
        Domoticz.Debug( "'" + x + "':'" + str(Images[x]) + "'")
    return

def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8')).decode("utf-8")

def UpdateDevice(Unit, nValue, sValue, imageKey=''):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        # Update the device before it times out even if the values are the same
        SensorTimeout = Settings['SensorTimeout']

        # try/catch due to http://bugs.python.org/issue27400
        try:
            timeDiff = datetime.now() - datetime.strptime(Devices[Unit].LastUpdate,'%Y-%m-%d %H:%M:%S')
        except TypeError:
            timeDiff = datetime.now() - datetime(*(time.strptime(Devices[Unit].LastUpdate,'%Y-%m-%d %H:%M:%S')[0:6]))

        timeDiffMinutes = (timeDiff.seconds/60)%60
        imageKey = 'venstar_'+imageKey
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue or timeDiffMinutes+5 > int(SensorTimeout)):
            if(imageKey and imageKey in Images):
                Devices[Unit].Update(nValue=nValue, sValue=str(sValue),Image=Images[imageKey].ID)
            else:
                Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return



