# 在 Windows 上从源码原生运行 ibis-server（不使用 Docker）

本副本基于上游 [Canner/wren-engine](https://github.com/Canner/wren-engine)（Apache-2.0）main 分支，
记录 2026-11 在 Windows 11 上纯源码启动 ibis-server（FastAPI 语义引擎，端口 8000）的可行路径与修改点。

## 环境要求

| 工具 | 版本 | 说明 |
|---|---|---|
| Python | **3.11.x（强制）** | pyproject 钉死 `>=3.11,<3.12`，3.12/3.14 无法安装 |
| Poetry | ≥1.8.3 | 装在项目 venv 内即可，不依赖系统 Poetry |
| Git | 任意新版 | 克隆源码 |
| Rust | 不需要 | Windows x86_64 有 wren-core-py 预编译 wheel（cp311-abi3） |
| Java | 不需要 | 仅 v2 MDL 兜底需要；v3 接口走 Rust 核心，进程内运行 |

## 本副本相对上游的修改（已提交）

1. `pyproject.toml`
   - `wren-engine = ">=0.6.0"`（原 0.1.0）
   - 新增 `wren-core-py = ">=0.8.2"`：上游锁文件钉的 0.1.0 在 PyPI **没有 Windows wheel**，
     会回退 maturin 源码编译并因 crates.io 访问失败而报错；0.8.2 提供 win_amd64 预编译 wheel。
2. `poetry.lock`：按上述约束重新解析生成。
3. `poetry.toml`：`virtualenvs.create = false`，复用项目内 `.venv`。
4. `.gitignore`：新增 `.venv/` 与 `*.log`（上游只忽略 `venv/`，不匹配 `.venv`）。
5. 新增 `e2e_check.py`：local_file 连接器查 TPC-H parquet 的端到端验证脚本。
6. 新增 `swagger-demo-payload.json`：可直接粘贴到 Swagger UI 的请求体示例。

## 安装步骤

```bash
git clone <本仓库地址> wren-engine
cd wren-engine/ibis-server

# 1. 建独立 venv（必须 3.11）
py -3.11 -m venv .venv
source .venv/Scripts/activate          # Git Bash；cmd 用 .venv\Scripts\activate
python -m pip install -U pip wheel setuptools

# 2. venv 内装新版 Poetry
python -m pip install -U "poetry>=1.8.3"
poetry config virtualenvs.create false --local

# 3. 装依赖（如 pip 镜像缺包，对个别包显式指定官方源）
poetry install
pip install --index-url https://pypi.org/simple "wren-core-py==0.8.2" "wren-engine==0.6.0"
pip install --index-url https://pypi.org/simple "psycopg[binary]"

# 4. 冒烟测试
python -c "from app.main import app; print(app.title)"
```

## 启动（必须设 UTF-8）

```bash
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
python -m fastapi run --port 8000
```

> 不设 `PYTHONUTF8=1` 时，Windows GBK 控制台无法渲染启动横幅的 emoji，
> 会抛 `UnicodeEncodeError: 'gbk' codec can't encode character` 导致进程退出。

启动后：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc
- 健康检查：http://localhost:8000/health → `{"status":"ok"}`

## 端到端验证

```bash
python e2e_check.py
```

预期返回 TPC-H 订单按状态分组的三行结果（F/O/P）。该脚本通过
`POST /v3/connector/local_file/query` 直接查询 `example/duckdb-tpch-example/data/orders.parquet`。

## 已知说明

- 启动日志出现 `WREN_ENGINE_ENDPOINT is not set` 属良性警告：仅表示 Java 遗留引擎未启动，
  v3 接口（Rust 核心）功能完整。
- 本仓库不包含 `.venv/`、日志文件及任何密钥；`.env*` 被上游 .gitignore 全局排除。
