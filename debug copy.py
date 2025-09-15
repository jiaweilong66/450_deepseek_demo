import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"设备: {port.device}, 描述: {port.description}, 硬件ID: {port.hwid}")
