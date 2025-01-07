"""
文件描述: 本文件用于获取本地设备的局域网 IP，用于推测可以连接的 IP 地址

创建者: 汐琳
创建时间: 2025-01-07 17:24:58
"""
import socket
import ipaddress

class NetworkUtils:
    def __init__(self):
        pass

    @staticmethod
    def get_local_ip():
        """
        获取本地设备的局域网 IP 地址
        :return: 返回本地 IP 地址
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('8.8.8.8', 80))  # 连接 Google DNS 服务器，获取本地网络接口 IP 地址
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'  # 如果连接失败，返回回环地址 --？
        finally:
            s.close()
        return local_ip

    def get_local_network_ips(self):
        """
        获取本机的局域网 IP 地址段
        :return: 局域网 IP 地址段列表
        """
        local_ip = self.get_local_ip()  # 获取本机 IP 地址
        local_network = ipaddress.IPv4Network(f'{local_ip}/24', strict=False)  # 假设子网掩码是 /24，即 255.255.255.0
        return list(local_network.hosts())  # 返回该子网内所有 IP 地址
