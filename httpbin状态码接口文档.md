# JSONPlaceholder REST API 接口文档（企业标准版）

| 文档属性 | 内容 |
| --- | --- |
| 文档状态 | 已基线 |
| 文档版本 | 1.0.0 |
| 最后更新日期 | 2026-06-09 |
| 维护方 | API 测试平台 / 接口自动化团队 |
| 适用对象 | 前端、后端、测试、接口自动化平台、Mock 服务使用方 |
| 安全等级 | Public，接口使用公开 Fake Data，不应传输业务敏感数据 |
| 依赖服务 | `https://jsonplaceholder.typicode.com` |
| 来源依据 | [JSONPlaceholder 官网](https://jsonplaceholder.typicode.com/) |

## 1. 文档概述

本文档基于 JSONPlaceholder 官方公开能力整理。JSONPlaceholder 是一个免费的在线 Fake REST API，适用于接口调试、前端原型、示例代码、接口自动化演示和本地开发测试。

JSONPlaceholder 由 JSON Server 和 LowDB 驱动，官网说明其提供 6 类常用资源，并支持常见 REST 路由和 HTTP 方法。本文档将官网信息整理为企业接口文档格式，包含接口契约、资源模型、请求参数、响应示例、异常说明、测试用例和维护建议。

| 项目 | 内容 |
| --- | --- |
| 服务名称 | JSONPlaceholder |
| 服务类型 | Fake REST API / Mock API |
| 基础地址 | `https://jsonplaceholder.typicode.com` |
| 请求协议 | HTTPS，官网也说明支持 HTTP |
| 数据格式 | JSON |
| 认证方式 | 无认证 |
| 主要用途 | 测试、原型、演示、接口自动化样例 |
| 是否生产可依赖 | 否，不应作为生产业务强依赖 |

### 1.1 适用范围

本文档适用于以下场景：

- 前端页面在后端接口未就绪时使用假数据进行原型开发。
- 接口自动化平台验证 `GET`、`POST`、`PUT`、`PATCH`、`DELETE` 等基础能力。
- 测试工具、SDK、网关或监控系统构造稳定的 REST API 示例。
- AI 测试平台生成接口用例、断言规则和 Mock 数据样例。

本文档不覆盖以下内容：

- 不承诺 JSONPlaceholder 官方公开服务的 SLA、容量、限流和可用性。
- 不作为真实业务数据模型、权限模型或持久化行为的设计依据。
- 不建议把该服务作为生产环境业务链路依赖。

### 1.2 企业接口文档检查结论

| 检查项 | 结论 |
| --- | --- |
| 接口基本信息 | 已包含服务名、Base URL、协议、认证、数据格式和用途 |
| 来源依据 | 已明确来源为 JSONPlaceholder 官网 |
| 资源清单 | 已覆盖 `posts`、`comments`、`albums`、`photos`、`todos`、`users` |
| REST 路由 | 已覆盖列表、详情、关联查询、查询参数、创建、全量更新、部分更新、删除 |
| OpenAPI 契约 | 已提供可导入的 OpenAPI 3.0 YAML |
| 请求说明 | 已包含路径参数、查询参数、请求头和请求体说明 |
| 响应说明 | 已包含主要响应字段、状态码、示例和断言建议 |
| 测试验收 | 已包含正向、查询、创建、更新、删除和异常边界用例 |
| 维护治理 | 已包含安全、合规、运维、导入和变更记录 |

## 2. 资源与路由总览

### 2.1 资源清单

| 资源 | 官方数量 | 说明 | 常见关系 |
| --- | ---: | --- | --- |
| `/posts` | 100 | 文章数据 | `posts` 与 `comments` 存在一对多关系 |
| `/comments` | 500 | 评论数据 | 可通过 `postId` 查询某篇文章的评论 |
| `/albums` | 100 | 相册数据 | `albums` 与 `photos` 存在一对多关系 |
| `/photos` | 5000 | 图片数据 | 可通过 `albumId` 查询某个相册下的图片 |
| `/todos` | 200 | 待办事项数据 | 与 `users` 存在用户归属关系 |
| `/users` | 10 | 用户数据 | 可关联 `posts`、`albums`、`todos` |

### 2.2 官方路由

| Method | Path | 说明 |
| --- | --- | --- |
| `GET` | `/posts` | 查询文章列表 |
| `GET` | `/posts/1` | 查询指定文章详情 |
| `GET` | `/posts/1/comments` | 查询指定文章下的评论 |
| `GET` | `/comments?postId=1` | 按查询参数查询评论 |
| `POST` | `/posts` | 创建文章 |
| `PUT` | `/posts/1` | 全量更新文章 |
| `PATCH` | `/posts/1` | 部分更新文章 |
| `DELETE` | `/posts/1` | 删除文章 |

说明：官网声明所有 HTTP 方法均支持。创建、更新、删除接口会返回模拟结果，但不会真实持久化到远端数据源。

## 3. OpenAPI 3.0 标准规范

> 如需导入 Swagger UI、Apifox、Postman 或其他支持 OpenAPI 的工具，建议将以下 YAML 内容单独保存为 `openapi.yaml` 后导入。

```yaml
openapi: 3.0.3
info:
  title: JSONPlaceholder REST API
  version: 1.0.0
  description: |
    JSONPlaceholder 是免费在线 Fake REST API，适用于测试、原型和接口自动化演示。
    本 OpenAPI 契约覆盖官网展示的核心资源、路由和常见请求方式。
  contact:
    name: API 测试平台 / 接口自动化团队
servers:
  - url: https://jsonplaceholder.typicode.com
    description: JSONPlaceholder 官方公开服务
externalDocs:
  description: JSONPlaceholder 官网
  url: https://jsonplaceholder.typicode.com/
tags:
  - name: Posts
    description: 文章资源
  - name: Comments
    description: 评论资源
  - name: Albums
    description: 相册资源
  - name: Photos
    description: 图片资源
  - name: Todos
    description: 待办事项资源
  - name: Users
    description: 用户资源
security: []
paths:
  /posts:
    get:
      tags: [Posts]
      summary: 查询文章列表
      operationId: listPosts
      parameters:
        - $ref: "#/components/parameters/UserIdQuery"
      responses:
        "200":
          description: 查询成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Post"
    post:
      tags: [Posts]
      summary: 创建文章
      operationId: createPost
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/PostCreateRequest"
      responses:
        "201":
          description: 创建成功；返回模拟创建后的文章对象
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Post"
  /posts/{id}:
    get:
      tags: [Posts]
      summary: 查询文章详情
      operationId: getPost
      parameters:
        - $ref: "#/components/parameters/IdPath"
      responses:
        "200":
          description: 查询成功
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Post"
        "404":
          description: 资源不存在
    put:
      tags: [Posts]
      summary: 全量更新文章
      operationId: replacePost
      parameters:
        - $ref: "#/components/parameters/IdPath"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/PostUpdateRequest"
      responses:
        "200":
          description: 更新成功；返回模拟更新后的文章对象
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Post"
    patch:
      tags: [Posts]
      summary: 部分更新文章
      operationId: updatePost
      parameters:
        - $ref: "#/components/parameters/IdPath"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/PostPatchRequest"
      responses:
        "200":
          description: 更新成功；返回模拟更新后的文章对象
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Post"
    delete:
      tags: [Posts]
      summary: 删除文章
      operationId: deletePost
      parameters:
        - $ref: "#/components/parameters/IdPath"
      responses:
        "200":
          description: 删除成功；返回空对象或模拟结果
          content:
            application/json:
              schema:
                type: object
  /posts/{id}/comments:
    get:
      tags: [Comments]
      summary: 查询指定文章下的评论
      operationId: listCommentsByPostPath
      parameters:
        - $ref: "#/components/parameters/IdPath"
      responses:
        "200":
          description: 查询成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Comment"
  /comments:
    get:
      tags: [Comments]
      summary: 查询评论列表
      operationId: listComments
      parameters:
        - $ref: "#/components/parameters/PostIdQuery"
      responses:
        "200":
          description: 查询成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Comment"
  /albums:
    get:
      tags: [Albums]
      summary: 查询相册列表
      operationId: listAlbums
      parameters:
        - $ref: "#/components/parameters/UserIdQuery"
      responses:
        "200":
          description: 查询成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Album"
  /photos:
    get:
      tags: [Photos]
      summary: 查询图片列表
      operationId: listPhotos
      parameters:
        - $ref: "#/components/parameters/AlbumIdQuery"
      responses:
        "200":
          description: 查询成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Photo"
  /todos:
    get:
      tags: [Todos]
      summary: 查询待办事项列表
      operationId: listTodos
      parameters:
        - $ref: "#/components/parameters/UserIdQuery"
      responses:
        "200":
          description: 查询成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Todo"
  /users:
    get:
      tags: [Users]
      summary: 查询用户列表
      operationId: listUsers
      responses:
        "200":
          description: 查询成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/User"
  /users/{id}:
    get:
      tags: [Users]
      summary: 查询用户详情
      operationId: getUser
      parameters:
        - $ref: "#/components/parameters/IdPath"
      responses:
        "200":
          description: 查询成功
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
components:
  parameters:
    IdPath:
      name: id
      in: path
      required: true
      description: 资源 ID，通常为正整数。
      schema:
        type: integer
        minimum: 1
      example: 1
    UserIdQuery:
      name: userId
      in: query
      required: false
      description: 用户 ID，用于筛选归属于指定用户的资源。
      schema:
        type: integer
        minimum: 1
      example: 1
    PostIdQuery:
      name: postId
      in: query
      required: false
      description: 文章 ID，用于筛选指定文章下的评论。
      schema:
        type: integer
        minimum: 1
      example: 1
    AlbumIdQuery:
      name: albumId
      in: query
      required: false
      description: 相册 ID，用于筛选指定相册下的图片。
      schema:
        type: integer
        minimum: 1
      example: 1
  schemas:
    Post:
      type: object
      required: [userId, id, title, body]
      properties:
        userId:
          type: integer
          example: 1
        id:
          type: integer
          example: 1
        title:
          type: string
          example: sunt aut facere repellat provident occaecati excepturi optio reprehenderit
        body:
          type: string
          example: quia et suscipit suscipit recusandae consequuntur expedita et cum
    PostCreateRequest:
      type: object
      required: [title, body, userId]
      properties:
        title:
          type: string
          example: foo
        body:
          type: string
          example: bar
        userId:
          type: integer
          example: 1
    PostUpdateRequest:
      allOf:
        - $ref: "#/components/schemas/PostCreateRequest"
    PostPatchRequest:
      type: object
      properties:
        title:
          type: string
          example: foo
        body:
          type: string
          example: bar
        userId:
          type: integer
          example: 1
    Comment:
      type: object
      required: [postId, id, name, email, body]
      properties:
        postId:
          type: integer
          example: 1
        id:
          type: integer
          example: 1
        name:
          type: string
          example: id labore ex et quam laborum
        email:
          type: string
          format: email
          example: Eliseo@gardner.biz
        body:
          type: string
          example: laudantium enim quasi est quidem magnam voluptate ipsam eos
    Album:
      type: object
      required: [userId, id, title]
      properties:
        userId:
          type: integer
          example: 1
        id:
          type: integer
          example: 1
        title:
          type: string
          example: quidem molestiae enim
    Photo:
      type: object
      required: [albumId, id, title, url, thumbnailUrl]
      properties:
        albumId:
          type: integer
          example: 1
        id:
          type: integer
          example: 1
        title:
          type: string
          example: accusamus beatae ad facilis cum similique qui sunt
        url:
          type: string
          format: uri
          example: https://via.placeholder.com/600/92c952
        thumbnailUrl:
          type: string
          format: uri
          example: https://via.placeholder.com/150/92c952
    Todo:
      type: object
      required: [userId, id, title, completed]
      properties:
        userId:
          type: integer
          example: 1
        id:
          type: integer
          example: 1
        title:
          type: string
          example: delectus aut autem
        completed:
          type: boolean
          example: false
    User:
      type: object
      required: [id, name, username, email]
      properties:
        id:
          type: integer
          example: 1
        name:
          type: string
          example: Leanne Graham
        username:
          type: string
          example: Bret
        email:
          type: string
          format: email
          example: Sincere@april.biz
```

## 4. 接口说明

### 4.1 基本信息

| 字段 | 内容 |
| --- | --- |
| Base URL | `https://jsonplaceholder.typicode.com` |
| Content-Type | `application/json; charset=UTF-8` |
| Accept | `application/json` |
| 认证方式 | 无 |
| 请求体格式 | JSON |
| 响应体格式 | JSON |
| 是否真实持久化 | 否，写操作返回模拟结果 |
| 超时建议 | 客户端建议设置 5 秒连接超时、10 秒总请求超时 |

### 4.2 请求头

| Header | 必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| `Accept` | 否 | `application/json` | 建议声明期望 JSON 响应 |
| `Content-Type` | 写操作必填 | `application/json; charset=UTF-8` | `POST`、`PUT`、`PATCH` 请求体格式 |
| `User-Agent` | 否 | `api-test-platform/1.0` | 建议自动化平台传入，便于日志识别 |

### 4.3 路径参数

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `id` | path | integer | 是 | `1` | 资源 ID，常用于详情、更新、删除和关联查询 |

### 4.4 查询参数

| 参数名 | 位置 | 类型 | 必填 | 示例 | 适用接口 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `postId` | query | integer | 否 | `1` | `/comments` | 按文章 ID 查询评论 |
| `userId` | query | integer | 否 | `1` | `/posts`、`/albums`、`/todos` | 按用户 ID 查询资源 |
| `albumId` | query | integer | 否 | `1` | `/photos` | 按相册 ID 查询图片 |

### 4.5 请求体

创建文章请求体：

```json
{
  "title": "foo",
  "body": "bar",
  "userId": 1
}
```

全量更新文章请求体：

```json
{
  "id": 1,
  "title": "foo",
  "body": "bar",
  "userId": 1
}
```

部分更新文章请求体：

```json
{
  "title": "foo"
}
```

## 5. 请求与响应示例

### 5.1 查询文章列表

```http
GET https://jsonplaceholder.typicode.com/posts
Accept: application/json
```

curl 示例：

```bash
curl -i "https://jsonplaceholder.typicode.com/posts" \
  -H "Accept: application/json"
```

预期结果：

```text
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
```

响应体示例：

```json
[
  {
    "userId": 1,
    "id": 1,
    "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
    "body": "quia et suscipit suscipit recusandae consequuntur expedita et cum"
  }
]
```

### 5.2 查询文章详情

```http
GET https://jsonplaceholder.typicode.com/posts/1
Accept: application/json
```

预期结果：

```text
HTTP/1.1 200 OK
```

核心断言：

- `status` 等于 `200`。
- 响应体包含 `userId`、`id`、`title`、`body`。
- `id` 等于 `1`。

### 5.3 查询文章评论

路径方式：

```http
GET https://jsonplaceholder.typicode.com/posts/1/comments
Accept: application/json
```

查询参数方式：

```http
GET https://jsonplaceholder.typicode.com/comments?postId=1
Accept: application/json
```

响应体示例：

```json
[
  {
    "postId": 1,
    "id": 1,
    "name": "id labore ex et quam laborum",
    "email": "Eliseo@gardner.biz",
    "body": "laudantium enim quasi est quidem magnam voluptate ipsam eos"
  }
]
```

### 5.4 创建文章

```http
POST https://jsonplaceholder.typicode.com/posts
Content-Type: application/json; charset=UTF-8
Accept: application/json

{
  "title": "foo",
  "body": "bar",
  "userId": 1
}
```

curl 示例：

```bash
curl -i -X POST "https://jsonplaceholder.typicode.com/posts" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "Accept: application/json" \
  -d '{"title":"foo","body":"bar","userId":1}'
```

预期结果：

```text
HTTP/1.1 201 Created
```

响应体示例：

```json
{
  "title": "foo",
  "body": "bar",
  "userId": 1,
  "id": 101
}
```

### 5.5 全量更新文章

```http
PUT https://jsonplaceholder.typicode.com/posts/1
Content-Type: application/json; charset=UTF-8
Accept: application/json

{
  "id": 1,
  "title": "foo",
  "body": "bar",
  "userId": 1
}
```

预期结果：

```text
HTTP/1.1 200 OK
```

### 5.6 部分更新文章

```http
PATCH https://jsonplaceholder.typicode.com/posts/1
Content-Type: application/json; charset=UTF-8
Accept: application/json

{
  "title": "foo"
}
```

预期结果：

```text
HTTP/1.1 200 OK
```

### 5.7 删除文章

```http
DELETE https://jsonplaceholder.typicode.com/posts/1
Accept: application/json
```

预期结果：

```text
HTTP/1.1 200 OK
```

说明：删除接口返回模拟结果，不代表远端数据被真实删除。

## 6. 响应说明

### 6.1 状态码

| 状态码 | 场景 | 说明 |
| --- | --- | --- |
| `200` | 查询、更新、删除 | 请求成功 |
| `201` | 创建资源 | 模拟创建成功 |
| `404` | 查询不存在资源 | 资源不存在 |

### 6.2 资源字段说明

文章 `Post`：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `userId` | integer | 文章所属用户 ID |
| `id` | integer | 文章 ID |
| `title` | string | 文章标题 |
| `body` | string | 文章正文 |

评论 `Comment`：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `postId` | integer | 评论所属文章 ID |
| `id` | integer | 评论 ID |
| `name` | string | 评论标题或名称 |
| `email` | string | 评论人邮箱 |
| `body` | string | 评论内容 |

待办 `Todo`：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `userId` | integer | 待办所属用户 ID |
| `id` | integer | 待办 ID |
| `title` | string | 待办标题 |
| `completed` | boolean | 是否完成 |

### 6.3 客户端断言建议

- 列表接口断言响应为 JSON 数组，并校验数组元素关键字段。
- 详情接口断言 `id` 与路径参数一致。
- 查询参数接口断言返回数据中的关联字段一致，例如 `comments?postId=1` 返回项的 `postId` 应为 `1`。
- 创建接口断言状态码为 `201`，且响应体包含提交字段和模拟生成的 `id`。
- 更新接口断言状态码为 `200`，且响应体体现更新后的字段。
- 删除接口断言状态码为 `200`，不要断言远端数据被真实删除。

## 7. 异常与边界场景

| 场景 | 示例 | 预期处理 |
| --- | --- | --- |
| 查询不存在资源 | `GET /posts/999999` | 断言 `404` 或空结果，具体以接口实际返回为准 |
| 查询参数无匹配数据 | `GET /comments?postId=999999` | 断言返回空数组 |
| 写操作后再次查询 | `POST /posts` 后 `GET /posts/101` | 不应假设创建数据被真实持久化 |
| 删除后再次查询 | `DELETE /posts/1` 后 `GET /posts/1` | 不应假设原始数据被真实删除 |
| 网络超时或 DNS 失败 | Base URL 不可达 | 应作为传输层异常处理，不应归类为接口业务错误 |

## 8. 接口测试用例

### 8.1 查询文章列表

```json
{
  "name": "JSONPlaceholder-查询文章列表",
  "method": "GET",
  "url": "https://jsonplaceholder.typicode.com/posts",
  "expectedStatus": 200,
  "assertions": [
    {
      "type": "json_array"
    },
    {
      "type": "json_field_exists",
      "path": "$[0].id"
    },
    {
      "type": "json_field_exists",
      "path": "$[0].title"
    }
  ]
}
```

### 8.2 查询文章详情

```json
{
  "name": "JSONPlaceholder-查询文章详情",
  "method": "GET",
  "url": "https://jsonplaceholder.typicode.com/posts/1",
  "expectedStatus": 200,
  "assertions": [
    {
      "type": "json_field_equals",
      "path": "$.id",
      "expected": 1
    },
    {
      "type": "json_field_exists",
      "path": "$.body"
    }
  ]
}
```

### 8.3 按文章查询评论

```json
{
  "name": "JSONPlaceholder-按postId查询评论",
  "method": "GET",
  "url": "https://jsonplaceholder.typicode.com/comments?postId=1",
  "expectedStatus": 200,
  "assertions": [
    {
      "type": "json_array"
    },
    {
      "type": "json_each_field_equals",
      "path": "$[*].postId",
      "expected": 1
    }
  ]
}
```

### 8.4 创建文章

```json
{
  "name": "JSONPlaceholder-创建文章",
  "method": "POST",
  "url": "https://jsonplaceholder.typicode.com/posts",
  "headers": {
    "Content-Type": "application/json; charset=UTF-8"
  },
  "body": {
    "title": "foo",
    "body": "bar",
    "userId": 1
  },
  "expectedStatus": 201,
  "assertions": [
    {
      "type": "json_field_equals",
      "path": "$.title",
      "expected": "foo"
    },
    {
      "type": "json_field_exists",
      "path": "$.id"
    }
  ]
}
```

### 8.5 部分更新文章

```json
{
  "name": "JSONPlaceholder-部分更新文章",
  "method": "PATCH",
  "url": "https://jsonplaceholder.typicode.com/posts/1",
  "headers": {
    "Content-Type": "application/json; charset=UTF-8"
  },
  "body": {
    "title": "foo"
  },
  "expectedStatus": 200,
  "assertions": [
    {
      "type": "json_field_equals",
      "path": "$.title",
      "expected": "foo"
    }
  ]
}
```

### 8.6 删除文章

```json
{
  "name": "JSONPlaceholder-删除文章",
  "method": "DELETE",
  "url": "https://jsonplaceholder.typicode.com/posts/1",
  "expectedStatus": 200,
  "assertions": [
    {
      "type": "status_code",
      "expected": 200
    }
  ]
}
```

## 9. 安全、合规与运维说明

| 项目 | 说明 |
| --- | --- |
| 鉴权 | 无鉴权，不需要 API Key、Token 或 Cookie |
| 数据安全 | 请求体和 URL 不应包含真实用户数据、密钥、账号、手机号、身份证号等敏感信息 |
| 数据性质 | Fake Data，不代表真实业务数据 |
| 写操作持久化 | 不真实持久化，返回值仅用于模拟接口行为 |
| 日志 | 可记录 Method、URL、状态码、耗时、请求体样例和断言结果；避免记录敏感数据 |
| 限流与可用性 | 官方公开服务可能存在网络波动或限流，本文档不承诺 SLA |
| 降级方案 | 企业内稳定自动化建议使用自建 JSON Server 或 Mock 服务 |

## 10. 导入和维护建议

| 场景 | 建议 |
| --- | --- |
| API 平台导入 | 使用第 3 节 OpenAPI 3.0 YAML 内容 |
| 人工阅读 | 使用资源总览、接口说明、请求示例和测试用例 |
| 自动化测试 | 以状态码、JSON 类型、关键字段和关联字段作为主要断言 |
| Mock 迁移 | 如需企业内稳定执行，建议复制资源结构到自建 Mock 服务 |
| 文档维护 | 当 JSONPlaceholder 官网资源、路由或示例发生变化时同步更新 |
| 版本管理 | 文档结构或契约变化时同步更新文档版本和 OpenAPI `info.version` |

## 11. 变更记录

| 版本 | 日期 | 说明 |
| --- | --- | --- |
| 1.0.0 | 2026-06-09 | 按 JSONPlaceholder 官网内容整理为企业标准 REST API 接口文档 |
