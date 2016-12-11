#########C O M M A N D S##########
#AO(DAC,value)
#AI(AIN)
#DO(FIO,value)
#DI(FIO)
#Examples:
# MAKE NA OBJECT
##cl=controll()

# Analog output on channel 0:
#cl.AO(cl.AIN['0'],3.12)
#
# READ Analog INPUT
#cl.AI(cl.AIN['0'])
# or
#VALUE=cl.AI(cl.AIN['0'])
#print VALUE

# ###############
import u3

d = u3.U3()
    #d.debug = True

d.getCalibrationData()
class controll:
    DAC = {'0':5000,
           '1':5002}

    FIO ={ '4':6004,
           '5':6005,
           '6':6006,
           '7':6007,
               }

    AIN = {'0':0,'1':2,'2':4,'3':6}

    # Analog = 1, Digital = 0
    FIO_AD = {'4':50594,
              '5':50595,
              '6':50596,
              '7':50597,
              }
    
    FIO_DIR = {'4':6104,
               '5':6105,
               '6':6106,
               '7':6107,
                }

    #commands FIO
    #d.writeRegister(FIO['4'], 1) -1,0 High/LOW
    #d.writeRegister(FIO_DIR['5'],0) 0-input, 1 - output
    #d.writeRegister(FIO_AD['6'],1) 0 - digital, 1 - Analog
    #d.writeRegister(DAC['0'],3.7) 3.7V

    def AO(self,DAC,value):
        if DAC>=4999 and DAC<=5003:
            try:
                d.writeRegister(DAC,value)
            except:
                pass

    def AI(self,AIN):
        if AIN >= 0 and AIN <= 9:
            try:
                z=d.readRegister(AIN)
            except:
                pass
            return z
            
         

    def DO(self,FIO,value):
        FIO_DIR = {'4':6104,
               '5':6105,
               '6':6106,
               '7':6107,
                }
        if value == 0 or value == 1:
            if FIO >= 6004 and FIO <= 6007:
                try:
                    d.writeRegister(FIO_DIR[str(FIO-6000)],1)

                    d.writeRegister(FIO,value)
                except:
                    pass

    def DI(self,FIO):
        FIO_DIR = {'4':6104,'5':6105,'6':6106,'7':6107}
        if FIO >= 6004 and FIO <= 6007:
            try:
                
                d.writeRegister(FIO_DIR[str(FIO-6000)], 0)
                z=d.readRegister(FIO)

            except:
                pass
            return z
        
    def DI_RO(self,FIO):##DI-READ-ONLY
        if FIO >= 6004 and FIO <= 6007:
             try:
                
                 #d.writeRegister(FIO_DIR[str(FIO-6000)], 0)
                 z=d.readRegister(FIO)

             except:
                 pass
             return z

cl=controll()
#d.writeRegister(50590,0)

#print(d.readRegister(cl.FIO['4']))
#d.writeRegister(50594,0)
#print(d.readRegister(50590,1))

#cl=controll()
#print(controll.DAC)
#print(cl.DAC['1'])

#cl.DO(cl.FIO['7'],1)
#cl.DI(cl.FIO['3'])
#z=cl.AI(cl.AIN['0'])
#l=cl.DI(cl.FIO['7'])
#print(l)
