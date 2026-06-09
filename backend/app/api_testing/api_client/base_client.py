"""
基础请求封装
============
纯 HTTP 请求封装，不包含任何业务逻辑。
目标练习接口：https://reqres.in/api

你需要实现 BaseClient 类：
    1. __init__(self, base_url, timeout=30, headers=None)
       → self.base_url = base_url.rstrip("/")  去掉末尾斜杠
       → self.timeout = timeout
       → self.session = requests.Session()      创建会话对象
       → self.session.headers.update({"Content-Type": "application/json"})
       → 如果传了 headers，也 update 进去

    2. set_token(self, token, scheme="Bearer")
       → 设置 self.session.headers["Authorization"] = f"{scheme} {token}"

    3. request(self, method, path, **kwargs)
       → 拼接完整 URL：f"{self.base_url}/{path.lstrip('/')}"
       → 设置默认超时：kwargs.setdefault("timeout", self.timeout)
       → 记录请求日志：logger.info(f">>> {method.upper()} {url}")
       → 如果 kwargs 中有 "json"，记录请求体日志
       → 如果 kwargs 中有 "params"，记录查询参数日志
       → 用 time.time() 记录开始时间
       → 调用 self.session.request(method, url, **kwargs) 发送请求
       → 计算耗时：round(time.time() - start, 3)
       → 记录响应日志：logger.info(f"<<< {resp.status_code} ({elapsed}s)")
       → return resp

    4. get(self, path, params=None, **kwargs) → Response
       → return self.request("GET", path, params=params, **kwargs)

    5. post(self, path, json=None, **kwargs) → Response
       → return self.request("POST", path, json=json, **kwargs)

    6. put(self, path, json=None, **kwargs) → Response
       → return self.request("PUT", path, json=json, **kwargs)

    7. delete(self, path, **kwargs) → Response
       → return self.request("DELETE", path, **kwargs)

    8. patch(self, path, json=None, **kwargs) → Response
       → return self.request("PATCH", path, json=json, **kwargs)

    9. extract(resp, field) → Any  （静态方法 @staticmethod）
       → 从响应 JSON 中按 "." 路径提取值
       → 例：extract(resp, "data.token") → resp.json()["data"]["token"]
       → 实现：data = resp.json()
               遍历 field.split(".")，逐层取值：
                 如果 data 是 dict → data = data.get(key)
                 如果 data 是 list 且 key 是数字 → data = data[int(key)]
                 否则 → return None
               return data

    10. assert_status(resp, expected=200)  （静态方法）
        → assert resp.status_code == expected
        → 失败信息包含：期望值、实际值、响应体前 300 字符

    11. assert_json_field(resp, field, expected)  （静态方法）
        → 用 extract 取出字段值
        → assert actual == expected

    12. close(self)
        → self.session.close()

    13. __enter__(self) / __exit__(self, *args)
        → 支持 with BaseClient(...) as client: 用法
        → __enter__ return self
        → __exit__ 调用 self.close()

提示：
    - requests.Session 会自动保持 cookie 和 headers
    - request 方法是核心，所有 get/post/put/delete/patch 都调用它
    - 用 try/except 保护 resp.json()，响应不一定是 JSON
    - logger 用 logging.getLogger(__name__) 创建
"""

import re
import requests
import time
import json
import logging
from typing import Any
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

# TODO: 在这里实现 BaseClient 类

class BaseClient:
    def __init__(self, base_url, timeout=30, headers=None):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        if headers:
            self.session.headers.update(headers)
    
    def set_token(self, token, scheme="Bearer"):
        self.session.headers['Authorization'] = f'{scheme} {token}'

    def request(self,method, path,**kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault('timeout',self.timeout)
        logger.info(f">>>{method.upper()} {url}")
        if kwargs.get('json'):
            logger.info(f"request body:{kwargs['json']}")
        if kwargs.get('params'):
            logger.info(f"request params:{kwargs['params']}")
        start_time = time.time()
        reqsep = self.session.request(method,url,**kwargs)
        elapsed = round(time.time() - start_time,3)
        logger.info(f"<<<{reqsep.status_code}({elapsed}s)")
        return reqsep
    
    def get(self, path,params=None,**kwargs) ->requests.Response:
        return self.request('get',path,params=params,**kwargs)

    def post(self,path,json = None,**kwargs) -> requests.Response:
        return self.request("post",path,json = json,**kwargs)

    def put(self,path,json = None,**kwargs) -> requests.Response:
        return self.request('put',path ,json=json,**kwargs)
    
    def delete(self,path,**kwargs) -> requests.Response:
        return self.request('delete',path,**kwargs)
    
    def patch(self,path,json = None,**kwargs):
        return self.request('patch',path,json = json,**kwargs)

    @staticmethod
    def extract(resp,field):
        try:
            date = resp.json()
        except Exception:
            return None
        for key in field.split("."):
            if isinstance(date,dict):
                date = date.get(key)
            elif isinstance(date,list) and key.isdigit():
                index = int(key)
                if index >=len(date):
                    return None
                date = date[int(key)]
            else:
                return None
        return date

    @staticmethod
    def assert_status(resp,expected=200):
        body_preview = resp.text[:300]
        assert resp.status_code == expected,(
            f"expcted status {expected},got{resp.status_code},body:{body_preview}"
        )

    @staticmethod
    def assert_json_field(resp,field,expected):
        actual = BaseClient.extract(resp,field)
        assert actual == expected,f"Expected {field}={expected}, got {actual}"

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self,exc_type, exc_value, traceback):
        self.close()


