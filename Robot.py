# Robot.py
import time
import numpy as np
from pymycobot import Pro450Client

class Robot:

    def __init__(self,
                 ip: str = "192.168.0.232",
                 port: int = 4500,
                 debug: int = 1,
                 ):
        # 1) 创建底层网口客户端（与小demo一致）
        self.mc = Pro450Client(ip, port, debug=debug)
        time.sleep(3)
        self.offset_x = +55.0    
        self.offset_y = +10.0

        # 2) 上电/模式初始化（与小demo保持一致，确保可读位姿/可运动）
        time.sleep(0.3)
        if hasattr(self.mc, "focus_all_servos"):
            self.mc.focus_all_servos()     # 使能扭矩
        time.sleep(0.3)
        if hasattr(self.mc, "set_fresh_mode"):
            self.mc.set_fresh_mode(0)      # 0=队列/非实时模式，通常更稳
        time.sleep(0.2)
        # ====== 参数（保持你原来的数值）======
        self.photo_angle = [-12.24, -7.77, -77.2, -18.16, -4.12, -57.28]
        self.end_angle   = [-64.18, 6.13, -100.3, 6.06, -7.91, -39.72]
        self.photo_coord = [222.7, -140.7, 260.9, 169.39, 8.82, -45.3]
        self.EyesInHand_matrix=np.array([[-1.83081906e-01,3.01688346e-02,3.04428114e+02],
        [-6.12363807e-03,1.91102870e-01,-1.51133833e+02]])
        self.sp = 50
        self.start_point = [-12.24, -7.77, -77.2, -18.16, -4.12, -57.28]
        #self.start_point = [15.73, 7.02, -127.56, 32.85, 6.54, -39.07]
        self.end_point   = [-64.18, 6.13, -100.3, 6.06, -7.91, -39.72]
        self.end= [-64.18, 6.13, -100.3, 6.06, -7.91, -39.72]

        # 坐标缓存（get_coords 偶发空回时兜底）
        self._last_coords = None

        # 3) 启动时先到初始姿态
        self.mc.send_angles(self.start_point, 50)
        self.wait_done()

    # ---------- 透传：让外部能直接用 mc.xxx 像 Pro450Client 一样 ----------
    def __getattr__(self, name):
        """
        未在本类显式定义的方法/属性，自动从 self.mc 上取。
        例如：mc.send_angles / mc.get_coords / mc.is_moving / mc.set_pro_gripper_open ...
        """
        return getattr(self.mc, name)

    # ---------- 工具 ----------
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
        self.set_pro_gripper_angle(70,14)
        self.set_pro_gripper_angle(70,14)
        time.sleep(2)
        for i in range(len(res)):
            if res[i][0] == color:
            # ② 像素->机器人XY
                u, v = res[i][1][0], res[i][1][1]
                pixel_coord = np.array([u, v, 1.0], dtype=float)
                target = self.EyesInHand_matrix.dot(pixel_coord)  # [X, Y]
                target = np.round(target, 2)

                # ③ 应用补偿
                target[0] += self.offset_x-20    # X 偏移
                target[1] += self.offset_y-5     # Y 偏移（左移90 => -90）

                # ④ 写入目标位姿（只改 XY，其余沿用原来的姿态/角度）
                self.photo_coord[0] = float(target[0])
                self.photo_coord[1] = float(target[1])

                # ⑤ 抓取路径（与你原逻辑一致）
                self.photo_coord[2] = 200
                self.send_coords(self.photo_coord, self.sp, 1)
                self.wait_done()

                self.photo_coord[2] = 120
                self.send_coords(self.photo_coord, self.sp, 1)
                self.wait_done()

                self.set_pro_gripper_angle(25, 14)
                self.set_pro_gripper_angle(25, 14)
                time.sleep(2)

                self.photo_coord[2] = 240
                self.send_coords(self.photo_coord, self.sp, 1)
                self.wait_done()

                self.send_angles(self.photo_angle, self.sp)
                self.wait_done()

                self.send_angles(self.end, self.sp)
                self.wait_done()

                for _ in range(3):
                    self.set_pro_gripper_open(14)
                    time.sleep(2)

                self.send_angles(self.photo_angle, self.sp)
                self.wait_done()


    def object_grab(self,res,object):
        self.set_pro_gripper_angle(90,14)
        self.set_pro_gripper_angle(90,14)
        time.sleep(2)
        for i in range(len(res)):
            if res[i][0]==object:
                u, v = res[i][1][0], res[i][1][1]
                pixel_coord = np.array([u, v, 1.0], dtype=float)
                target = self.EyesInHand_matrix.dot(pixel_coord)  # [X, Y]
                target = np.round(target, 2)

            # ③ 应用补偿
                target[0] += self.offset_x
                target[1] += self.offset_y

            # ④ 写入目标位姿（只改 XY，其余保持）
                self.photo_coord[0] = float(target[0])
                self.photo_coord[1] = float(target[1])
                self.photo_coord[2]=230
                # self.photo_coord[1]+=10
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.photo_coord[2]=140
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.set_pro_gripper_angle(50,14)
                self.set_pro_gripper_angle(50,14)
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
        self.set_pro_gripper_angle(100,14)
        self.set_pro_gripper_angle(100,14)
        time.sleep(2)
        for i in range(len(res)):
            if res[i][0]==object:
                u, v = res[i][1][0], res[i][1][1]
                pixel_coord = np.array([u, v, 1.0], dtype=float)
                target = self.EyesInHand_matrix.dot(pixel_coord)  # [X, Y]
                target = np.round(target, 2)
            # ③ 应用补偿
                target[0] += self.offset_x-20
                target[1] += self.offset_y-20
            # ④ 写入目标位姿（只改 XY，其余保持）
                self.photo_coord[0] = float(target[0])
                self.photo_coord[1] = float(target[1])
                self.photo_coord[2]=230
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                if object=="对乙酰氨基酚缓释片":
                    self.photo_coord[2]=160
                    value=75
                else:
                    self.photo_coord[2]=155
                    value=75
                self.send_coords(self.photo_coord,self.sp,1)
                self.wait_done()
                self.set_pro_gripper_angle(value,14)
                self.set_pro_gripper_angle(value,14)
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