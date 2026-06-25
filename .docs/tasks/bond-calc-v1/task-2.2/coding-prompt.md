# Coding Prompt — Task 2.2: 计算 API 路由

> 生成日期：2025-06-25 | 关联文档：[task.md](./task.md) | [test-cases.md](./test-cases.md)

---

## 1. 任务目标

实现计算触发与结果查询的 REST API：`POST /api/v1/calculations`（触发计算）和 `GET /api/v1/calculations/{id}`（获取结果）。计算结果持久化到 MongoDB `calculations` 集合，支持同一基金代码 5 分钟内缓存复用。

---

## 2. 技术上下文

- **语言/框架**: Python 3.11+ / FastAPI / Beanie ODM / MongoDB
- **现有代码依赖**:
  - `services/calculation_service.py` — `calculate(fund_code)` 返回 `CalculationResponse`（已在 Task 2.1 实现）
  - `models/schemas.py` — `CalculationRequest`、`CalculationResponse`、`ApiResponse`（已定义）
  - `models/calculation.py` — `Calculation` Beanie 文档模型
  - `core/cache.py` — `get_cache("calc:")` 内存缓存（已实现）
  - `core/exceptions.py` — `AppException`、`FatalError`、`ErrorCode`（已实现）
  - `core/config.py` — `settings.CACHE_TTL_CALC` = 300 秒
  - `api/routes/funds.py` — 已有路由（参照其 ApiResponse 包装 + AppException 处理模式）

### 涉及文件

| 操作 | 文件 | 说明 |
|------|------|------|
| **新建** | `server/api/routes/calculations.py` | 计算 API 路由（POST + GET） |
| **修改** | `server/api/main.py` | 注册 calculations 路由 |
| **修改** | `server/models/calculation.py` | 添加 `status`、`error_message`、`fund_name`、`disclaimer` 字段 |

---

## 3. 实现要求

### 3.1 文件 `server/models/calculation.py`（修改）

在现有 `Calculation(Document)` 类中**新增**以下字段：

```python
# 在现有字段基础上新增：

fund_name: str = ""
"""基金名称。"""

status: str = "processing"
"""计算状态：processing | completed | failed。"""

error_message: str | None = None
"""失败时的错误描述。"""

disclaimer: str = ""
"""免责声明文本。"""
```

**修改原因**: Task 2.2 要求持久化完整计算结果（含基金名称、免责声明），并支持状态追踪（processing/completed/failed）。

> ⚠️ 注意：`created_at` 字段已存在但无默认值。在路由层创建文档时需显式赋值 `datetime.utcnow()`。

---

### 3.2 文件 `server/api/routes/calculations.py`（新建）

参照 `server/api/routes/funds.py` 的代码风格，创建路由文件。

#### 模块级

- **Router 定义**:
  ```python
  router = APIRouter(prefix="/calculations", tags=["收益计算"])
  ```
- **导入清单**:
  ```python
  import re
  from datetime import datetime, timedelta

  from fastapi import APIRouter, HTTPException
  from beanie import PydanticObjectId
  from loguru import logger
  from bson import ObjectId
  from bson.errors import InvalidId

  from models.schemas import ApiResponse, CalculationRequest, CalculationResponse
  from models.calculation import Calculation
  from services.calculation_service import calculate as do_calculate
  from core.exceptions import AppException, FatalError, ErrorCode
  from core.config import settings
  ```

---

#### 3.2.1 POST `/` — 触发计算

- **装饰器**:
  ```python
  @router.post(
      "/",
      response_model=ApiResponse[dict],
      summary="触发基金收益计算",
      description=(
          "输入 6 位基金代码，触发 8 项收益指标异步计算。"
          "同一基金代码 + 5 分钟内有缓存结果时直接返回已有 calculation_id。"
      ),
      responses={
          200: {"description": "计算完成"},
          503: {"description": "所有数据源不可用"},
      },
  )
  async def trigger_calculation(request: CalculationRequest):
  ```

- **关键逻辑**（按顺序）:

  1. **格式校验** — 使用正则 `r"^\d{6}$"` 校验 `fund_code`：
     - 不匹配 → `raise AppException(message="基金代码格式错误，请输入 6 位数字", code=ErrorCode.INVALID_CODE_FORMAT, status_code=200)`
     - 注意：status_code 用 200（业务错误由 `ApiResponse.code` 表达），而非 422
  
  2. **MongoDB 缓存检查** — 查询同一基金代码 + 5 分钟内的已完成计算：
     ```python
     five_min_ago = datetime.utcnow() - timedelta(seconds=settings.CACHE_TTL_CALC)
     existing = await Calculation.find_one(
         Calculation.fund_code == fund_code,
         Calculation.created_at >= five_min_ago,
         Calculation.status == "completed",
     )
     if existing:
         logger.debug("命中 MongoDB 缓存 code={}", fund_code)
         return ApiResponse(
             code=0, message="success",
             data={"calculation_id": str(existing.id), "status": "completed"}
         )
     ```

  3. **创建 processing 文档** — 先写入 MongoDB 标记"处理中"：
     ```python
     calc_doc = Calculation(
         fund_code=fund_code,
         fund_name="",
         status="processing",
         data_date="",
         is_trading_day=False,
         disclaimer="",
         created_at=datetime.utcnow(),
     )
     await calc_doc.insert()
     ```

  4. **执行计算** — 调用 `do_calculate(fund_code)`（即 `calculation_service.calculate`），用 try/except 包裹：
     - **成功** → 将 `CalculationResponse` 各字段赋值到 `calc_doc`，设置 `status="completed"`
     - **FatalError** → 设置 `status="failed"`、`error_message=str(e)`，save 后 re-raise（让统一异常处理或 ApiResponse 包装返回错误）
     - **其他 Exception** → 设置 `status="failed"`、`error_message=str(e)`，save 后返回
       ```python
       return ApiResponse(
           code=ErrorCode.CALCULATION_FAILED,
           message=f"计算失败：{str(e)}",
           data={"calculation_id": str(calc_doc.id), "status": "failed"}
       )
       ```

  5. **字段映射**（CalculationResponse → Calculation 文档）：
     ```python
     calc_doc.fund_name = result.fund_name
     calc_doc.nav = result.nav
     calc_doc.daily_change_pct = result.daily_change_pct
     calc_doc.seven_day_annual_yield = result.seven_day_annual_yield
     calc_doc.wanfen_income = result.wanfen_income
     calc_doc.one_month_return = result.one_month_return
     calc_doc.three_month_max_drawdown = result.three_month_max_drawdown
     calc_doc.ten_year_treasury = result.ten_year_treasury
     calc_doc.credit_spread_aa_plus = result.credit_spread_aa_plus
     calc_doc.data_date = result.data_date
     calc_doc.is_trading_day = result.is_trading_day
     calc_doc.disclaimer = result.disclaimer
     calc_doc.status = "completed"
     await calc_doc.save()
     ```

  6. **返回成功响应**:
     ```python
     return ApiResponse(
         code=0, message="success",
         data={"calculation_id": str(calc_doc.id), "status": "completed"}
     )
     ```

---

#### 3.2.2 GET `/{calculation_id}` — 获取计算结果

- **装饰器**:
  ```python
  @router.get(
      "/{calculation_id}",
      response_model=ApiResponse[dict],
      summary="获取计算结果",
      description="根据 calculation_id 查询收益计算详情。",
      responses={
          200: {"description": "计算结果"},
          404: {"description": "计算结果不存在"},
      },
  )
  async def get_calculation(calculation_id: str):
  ```

- **关键逻辑**（按顺序）:

  1. **ID 格式校验** — 使用 `bson.ObjectId` 验证：
     ```python
     try:
         obj_id = ObjectId(calculation_id)
     except InvalidId:
         raise HTTPException(status_code=404, detail="计算结果不存在")
     ```

  2. **MongoDB 查询**:
     ```python
     calc_doc = await Calculation.get(obj_id)
     if calc_doc is None:
         raise HTTPException(status_code=404, detail="计算结果不存在")
     ```

  3. **状态分支**:
     - `status == "processing"` → 返回处理中提示：
       ```python
       return ApiResponse(
           code=0, message="success",
           data={"status": "processing", "message": "计算中，请稍后刷新"}
       )
       ```
     - `status == "failed"` → 返回失败信息：
       ```python
       return ApiResponse(
           code=0, message="success",
           data={"status": "failed", "error_message": calc_doc.error_message or "未知错误"}
       )
       ```
     - `status == "completed"` → 组装完整响应（**必须包含所有字段，None 值也保留**）：
       ```python
       return ApiResponse(
           code=0, message="success",
           data={
               "fund_code": calc_doc.fund_code,
               "fund_name": calc_doc.fund_name,
               "nav": calc_doc.nav,
               "daily_change_pct": calc_doc.daily_change_pct,
               "seven_day_annual_yield": calc_doc.seven_day_annual_yield,
               "wanfen_income": calc_doc.wanfen_income,
               "one_month_return": calc_doc.one_month_return,
               "three_month_max_drawdown": calc_doc.three_month_max_drawdown,
               "ten_year_treasury": calc_doc.ten_year_treasury,
               "credit_spread_aa_plus": calc_doc.credit_spread_aa_plus,
               "data_date": calc_doc.data_date,
               "is_trading_day": calc_doc.is_trading_day,
               "disclaimer": calc_doc.disclaimer,
               "status": "completed",
           }
       )
       ```

---

### 3.3 文件 `server/api/main.py`（修改）

在现有 `api/main.py` 的「路由注册」区域添加 calculations 路由：

```python
# 在 from api.routes import funds 之后添加：
from api.routes import calculations

# 在 app.include_router(funds.router, prefix="/api/v1") 之后添加：
app.include_router(calculations.router, prefix="/api/v1")
```

---

## 4. 代码规范要求

1. **参照 `funds.py` 风格**：路由函数用 `async def`，错误处理用 `try/except AppException` 模式（POST 路由）
2. **loguru 日志**：关键步骤打日志（格式校验失败 WARNING、缓存命中 DEBUG、计算开始 INFO、计算失败 ERROR）
3. **Pydantic 字段保留**：GET completed 响应中 `None` 值字段必须出现在 JSON 中（`exclude_none=False` 或显式列出所有键），不可被 `model_dump(exclude_none=True)` 吞掉
4. **中文错误消息**：面向终端用户的消息用中文
5. **类型注解**：所有函数标注返回类型
6. **不引入新依赖**：仅使用项目已有依赖（fastapi、beanie、bson、loguru、datetime、re）

---

## 5. 测试要求

代码必须能通过以下测试用例（详见 [test-cases.md](./test-cases.md)）：

| 用例 | 要求 |
|------|------|
| TC-001 | POST 有效 fund_code → 200 + calculation_id + status |
| TC-002 | GET completed → 200 + 完整 8 项指标 + 元数据 |
| TC-003 | GET processing → 200 + status "processing" + message |
| TC-004 | GET failed → 200 + status "failed" + error_message |
| TC-005 | 同一 fund_code 5 分钟内缓存命中，返回相同 calculation_id |
| TC-006 | 计算结果持久化到 MongoDB `calculations` 集合 |
| TC-007 | Swagger `/docs` 可看到两个接口定义 |
| TC-008 | fund_code 边界值校验（6 位通过、非 6 位拒绝） |
| TC-009 | 数值字段 None 在响应中保留键名，值为 `null` |
| TC-010 | fund_code 格式非法 → 业务错误码 40003 |
| TC-011 | 缺少 fund_code → 422（FastAPI 自动校验） |
| TC-012 | GET 不存在 ID → 404 |
| TC-013 | GET 无效格式 ID → 404（不返回 500） |
| TC-014 | 路由注册到 main.py + `/api/v1` 前缀 |
| TC-015 | 缓存过期后重新计算（不同 calculation_id） |

---

## 6. 注意事项

1. **calculation_id 使用 MongoDB `_id`**：通过 `str(calc_doc.id)` 获取 24 字符十六进制字符串，不要在代码中自行生成 UUID
2. **内存缓存 vs MongoDB 缓存**：`calculation_service.calculate()` 内部有自己的内存缓存（`calc:*` 前缀，TTL 5min），路由层的 MongoDB 缓存查询是额外一层——两者互补：内存缓存加速重复计算，MongoDB 缓存提供 calculation_id 复用
3. **FatalError（全部数据源失败）**：在路由层 catch `FatalError` 后，需将 MongoDB 文档标记为 `failed` 再返回错误——避免文档永远停在 `processing`
4. **`created_at` 赋值**：创建 Calculation 文档时需手动赋值 `datetime.utcnow()`，Beanie Document 不会自动设置默认值
5. **ApiResponse[dict] vs ApiResponse[CalculationResponse]**：POST 返回的 `data` 是 `{"calculation_id": str, "status": str}` 不是完整 CalculationResponse，所以 `response_model` 用 `ApiResponse[dict]`。同理 GET 根据不同 status 返回不同结构的 data，也用 `dict`
6. **不要修改 `services/calculation_service.py`**：它已在 Task 2.1 完成，路由层只调用不修改
7. **不要新建 schema**：`CalculationRequest`、`CalculationResponse`、`ApiResponse` 已在 `models/schemas.py` 中定义，直接使用
