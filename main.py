
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib.pyplot as plt
import socket,sys

from kivy.graphics import *

import numpy as np
import threading
import pickle
from kivy.clock import Clock





################ Simulace RPi############## Jestlize bude problem s tim ze LABJACK jiz je zapojen -> Zrusit vsechny Python procesy, ctr+alt+delete -> zrusit
def python_sc():
    import os
    os.system('python control.py')
threading.Thread(target=python_sc).start()








class gwindow(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(gwindow, self).__init__(*args, **kwargs)

class MainWindow(BoxLayout):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.LIST_OF_GRAPHS = []
        self.Xx = []
        self.Yy = []
        self.valie = 0
        self.xt=1
        self.yt=1
        self.uhel=1
        self.velocity=1
        OUTPUT = {'DAC': [0, 0], 'FIO': [0, 0], 'value': 0, 'LH': [0, 0], 'frequency': [0, 0]}
        self.disconnection = False
        self.AIN_line=[[],[],[],[]]
        self.FIO_line=[[],[],[],[]]
        self.Time_line=[]

        self.serialized_dict = pickle.dumps(OUTPUT,protocol=2)

    def on_touch_down(self, touch):

        if self.collide_point(touch.x, touch.y):

            if ((touch.x-self.ids.sm_real_time.x)>self.ids.display.x and (touch.x-self.ids.sm_real_time.x) < (self.ids.display.x+self.ids.display.width)) and ((touch.y-self.ids.sm_real_time.y) > self.ids.display.y and (touch.y-self.ids.sm_real_time.y) < (self.ids.display.y + self.ids.display.height)):
                if self.ids.sm_real_time.current == 'output':  # Pokud je otevreno platno - Control stranka

                    self.draw_vector(touch)
        return super(MainWindow, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y):

            if ((touch.x - self.ids.sm_real_time.x) > self.ids.display.x and (touch.x - self.ids.sm_real_time.x) < (
                self.ids.display.x + self.ids.display.width)) and (
                    (touch.y - self.ids.sm_real_time.y) > self.ids.display.y and (touch.y - self.ids.sm_real_time.y) < (
                self.ids.display.y + self.ids.display.height)):
                if self.ids.sm_real_time.current == 'output':  # Pokud je otevreno platno - Control stranka

                    self.draw_vector(touch)
        return super(MainWindow, self).on_touch_down(touch)

#####################   DRAWING ON CANVAS - GEOMETRY, TOUCH, POSITIONING
    def draw_vector(self,touch):
        display = self.ids.display
        display.canvas.clear()

        centerX=display.width/2
        centerY=display.height/2

        posX = touch.x - self.ids.sm_real_time.x-self.ids.display.x
        posY = touch.y  - self.ids.sm_real_time.y- display.y


        self.xt = posX - centerX
        self.yt = posY - centerY

        velocity = np.sqrt((self.xt**2) + (self.yt**2))
        self.velocity=velocity/45

        self.uhel=1
        if self.xt >= 0 and self.yt >= 0:
            self.uhel = np.arcsin(-self.yt / velocity)* (-180) /np.pi
        if self.xt >= 0 and self.yt <= 0:
            self.uhel = 360-np.arcsin(self.yt / velocity) * (-180) / np.pi
        if self.xt <= 0 and self.yt < 0:
            self.uhel =180+ np.arcsin(self.yt / velocity) * (-180) / np.pi
        if self.xt <= 0 and self.yt > 0:
            self.uhel =180- np.arcsin(self.yt / velocity) * 180 / np.pi
        try:
            freq=round(self.uhel,2) # neni treba
            self.ids.vel.text=str(freq/15) # neni treba
        except:
            pass



        #threading.Thread(target=MainWindow.connecting(self, HOSTNAME), kwargs={'HOSTNAME': HOSTNAME})


        ##################### CONTROL LOGIC - THROUGH GRAPHICS #######################
        with display.canvas:
            Color(0,0,0,0)
            Rectangle(pos=(0,0), size=display.size)

            #Color(3/255,152/255,1,1)
            Color(1,1, 1, 1)
            Line(points=[centerX,centerY,posX,posY], width=1.3,close=True,joint='round')

            Color(1,1,1,1)



            fix_r= self.ids.display.width/2.7
            Line(circle=(centerX, centerY, fix_r*1.01,0,360),width=1.3)



            Line(points=[centerX, centerY, centerX, centerY+fix_r], width=0.5, close=True,joint='round')
            Line(points=[centerX, centerY, centerX+fix_r, centerY], width=0.5, close=True,joint='round')
            Line(points=[centerX, centerY, centerX-fix_r, centerY], width=0.5, close=True,joint='round')
            Line(points=[centerX, centerY, centerX+np.cos(45*np.pi/180)*fix_r, centerY+np.sin(45*np.pi/180)*fix_r], width=0.5, close=True,joint='round')




            ################################### Circle Mechanics
            diameter=fix_r*2
            frek=0
            freq_act=0
            LH_value = 0
            voltage=0
            self.ids.logic.text = 'None'
            self.ids.pb2.value=0
            self.ids.pb.max = fix_r
            self.ids.pb.value = velocity

            if self.uhel >=0 and self.uhel<=45: #1 Kvadrat, prava cast
                Color(3 / 255, 152 / 255, 1, 1)

                Ellipse(pos=(0-diameter/2+self.ids.display.width/2,0-diameter/2+self.ids.display.height/2), size=(diameter, diameter),
                        angle_start=45, angle_end=90)
                LH_value=0
                self.ids.logic.text='False'
                voltage = 0  # Max Voltage je dano podminkou IF o par radku nize
                self.ids.pb.value = 0


            if self.uhel > 45 and self.uhel <= 90: ## 1 Kvadrat, leva cast
                Color(3 / 255, 152 / 255, 1, 1)

                Ellipse(
                    pos=(0 - diameter / 2 + self.ids.display.width / 2, 0 - diameter / 2 + self.ids.display.height / 2),
                    size=(diameter, diameter),
                    angle_start=0, angle_end=45)
                LH_value=1
                self.ids.logic.text='True'
                voltage = 3.3  # Max Voltage je dano podminkou IF o par radku nize
                self.ids.pb.value = (3.3/4.9)*fix_r



            if self.uhel > 90 and self.uhel <= 180:

                if velocity <= fix_r:
                    Color(3 / 255, 152 / 255, 1, velocity/fix_r)

                    #Color(1, 1, 1, velocity/fix_r)
                    Ellipse(
                        pos=(0 - velocity + self.ids.display.width / 2, 0 - velocity+ self.ids.display.height / 2),
                        size=(velocity*2, velocity*2),
                        angle_start=270, angle_end=360)
                else:
                    Color(3 / 255, 152 / 255, 1, velocity/fix_r)
                    Ellipse(
                        pos=(0 - fix_r + self.ids.display.width / 2, 0 - fix_r + self.ids.display.height / 2),
                        size=(fix_r * 2, fix_r * 2),
                        angle_start=270, angle_end=360)
                voltage = round(5 * velocity / fix_r, 2)  # Max Voltage je dano podminkou IF o par radku nize

            if self.uhel > 180 and self.uhel <= 360:
                if velocity <= fix_r:
                    Color(3 / 255, 152 / 255, 1, velocity/fix_r)

                    #Color(1, 1, 1, velocity / fix_r)
                    Ellipse(
                        pos=(0 - velocity + self.ids.display.width / 2, 0 - velocity + self.ids.display.height / 2),
                        size=(velocity * 2, velocity * 2),
                        angle_start=270, angle_end=90 + 360 - self.uhel)
                    frek=round(self.uhel-180+3,2)
                    freq_act = 1
                    self.ids.pb2.value = (self.uhel-180)*2 #MAX PB2 JE 360



                else:
                    Color(3 / 255, 152 / 255, 1, velocity/fix_r)
                    Ellipse(
                        pos=(0 - fix_r + self.ids.display.width / 2, 0 - fix_r + self.ids.display.height / 2),
                        size=(fix_r * 2, fix_r * 2),
                        angle_start=270, angle_end=90 + 360 - self.uhel)
                    frek = round(self.uhel - 180+3,2)
                    #print(self.uhel-90)
                    self.ids.pb2.value = (self.uhel-180)*2 #MAX PB2 JE 360
                    freq_act = 1
                voltage = round(5 * velocity / fix_r, 2)  # Max Voltage je dano podminkou IF o par radku nize

            ##### LABELS IN THE CIRCLES, PUSHMATRIX a POPMATRIX zapricini ze prikaz rotace se neuplatni v celem canvas ale jen mezi temito dvema prikazy
            z = []



            PushMatrix()
            r=Rotate()
            r.angle=0

            widget = Label(text='[b]' + 'Puls' + '[/b]',pos=[centerX, centerY - fix_r*0.7], size=[1, 1],font_size='20sp', markup=True,)
            z.append(widget)
            PopMatrix()

            PushMatrix()
            r = Rotate()
            r.angle=45/2-90
            pozice=[float(round(centerX + np.cos((45/2) * np.pi / 180) * fix_r*0.7,2)),float(round(centerY + np.sin((45/2) * np.pi / 180) * fix_r*0.7,2))]
            #print(type(float(pozice[0])))
            r.origin= pozice
            widget2 = Label(text='[b]' + 'False' + '[/b]', pos=pozice, size=[1, 1],
                           font_size='20sp', markup=True)
            z.append(widget2)
            PopMatrix()

            PushMatrix()
            r = Rotate()
            r.angle = 45 *3/2 - 90
            pozice = [float(round(centerX + np.cos((45*3/2) * np.pi / 180) * fix_r * 0.7, 2)),
                      float(round(centerY + np.sin((45*3/ 2) * np.pi / 180) * fix_r * 0.7, 2))]
            #print(type(float(pozice[0])))
            r.origin = pozice
            widget2 = Label(text='[b]' + 'True' + '[/b]', pos=pozice, size=[1, 1],
                            font_size='20sp', markup=True)
            z.append(widget2)
            PopMatrix()

            PushMatrix()
            r = Rotate()
            r.angle = 180*3/4 - 90
            pozice = [float(round(centerX + np.cos((180*3/4) * np.pi / 180) * fix_r * 0.7, 2)),
                      float(round(centerY + np.sin((180*3/4) * np.pi / 180) * fix_r * 0.7, 2))]
            #print(type(float(pozice[0])))
            r.origin = pozice
            widget2 = Label(text='[b]'+ 'Analog' + '[/b]', pos=pozice, size=[1, 1],
                            font_size='20sp', markup=True)
            z.append(widget2)
            PopMatrix()

            #widget = Label(text='[b]' + 'Puls' + '[/b]',pos=[centerX, centerY - fix_r*0.7], size=[1, 1],font_size='25sp', markup=True)


            z.append(widget)

            self.z = z

            #### MAX HODNOTA 4,9V
            if voltage>4.9:
                voltage=4.9
            frek=frek
            frek=round(float(frek),1)
            #print(frek)
            self.ids.vel.text = str(round(frek,2))


            self.ids.amplit.text = str(voltage)



        ##########Getting data for commands actualized in RPi - 'OUTPUT'
        option={        'DAC0': self.ids.dac0.state,
                        'DAC1': self.ids.dac1.state,
                        'FIO4': self.ids.FIO4.state,
                        'FIO5': self.ids.FIO5.state,
                        'FIO6': self.ids.FIO6.state,
                        'FIO7': self.ids.FIO7.state,
                        }
        OUTPUT = {'DAC': [0, 0], 'FIO': [0, 0], 'value': 0, 'LH': [0, 0], 'frequency': [0, 0]}

        self.data_to_transmit(option,OUTPUT,voltage,LH_value,frek,freq_act)
        #####
    def data_to_transmit(self,option,OUTPUT,voltage,LH_value,frek,freq_act):
        for i in option:
            if option[i]=='down':
                if i == 'DAC0':
                    OUTPUT['DAC']=[1,0]
                    OUTPUT['value'] = voltage
                    OUTPUT['LH'] = [0,LH_value]
                    OUTPUT['frequency']=[freq_act,frek]
                if i == 'DAC1':
                    OUTPUT['DAC'] = [1, 1]
                    OUTPUT['value'] = voltage
                    OUTPUT['LH'] = [0, LH_value]
                    OUTPUT['frequency'] = [freq_act,frek]
                if i == 'FIO4':
                    OUTPUT['FIO'] = [1, 4]
                    OUTPUT['value'] = 0
                    OUTPUT['LH'] = [1, LH_value]
                    OUTPUT['frequency'] = [freq_act,frek]
                if i == 'FIO5':
                    OUTPUT['FIO'] = [1, 5]
                    OUTPUT['value'] = 0
                    OUTPUT['LH'] = [1, LH_value]
                    OUTPUT['frequency'] = [freq_act,frek]
                if i == 'FIO6':
                    OUTPUT['FIO'] = [1, 6]
                    OUTPUT['value'] = 0
                    OUTPUT['LH'] = [1, LH_value]
                    OUTPUT['frequency'] = [freq_act,frek]
                if i == 'FIO7':
                    OUTPUT['FIO'] = [1, 7]
                    OUTPUT['value'] = 0
                    OUTPUT['LH'] = [1, LH_value]
                    OUTPUT['frequency'] = [freq_act,frek]
                #print(OUTPUT)

            self.serialized_dict = pickle.dumps(OUTPUT,protocol=2)



    def clear_channels(self):
        OUTPUT = 'CLEAR' # make a function inside RASPBERRY PI
        self.serialized_dict = pickle.dumps(OUTPUT, protocol=2)

    def est(self):
        threading.Thread(target=self.establish).start()
    def con(self):
        threading.Thread(target=self.connect_to).start()




############################### Client side
    def connect_to(self):
        c = socket.socket()
        # host = '10.0.0.35'  # ip of raspberry pi
        # port = 10003

        c.connect((str(self.ids.t_ip.text), int(self.ids.t_port.text)))
        self.ids.con.text='connected'
        print('Connected')
        self.ids.pbdata.value=0
        self.disconnection = False
        while self.disconnection==False:
            #print(self.serialized_dict)
            c.send(self.serialized_dict)
            rd=c.recv(1024*350)
            self.received_data=pickle.loads(rd)

            #### Processing the data
            self.time_data = self.received_data['Time']
            self.AIN_data = self.received_data['AIN']
            self.FIO_data = self.received_data['FIO']

            self.ids.pbdata.value+=0.25
            if self.ids.pbdata.value >= 100:
                self.ids.pbdata.value = 0


        ## DISCONNECTION FROM THE SERVER
        self.disconnection = False
        print('Server Disconnect')
        self.ids.con.text = 'connect'
        c.close()

    def disconnect(self):
        self.ids.con.disabled = False
        self.disconnection = True
    def find_my_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("gmail.com", 80))
            MY_LOCAL_IPl = (s.getsockname()[0])
            s.close()
            self.ids.t_ip.text=str(MY_LOCAL_IPl)
        except:
            pass
###############################END OF CLIENT SIDE



############################## MATPLOTLIB INTEGRATION FOR VISUALISATION OF INPUT CHANNELS

    def create_graph(self):
        plt.rc('axes', edgecolor=[1, 1, 1, 1])
        fig, self.ax = plt.subplots(facecolor=[0, 0, 0, 0])


        self.ax.tick_params(color=[1, 1, 1, 1], labelcolor=[1, 1, 1, 1])
        self.ax.xaxis.label.set_color([1, 1, 1, 1])
        self.ax.yaxis.label.set_color([1, 1, 1, 1])

        # self.ax.titleaxis.label.set_color(self.ids.cpicker.color)

        self.canvas = FigureCanvasKivyAgg(figure=fig)
        graph_window = self.ids.graph_window
        graph_window.add_widget(self.canvas)
        self.LIST_OF_GRAPHS.append(self.canvas)
        self.ax.set_axis_bgcolor('black')


    def delete_graph(self):
        print('delete')
        graph_window = self.ids.graph_window
        for i in self.LIST_OF_GRAPHS:
            # print(i)
            graph_window.remove_widget(i)
        try:
            Clock.unschedule(self.real_time)
        except:
            pass


    def start_real_time(self):
        #print(threading.activeCount())
        try:
            self.ax.cla()

            plt.rc('axes', edgecolor=[1, 1, 1, 1])
            plt.xlabel('Time [s]', fontsize=14)
            plt.ylabel('Voltage [V]', fontsize=14)
            plt.title('Real-time', fontsize=14, color='#FFFFFF')
            self.graph_AIN0, = self.ax.plot([], [], color='#78D4FF')
            self.graph_AIN1, = self.ax.plot([], [], color='#7BFF90')
            self.graph_AIN2, = self.ax.plot([], [], color='#FFFC6B')
            self.graph_AIN3, = self.ax.plot([], [], color='#FF6CC2')
            self.graph_FIO4, = self.ax.plot([], [], color='#FC0100')
            self.graph_FIO5, = self.ax.plot([], [], color='#00FC35')
            self.graph_FIO6, = self.ax.plot([], [], color='#FCF900')
            self.graph_FIO7, = self.ax.plot([], [], color='#001DFC')
            ymin = -1
            ymax = 6.5
            self.ax.set_ylim([ymin, ymax])
            # self.ax.grid(color='w', linestyle='-', linewidth=1
            Clock.schedule_interval(self.real_time, 1 / 40)
        except:
            print(('Chyba'))

    def real_time(self, dt):
        try:
            for i in range(len(self.AIN_data)):
                self.AIN_line[i].append(self.AIN_data[i])
                self.FIO_line[i].append(self.FIO_data[i])
            self.Time_line.append(self.time_data)

            if self.ids.ain0.state == 'down':
                self.graph_AIN0.set_xdata(self.Time_line)
                self.graph_AIN0.set_ydata(self.AIN_line[0])
            if self.ids.ain1.state == 'down':
                self.graph_AIN1.set_xdata(self.Time_line)
                self.graph_AIN1.set_ydata(self.AIN_line[1])
            if self.ids.ain2.state == 'down':
                self.graph_AIN2.set_xdata(self.Time_line)
                self.graph_AIN2.set_ydata(self.AIN_line[2])
            if self.ids.ain3.state == 'down':
                self.graph_AIN3.set_xdata(self.Time_line)
                self.graph_AIN3.set_ydata(self.AIN_line[3])

            if self.ids.FIOs4.state == 'down':
                self.graph_FIO4.set_xdata(self.Time_line)
                self.graph_FIO4.set_ydata(self.FIO_line[0])
            if self.ids.FIOs5.state == 'down':
                self.graph_FIO5.set_xdata(self.Time_line)
                self.graph_FIO5.set_ydata(self.FIO_line[1])
            if self.ids.FIOs6.state == 'down':
                self.graph_FIO6.set_xdata(self.Time_line)
                self.graph_FIO6.set_ydata(self.FIO_line[2])
            if self.ids.FIOs7.state == 'down':
                self.graph_FIO7.set_xdata(self.Time_line)
                self.graph_FIO7.set_ydata(self.FIO_line[3])


            #self.datat.append(t)
            #self.datav.append(v[0])
            #self.datav2.append(v[1])

            #self.line.set_xdata(self.datat)
            #self.line.set_ydata(self.datav)

            #self.line2.set_xdata(self.datat)
            #self.line2.set_ydata(self.datav2)


            # print(type(self.Xx[0]))





            self.ax.set_xlim([self.Time_line[-1]-10,self.Time_line[-1]])


            if  len(self.Time_line) >= 415: ### Great Influence on FPS of plotting - Greater number/smaller fps
                self.ids.FPS_g.text=('FPS: '+str(round(401/(self.Time_line[-1]-self.Time_line[0]),2)))
                for i in range(len(self.AIN_data)):
                    self.AIN_line[i]=self.AIN_line[i][-400:]
                    self.FIO_line[i]=self.FIO_line[i][-400:]
                self.Time_line=self.Time_line[-400:]

            self.canvas.draw()
        except:
            print('Chyba - Jste pripojeni??')
        #time.sleep(0.04)




class guiApp(App):
    pass


if __name__ == '__main__':
    guiApp().run()

