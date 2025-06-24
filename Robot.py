import cv2
import numpy as np
from pymycobot import MyCobot320,utils
import time

class Robot(MyCobot320):
    def __init__(self):
        super().__init__(utils.get_port_list()[0])
        self.photo_angle=[0.35, -4.48, -33.04, -55.1, 89.64, 46.75]
        self.end_angle=[88.85, -9.93, -67.41, -14.58, 86.13, 128.14]
        self.photo_coord=[176.0, -88.1, 333.8, 178.44, -2.16, -136.36]
        self.EyesInHand_matrix=np.array([[-2.36494964e-02 , 4.90217708e-01 , 1.29350576e+02],
        [ 5.08590888e-01 ,-2.50828565e-02 ,-2.54288197e+02]])
        self.sp=50
        self.cam_coord=None
        self.start_point=[-2.46, 16.78, -101.68, -0.7, 90.35, 51.41]
        self.end_point=[88.85, -9.93, -67.41, -14.58, 86.13, 128.14]
        self.send_angles([-2.46, 16.78, -101.68, -0.7, 90.35, 51.41],50)
        self.wait_done()
        self.end=[88.24, -16.87, -49.13, -32.25, 85.86, 127.88]


    def wait_done(self):
        time.sleep(1.5)
        while self.is_moving()==1:
            time.sleep(1.5)
    
    def action(self,*args):
        tmp= None
        
        while tmp is None:
            tmp=self.get_coords()
            time.sleep(0.5)
        if args[0]=='front' :
            tmp[0]+=args[1]
            self.send_coords(tmp,100,1)
            self.wait_done()
        elif args[0]=='back':
            tmp[0]-=args[1]
            self.send_coords(tmp,100,1)
            self.wait_done()
        if args[0]=='right' :
            tmp[1]+=args[1]
            self.send_coords(tmp,100,1)
            self.wait_done()
        elif args[0]=='left':
            tmp[1]-=args[1]
            self.send_coords(tmp,100,1)
            self.wait_done()

        elif args[0]=='open':
            self.set_pro_gripper_open(14)
            time.sleep(2)
            self.set_pro_gripper_open(14)
            # time.sleep(2)
        elif args[0]=='close':
            self.set_pro_gripper_close(14)
            time.sleep(2)
            self.set_pro_gripper_close(14)

    def go_photo_position(self):
        self.send_angles(self.photo_angle,self.sp)
        self.wait_done()
    
    def color_grab(self,res,color):
        self.set_pro_gripper_angle(14,100)
        self.set_pro_gripper_angle(14,100)
        time.sleep(2)
        for i in range(len(res)):
            if res[i][0]==color:
                pixel_coord=np.array([res[i][1][0], res[i][1][1],1])
                tagrget=self.EyesInHand_matrix.dot(pixel_coord)
                for i in range(2):
                    tagrget[i]=round(tagrget[i],2)
                for i in range(2):
                    self.photo_coord[i]=tagrget[i]
                self.photo_coord[2]=230
                # self.photo_coord[1]+=30
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.photo_coord[2]=180
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.set_pro_gripper_angle(14,30)
                self.set_pro_gripper_angle(14,30)
                time.sleep(2)
                self.photo_coord[2]=260
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.send_angles(self.photo_angle,self.sp)
                self.wait_done()
                self.send_angles(self.end,self.sp)
                self.wait_done()
                for i in range(3):
                    self.set_pro_gripper_open(14)
                    time.sleep(2)
                self.send_angles(self.photo_angle,self.sp)
                self.wait_done()


    def object_grab(self,res,object):
        self.set_pro_gripper_angle(14,90)
        self.set_pro_gripper_angle(14,90)
        time.sleep(2)
        for i in range(len(res)):
            if res[i][0]==object:
                pixel_coord=np.array([res[i][1][0], res[i][1][1],1])
                tagrget=self.EyesInHand_matrix.dot(pixel_coord)
                for i in range(2):
                    tagrget[i]=round(tagrget[i],2)
                for i in range(2):
                    self.photo_coord[i]=tagrget[i]
                self.photo_coord[2]=230
                # self.photo_coord[1]+=10
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.photo_coord[2]=160
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.set_pro_gripper_angle(14,30)
                self.set_pro_gripper_angle(14,30)
                time.sleep(2)
                self.photo_coord[2]=260
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.send_angles(self.photo_angle,self.sp)
                self.wait_done()
                self.send_angles(self.end,self.sp)
                self.wait_done()
                for i in range(3):
                    self.set_pro_gripper_open(14)
                    time.sleep(2)
                self.send_angles(self.photo_angle,self.sp)
                self.wait_done()


    def medicine_grab(self,res,object):
        self.set_pro_gripper_angle(14,100)
        self.set_pro_gripper_angle(14,100)
        time.sleep(2)
        for i in range(len(res)):
            if res[i][0]==object:
                pixel_coord=np.array([res[i][1][0], res[i][1][1],1])
                tagrget=self.EyesInHand_matrix.dot(pixel_coord)
                for i in range(2):
                    tagrget[i]=round(tagrget[i],2)
                for i in range(2):
                    self.photo_coord[i]=tagrget[i]
                self.photo_coord[0]-=10
                self.photo_coord[2]=230
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                if object=="盐酸苯环壬酯片":
                    self.photo_coord[2]=160
                    value=60
                else:
                    self.photo_coord[2]=180
                    value=60
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.set_pro_gripper_angle(14,value)
                self.set_pro_gripper_angle(14,value)
                time.sleep(2)
                self.photo_coord[2]=260
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.send_angles(self.photo_angle,self.sp)
                self.wait_done()
                self.send_angles(self.end,self.sp)
                self.wait_done()
                for i in range(3):
                    self.set_pro_gripper_open(14)
                    time.sleep(2)
                self.send_angles(self.photo_angle,self.sp)
                self.wait_done()
            


if __name__=="__main__":
    r=Robot()
    



        

        


   
