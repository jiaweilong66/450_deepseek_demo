import time
import numpy as np
from pymycobot import Pro450Client

mc = Pro450Client("192.168.0.232", 4500)

print(mc.get_angles())
print(mc.get_coords())