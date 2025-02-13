"""
文件总述: 公司内部平台数据库字段

创建者: 汐琳
创建时间: 2025/2/11 11:49
"""
from dataclasses import dataclass
from typing import List


@dataclass
class ProductSeries:
    product_series_id: str
    product_series_name: str
    # product_series_list:

"""
机器：
零部件
"""
class Product:
    produce_id: str
    produce_Name: str
    product_series_id: str
    product_type: str

@dataclass
class School:
    school_video_id: str   # 视频id
    school_cover_img_id: str   # 封面url
    school_title: str   # 标题
    school_synopsis: str   # 简介
    school_type: int   # 类型：1-使用教程，2-保养教程，3-种植教程
    school_video_url_id: str   # 视频地址
    school_upload_date: str   # 上传日期
    school_upload_userId: str   # 上传者id
    
# 对采购订单的驳回记录
class RejectPurchaseOrderRecord:
    reject_purchase_order_record_id: str   # 主键Id
    pandag_staff_id: str   # 拒绝该订单的平台工作人员的id
    reject_reason: str   # 拒绝原因
    reject_time: str   # 拒绝时间
    order_purchase_id: str   # 采购订单id