"""
文件总述: 用户端数据库字段

创建者: 汐琳
创建时间: 2025/2/11 11:48
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Consumer:
    consumer_id: str    # 客户Id
    consumer_openId: str    # 客户微信openId
    consumer_name: str  # 客户名称
    consumer_name_initial: str  # 客户名称首字母
    consumer_phone_number: str  # 客户电话
    consumer_avatar_id: str    # 客户头像
    consumer_gender: str    # 客户性别
    consumer_birthday: str  # 客户生日
    consumer_birthday_is_update: bool   # 客户是否已经修改过生日
    consumer_had_read_videoId: List[str]    # 已经查看的视频id
    consumer_belong_branchId: str   # 客户所属网点

    consumer_possess_machine_list: List[str]    # 拥有的农机id
    consumer_collaborator_machine_list: List[str]    # 允许被协作的农机id
    consumer_possess_collaborator_list: List[str]    # 拥有的协作者id

@dataclass
class Machine:
    machine_serial_id: str  # 机器序列码
    machine_type: str   # 机器类型
    machine_name: str   # 机器名称
    machine_owner_id: str   # 机器所有者Id
    machine_collaborator_list: List[str]    # 协作者Id
    machine_insurance_id: str   # 机器保险单号
    machine_unseal_time: str    # 机器启封时间

    machine_current_battery: int    # 当前电量
    machine_status: int # 机器的状态：1-关闭；2-启动；3-启动且异常
    machine_status_drive_knife: int # 刀盘驱动状态：1-关闭；2-打开并运行；3-异常
    machine_status_drive_walk: int  # 行走驱动状态：1-关闭；2-打开并运行；3-异常

@dataclass
class School:
    school_video_id: str   # 视频id
    school_cover_img: str   # 封面url
    school_title: str   # 标题
    school_synopsis: str   # 简介
    school_type: int   # 类型：1-使用教程，2-保养教程，3-种植教程
    school_video_url: str   # 视频地址
    school_upload_date: str   # 上传日期
    school_upload_userId: str   # 上传者id

@dataclass
class Appointment:
    appointment_id: str   # 预约id
    appointment_type: int   # 预约类型
    appointment_date: str   # 预约日期
    appointment_time: int   # 预约时间段：1-上午，2-下午

   # 预约状态：
   # 1 - 用户申请，未被接单
   # 2 - 商家通过预约，等待用户前往
   # 3 - 到达预约时间，用户爽约未去
   # 4 - 到达预约时间，商家未处理
   # 5 - 到达预约时间，问题处理
    appointment_status: int   # 预约状态

    consumer_id: str   # 预约者id
    branch_id: str   # 网点id
    service_orderId: str   # 订单id

@dataclass
class ServiceOrder:
    service_orderId: str  # 订单id
    service_type: int  # 服务类型，1-保养，2-动力，3-外观，4-控制，5-未知，6-投诉，7-撤销（撤销暂时不做）
    service_description: str  # 故障描述
    service_price: int  # 成交价格

    consumer_id: str # 请求者id
    machine_serial_id: str  # 产品id
    appointment_id: str  # 预约id
    branchId: str  # 网点id - -新增
    workOrderId: str  # 工单id - -新增

@dataclass
class MaintenanceOrder:
    maintenance_OrderId: str   # 维护代办列表
    maintenance_Type: int   # 1:系统检测，2：自主申报
    maintenance_Title: str   # 消息标题
    maintenance_Content: str   # 消息内容
    maintenance_Status: int   # 1：待处理，2：处理中，3：已完成，4：已投诉

    consumer_id: str   # 申报者id
    machine_serial_id: str   # 机器id
    service_orderId: str   # 订单id
    workOrderId: str   # 工单id