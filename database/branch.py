"""
文件总述: 商家端数据库字段

创建者: 汐琳
创建时间: 2025/2/11 11:48
"""
from dataclasses import dataclass
from typing import List


@dataclass
class Branch:
    branch_id: str  # 网点id
    branch_name: str  # 网点名称
    branch_log_lat: tuple[float, float]  # 网点经纬度坐标
    administrator_id: str  # 网点超管id

@dataclass
class Administrator:
    administrator_id: str
    administrator_openId: str
    administrator_name: str  # 名称
    administrator_phone_number: str  # 手机号
    administrator_avatar_id: str  # 头像id
    administrator_gender: int  # 性别:0 - 女，1 - 男
    administrator_birthday: str  # 生日
    administrator_had_read_videoId: List[str]  # 已经查看的视频id

    administrator_belong_branch_id: str  # 所属网点id

@dataclass
class ComplaintRecord:
    complaint_record_id: str  # 投诉记录id
    consumer_id: str  # 投诉者id
    branch_id: str  # 网点id
    complaint_record_create_time: str  # 投诉时间
    complaint_record_reason: str  # 投诉原因
    appeal_time: str  # 申诉时间
    appeal_reason: str  # 申诉原因
    complaint_status: int  # 投诉状态：1-投诉中；2-申诉中；3-申诉成功；4-申诉失败
    complaint_record_end_time: str  # 投诉结束时间
    order_service_work_id: str  # 被投诉的服务类工单Id

@dataclass
class OrderSalesWork:
    order_sales_work_id: str  # 销售工单id
    order_sales_work_create_time: str  # 创建时间 YYYY-MM-DD HH:mm:ss
    order_sales_work_type: int  # 销售工单类型：1-整机；2-零部件
    order_sales_work_status: int  # 销售工单状态：1-正常；2-撤销
    machine_id: str  # 机器序列码

    consumer_id: str  # 用户id（服务对象id）
    branch_id: str  # 销售者id
    machine_main_id: str  # 整机id --销售主机时为空，销售零部件时是主体
    order_service_work_id: str  # 销售工单类型为整机时为空，为零部件时，需要挂在维修工单上
    # productFactoryVersionInfo: productFactoryVersion[]  # 产品在平台的记录表

@dataclass
class OrderServiceWork:
    order_service_work_id: str  # 工单id
    order_service_work_type: int  # 维修/保养类型；1-保养，2-动力，3-外观，4-控制，5-未知
    order_service_work_source: int  # 工单来源：1-用户主动申报；2-系统检测；3-商家自主创建
    order_service_work_status: int  # 工单状态：1-待受理（该状态下需要将订单指派到具体执行人身上，包括管理或超管）；2-处理中；3-执行完成
    order_service_work_create_time: str  # 创建时间 YYYY-MM-DD HH: mm:ss
    order_service_work_process_time: str  # 受理时间 YYYY-MM-DD HH: mm:ss
    order_service_work_finish_time: str  # 结束时间 YYYY-MM-DD HH: mm:ss
    order_service_work_content: str  # 工单服务内容
    # order_service_work_price: int  # 成交价格

    machine_id: str  # 机器id
    consumer_id: str  # 用户id（服务对象id）
    branch_id: str  # 网点id
    order_sales_work_id: List[OrderSalesWork]  # 购买（零部件）订单列表
    service_order_id: str  # 用户提交的订单id

    complaint_record_id: str  # 投诉记录

    scoring_record_id: str  # 评分记录id

@dataclass
class ScoringRecord:
    scoring_record_id: str  # 评分记录id
    scoring_responding_speed_user: int  # 响应速度评分
    scoring_service_quality_user: int  # 服务质量评分
    scoring_time_user: str  # 评分时间 YYYY-MM-DD HH:mm:ss
    responding_speed_system: int  # 系统自测响应速度评分

    consumer_id: str  # 评分用户id
    branch_id: str  # 网点id
    order_service_work_id: str  # 用户服务订单id

@dataclass
class OrderPurchaseItem:
    order_purchase_item_id: str  # _id
    product_id: str  # 产品id
    product_quantity: int  # 产品数量

@dataclass
class OrderPurchase:
    order_purchase_id: str  # 采购订单id【对商家来说即进货批次】
    order_purchase_status: int  # 进货状态：1-待超管审批；2-超管同意；3-超管拒绝；4-平台同意，待发货；5-平台拒绝；6-申诉待审核；7-申诉被拒；8-已撤回；9-已完成；10-发货中；11-已到货
    order_purchase_create_time: str  # 采购工单创建时间 YYYY-MM-DD HH:mm:ss
    order_purchase_end_Time: str  # 采购工单结束时间 YYYY-MM-DD HH:mm:ss

    branch_id: str  # 网点id
    purchase_order_item: List[OrderPurchaseItem]  # 采购明细
    # deliveryInfo: deliveryToBranch[]  # 出库订单

@dataclass
class MessageBranch:
    message_branch_id: str  # 消息Id
    message_branch_type: int  # 消息类型 1-采购消息；2-客户消息；3-系统消息
    message_branch_title: str  # 消息标题
    message_branch_content: str  # 消息内容
    message_branch_create_time: str  # 消息创建/推送时间
    message_branch_has_read: int  # 消息是否已读 0-未读，1-已读

    consumer_id: str  # 消息拥有者Id