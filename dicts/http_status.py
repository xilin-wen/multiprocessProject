http_status_codes = {
    # 2xx Success - 请求成功处理
    200: "OK",  # 请求成功，通常返回请求的资源
    201: "Created",  # 请求成功且服务器创建了新资源
    202: "Accepted",  # 请求已接收，但尚未处理完成
    203: "Non-Authoritative Information",  # 请求成功，但响应数据来自代理服务器而非原服务器
    204: "No Content",  # 请求成功，但没有返回任何内容
    205: "Reset Content",  # 请求成功，但需要客户端重置文档视图
    206: "Partial Content",  # 请求成功并且响应体是部分内容（如支持断点续传）

    # 3xx Redirection - 客户端需要进一步操作来完成请求
    300: "Multiple Choices",  # 请求有多个可能的响应，客户端可以选择其一
    301: "Moved Permanently",  # 请求的资源已永久移动，客户端应使用新 URL
    302: "Found",  # 请求的资源临时移动，客户端应继续使用原 URL
    303: "See Other",  # 请求的资源可以通过其他 URL 获取
    304: "Not Modified",  # 请求的资源未修改，客户端可以使用缓存的版本
    305: "Use Proxy",  # 客户端必须通过代理访问请求的资源
    307: "Temporary Redirect",  # 请求的资源临时重定向，客户端应使用原方法继续请求
    308: "Permanent Redirect",  # 请求的资源永久重定向，客户端应使用原方法继续请求

    # 4xx Client Errors - 客户端错误，请求无效或权限不足
    400: "Bad Request",  # 请求格式错误，服务器无法理解
    401: "Unauthorized",  # 请求需要认证，未提供有效认证信息
    402: "Payment Required",  # 尚未广泛使用，表示需要支付才能继续请求
    403: "Forbidden",  # 请求被服务器拒绝，通常由于权限不足
    404: "Not Found",  # 请求的资源不存在，URL 无效
    405: "Method Not Allowed",  # 请求方法不被允许（如 GET、POST 不支持该资源）
    406: "Not Acceptable",  # 请求的资源无法满足客户端的接受条件
    407: "Proxy Authentication Required",  # 需要通过代理进行认证
    408: "Request Timeout",  # 客户端请求超时，服务器未收到完整请求
    409: "Conflict",  # 请求与当前资源状态冲突，通常用于并发操作
    410: "Gone",  # 请求的资源已被永久删除
    411: "Length Required",  # 请求头中缺少 Content-Length 字段
    412: "Precondition Failed",  # 请求头中的先决条件失败
    413: "Payload Too Large",  # 请求体过大，服务器无法处理
    414: "URI Too Long",  # 请求的 URL 太长，服务器无法处理
    415: "Unsupported Media Type",  # 请求的媒体类型不被支持
    416: "Range Not Satisfiable",  # 请求的范围无法满足，文件超出范围
    417: "Expectation Failed",  # 请求头中的 Expect 字段无法满足

    # 5xx Server Errors - 服务器错误，表示服务器处理请求时出现问题
    500: "Internal Server Error",  # 服务器内部错误，无法完成请求
    501: "Not Implemented",  # 服务器不支持请求的方法或功能
    502: "Bad Gateway",  # 服务器作为网关或代理时，收到来自上游服务器的无效响应
    503: "Service Unavailable",  # 服务器不可用，通常是因为过载或正在维护
    504: "Gateway Timeout",  # 服务器作为网关或代理时，未能从上游服务器及时获取响应
    505: "HTTP Version Not Supported",  # 服务器不支持客户端请求的 HTTP 版本
}
