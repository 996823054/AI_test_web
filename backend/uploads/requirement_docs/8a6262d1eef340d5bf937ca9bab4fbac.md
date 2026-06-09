# httpbin 状态码接口文档

## 1. 文档概述

本文档采用 **OpenAPI 3.0** 作为接口描述标准，用于描述 `httpbin.org` 的状态码测试接口。

该接口用于验证客户端、网关、接口自动化平台或监控系统对不同 HTTP 状态码的处理能力。调用方可以在路径中指定一个或多个状态码，服务端会返回对应的 HTTP 状态；当传入多个状态码时，服务端会随机返回其中一个。

| 项目 | 内容 |
| --- | --- |
| 服务名称 | httpbin.org |
| 接口名称 | 返回指定 HTTP 状态码 |
| OpenAPI 版本 | 3.0.3 |
| 基础地址 | `https://httpbin.org` |
| 接口路径 | `/status/{codes}` |
| 默认请求方式 | `GET` |
| 数据格式 | 无业务响应体，重点验证 HTTP 状态码 |
| 参考文档 | [httpbin Status codes](https://httpbin.org/#/Status_codes) |

## 2. OpenAPI 3.0 标准规范

> 如需导入 Swagger UI、Apifox、Postman 或其他支持 OpenAPI 的工具，建议将以下 YAML 内容单独保存为 `openapi.yaml` 后导入。

```yaml
openapi: 3.0.3
info:
  title: httpbin 状态码接口
  version: 1.0.0
  description: |
    用于测试客户端对不同 HTTP 状态码的处理能力。
    codes 可以是单个状态码，也可以是逗号分隔的多个状态码。
servers:
  - url: https://httpbin.org
    description: httpbin 官方服务
tags:
  - name: Status Codes
    description: HTTP 状态码测试接口
paths:
  /status/{codes}:
    get:
      tags:
        - Status Codes
      summary: 返回指定 HTTP 状态码
      description: |
        根据路径参数 codes 返回指定 HTTP 状态码。
        当 codes 为多个逗号分隔的状态码时，服务端会随机返回其中一个。
      operationId: getStatusCode
      parameters:
        - name: codes
          in: path
          required: true
          description: |
            一个或多个 HTTP 状态码。
            多个状态码使用英文逗号分隔，例如 200,400,500。
          schema:
            type: string
            example: "200"
          examples:
            success:
              summary: 返回 200
              value: "200"
            notFound:
              summary: 返回 404
              value: "404"
            random:
              summary: 从多个状态码中随机返回
              value: "200,400,500"
      responses:
        "100":
          description: Informational responses
        "200":
          description: Success
        "201":
          description: Created
        "202":
          description: Accepted
        "204":
          description: No Content
        "301":
          description: Moved Permanently
        "302":
          description: Found
        "304":
          description: Not Modified
        "400":
          description: Bad Request
        "401":
          description: Unauthorized
        "403":
          description: Forbidden
        "404":
          description: Not Found
        "409":
          description: Conflict
        "429":
          description: Too Many Requests
        "500":
          description: Internal Server Error
        "502":
          description: Bad Gateway
        "503":
          description: Service Unavailable
        default:
          description: 返回 codes 中指定的 HTTP 状态码
    post:
      tags:
        - Status Codes
      summary: 使用 POST 返回指定 HTTP 状态码
      description: 与 GET 行为一致，根据路径参数 codes 返回指定 HTTP 状态码。
      operationId: postStatusCode
      parameters:
        - $ref: "#/components/parameters/Codes"
      responses:
        default:
          description: 返回 codes 中指定的 HTTP 状态码
    put:
      tags:
        - Status Codes
      summary: 使用 PUT 返回指定 HTTP 状态码
      description: 与 GET 行为一致，根据路径参数 codes 返回指定 HTTP 状态码。
      operationId: putStatusCode
      parameters:
        - $ref: "#/components/parameters/Codes"
      responses:
        default:
          description: 返回 codes 中指定的 HTTP 状态码
    patch:
      tags:
        - Status Codes
      summary: 使用 PATCH 返回指定 HTTP 状态码
      description: 与 GET 行为一致，根据路径参数 codes 返回指定 HTTP 状态码。
      operationId: patchStatusCode
      parameters:
        - $ref: "#/components/parameters/Codes"
      responses:
        default:
          description: 返回 codes 中指定的 HTTP 状态码
    delete:
      tags:
        - Status Codes
      summary: 使用 DELETE 返回指定 HTTP 状态码
      description: 与 GET 行为一致，根据路径参数 codes 返回指定 HTTP 状态码。
      operationId: deleteStatusCode
      parameters:
        - $ref: "#/components/parameters/Codes"
      responses:
        default:
          description: 返回 codes 中指定的 HTTP 状态码
    trace:
      tags:
        - Status Codes
      summary: 使用 TRACE 返回指定 HTTP 状态码
      description: 与 GET 行为一致，根据路径参数 codes 返回指定 HTTP 状态码。
      operationId: traceStatusCode
      parameters:
        - $ref: "#/components/parameters/Codes"
      responses:
        default:
          description: 返回 codes 中指定的 HTTP 状态码
components:
  parameters:
    Codes:
      name: codes
      in: path
      required: true
      description: 一个或多个 HTTP 状态码，多个状态码使用英文逗号分隔。
      schema:
        type: string
        example: "200"
```

## 3. 接口说明

### 3.1 基本信息

| 字段 | 内容 |
| --- | --- |
| Method | `GET` / `POST` / `PUT` / `PATCH` / `DELETE` / `TRACE` |
| Path | `/status/{codes}` |
| URL | `https://httpbin.org/status/{codes}` |
| 认证方式 | 无 |
| 请求体 | 无 |
| 响应体 | 通常无业务 JSON body |
| 主要用途 | 验证客户端对 HTTP 状态码的处理逻辑 |

### 3.2 路径参数

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `codes` | path | string | 是 | `200` | 指定需要返回的 HTTP 状态码 |
| `codes` | path | string | 是 | `200,400,500` | 多个状态码使用英文逗号分隔，服务端随机返回其中一个 |

## 4. 请求示例

### 4.1 返回 200

```http
GET https://httpbin.org/status/200
```

预期结果：

```text
HTTP/1.1 200 OK
```

### 4.2 返回 404

```http
GET https://httpbin.org/status/404
```

预期结果：

```text
HTTP/1.1 404 Not Found
```

### 4.3 返回 500

```http
GET https://httpbin.org/status/500
```

预期结果：

```text
HTTP/1.1 500 Internal Server Error
```

### 4.4 随机返回多个状态码之一

```http
GET https://httpbin.org/status/200,400,500
```

预期结果：

```text
HTTP/1.1 200 OK
```

或：

```text
HTTP/1.1 400 Bad Request
```

或：

```text
HTTP/1.1 500 Internal Server Error
```

## 5. 响应说明

该接口主要通过 HTTP 状态码表达结果，通常不返回业务 JSON 响应体。

| 状态码范围 | 类型 | 说明 |
| --- | --- | --- |
| `1xx` | Informational | 请求已接收，继续处理 |
| `2xx` | Success | 请求成功 |
| `3xx` | Redirection | 需要重定向或使用缓存 |
| `4xx` | Client Error | 客户端请求错误 |
| `5xx` | Server Error | 服务端错误 |

常用状态码示例：

| 请求路径 | 预期状态码 | 说明 |
| --- | --- | --- |
| `/status/200` | `200` | 请求成功 |
| `/status/201` | `201` | 资源创建成功 |
| `/status/204` | `204` | 请求成功但无响应体 |
| `/status/301` | `301` | 永久重定向 |
| `/status/302` | `302` | 临时重定向 |
| `/status/400` | `400` | 请求参数错误 |
| `/status/401` | `401` | 未认证 |
| `/status/403` | `403` | 无权限 |
| `/status/404` | `404` | 资源不存在 |
| `/status/429` | `429` | 请求过多 |
| `/status/500` | `500` | 服务端错误 |
| `/status/503` | `503` | 服务不可用 |

## 6. 接口测试用例

### 6.1 返回 200

```json
{
  "name": "状态码接口-返回200",
  "method": "GET",
  "url": "https://httpbin.org/status/200",
  "expectedStatus": 200,
  "assertions": [
    {
      "type": "status_code",
      "expected": 200
    }
  ]
}
```

### 6.2 返回 404

```json
{
  "name": "状态码接口-返回404",
  "method": "GET",
  "url": "https://httpbin.org/status/404",
  "expectedStatus": 404,
  "assertions": [
    {
      "type": "status_code",
      "expected": 404
    }
  ]
}
```

### 6.3 返回 500

```json
{
  "name": "状态码接口-返回500",
  "method": "GET",
  "url": "https://httpbin.org/status/500",
  "expectedStatus": 500,
  "assertions": [
    {
      "type": "status_code",
      "expected": 500
    }
  ]
}
```

### 6.4 多状态码随机返回

```json
{
  "name": "状态码接口-多状态码随机返回",
  "method": "GET",
  "url": "https://httpbin.org/status/200,400,500",
  "expectedStatusIn": [200, 400, 500],
  "assertions": [
    {
      "type": "status_code_in",
      "expected": [200, 400, 500]
    }
  ]
}
```

## 7. 导入和维护建议

为保证接口文档具备行业通用性，建议遵循以下维护方式：

| 场景 | 建议 |
| --- | --- |
| API 平台导入 | 使用第 2 节 OpenAPI 3.0 YAML 内容 |
| 人工阅读 | 使用本文档的接口说明、请求示例和测试用例 |
| 自动化测试 | 以 OpenAPI 规范中的 `paths`、`parameters`、`responses` 为准 |
| 文档维护 | 避免同时混用 Swagger 2.0 和 OpenAPI 3.0 |
| 版本管理 | 接口结构变更时同步更新 `info.version` |

## 8. 变更记录

| 版本 | 日期 | 说明 |
| --- | --- | --- |
| 1.0.0 | 2026-05-11 | 按 OpenAPI 3.0 标准重新整理状态码接口文档 |
