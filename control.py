#
import threading
import pickle
import socket,sys
import time
import u3

import LJcontrol as LJc
cl=LJc.controll()
print(cl.DAC)


controller={'DAC':[1,1],'FIO':[0,0],'value':0,'frequency':[0,0]}
global data_to_send
data_to_send={'AIN':[0,0,0,0],'FIO':[0,0,0,0],'Time':0}


def establish(): ## Establish server
        #### najde svoji vlastni IP
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com", 80))
        MY_LOCAL_IP = (s.getsockname()[0])
        s.close()
        ###################################
        s = socket.socket()
        port=10011

        s.bind((str(MY_LOCAL_IP), port))
        s.listen(5)
      
        while True:
            c, addr = s.accept()
            print('Got Connection from:', addr)
            while True:
                global controller
                try: ## RECEIVE DATA,UNPACK IT with PROTOCOL 2
                    received_data = c.recv(1024*350)
                    controller = pickle.loads(received_data)
                except IndexError:      
                    print('index error')
                except:
                        break

                try:
                        serialized_data=pickle.dumps(data_to_send,protocol=2)
                        c.send(serialized_data)
                except:
                        pass
      
              
                
threading.Thread(target=establish).start()

def input_read(): ### This method collects values from all inputs
        start = time.time()
        while True:
                global data_to_send
                for i in range(4):
                        data_to_send['FIO'][i]=round(cl.DI_RO(cl.FIO[str(i+4)]),2)
                        now = time.time()
                        data_to_send['AIN'][i]=round(cl.AI(cl.AIN[str(i)]),2)
                data_to_send['Time']= round(now - start,2)
                time.sleep(0.001)


def check_point(): ### Assigning commands to LABJACK from received data
        while True:
                if controller['DAC'][0] == 1:
                        cl.AO(cl.DAC[str(controller['DAC'][1])],controller['value'])
                        if controller['frequency'][0] == 1:
                                try:
                                        cl.AO(cl.DAC[str(controller['DAC'][1])],controller['value'])
                                        time.sleep(0.5/controller['frequency'][1])
                                        cl.AO(cl.DAC[str(controller['DAC'][1])],0)
                                        time.sleep(0.5/controller['frequency'][1])
                                except:
                                        pass
                if controller['FIO'][0] == 1:
                        cl.DO(cl.FIO[str(controller['FIO'][1])],controller['LH'][1])
                        
                                
                                
                time.sleep(0.025)
                
threading.Thread(target=input_read).start()
threading.Thread(target=check_point).start()



