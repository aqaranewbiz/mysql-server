[![smithery badge](https://smithery.ai/badge/@aqaranewbiz/mysql-server)](https://smithery.ai/server/@aqaranewbiz/mysql-server)
# MySQL MCP Server

이 저장소는 MySQL 데이터베이스에 연결할 수 있는 Smithery AI MCP 서버를 포함하고 있습니다.

## 기능

- MySQL 데이터베이스 연결
- SQL 쿼리 실행
- 날짜/시간 타입 지원
- HTTP 및 WebSocket 모두 지원

## 설치 방법

1. **저장소 복제**:
   ```bash
   git clone <repository-url>
   cd MCP_Server
   ```

2. **의존성 설치**:
   ```bash
   pip install -r requirements.txt
   ```

## 환경 변수

다음과 같은 환경 변수를 설정하여 MySQL 연결을 구성할 수 있습니다:

- `MYSQL_HOST`: MySQL 서버 호스트 (기본값: "localhost")
- `MYSQL_PORT`: MySQL 서버 포트 (기본값: 3306)
- `MYSQL_USER`: MySQL 사용자 이름
- `MYSQL_PASSWORD`: MySQL 비밀번호
- `MYSQL_DATABASE`: 기본 MySQL 데이터베이스 (선택 사항)

## 서버 실행

### HTTP 서버 (mcp_mysql_server.py) - 기본값
```bash
python mcp_mysql_server.py
```

### WebSocket 서버 (mcp_server.py)
```bash
python mcp_server.py
```

## MCP 도구

### mysql_query

SQL 쿼리를 실행합니다.

**매개변수**:
- `query`: 실행할 SQL 쿼리 (필수)
- `db_config`: 데이터베이스 연결 설정 (선택 사항)
  - `host`: 데이터베이스 호스트
  - `port`: 데이터베이스 포트
  - `user`: 데이터베이스 사용자
  - `password`: 데이터베이스 비밀번호
  - `database`: 데이터베이스 이름

## 호환성 정보

`mcp_server.py`와 `mcp_mysql_server.py` 파일은 다음과 같은 차이점이 있습니다:

1. `mcp_server.py`: WebSocket을 사용하는 JSON-RPC 2.0 서버
2. `mcp_mysql_server.py`: HTTP를 사용하는 REST API 서버

두 서버는 기능적으로 호환되며, 동일한 MySQL 쿼리 기능을 제공합니다. 배포 환경 및 요구사항에 따라 적절한 서버를 선택할 수 있습니다.

## Smithery AI에 배포

이 서버는 Smithery AI에 배포할 수 있도록 설계되었습니다. `smithery.yaml` 파일은 Smithery AI에 필요한 설정을 정의합니다.

배포하려면 Smithery AI 대시보드에서 이 저장소를 등록하고 배포하면 됩니다.

## License
This project is licensed under the MIT License. 

## smithery.yaml
```yaml
version: '1'
configSchema:
  type: "object"
  properties:
    mysql_host:
      type: "string"
      description: "MySQL server host"
      default: "localhost"
    mysql_port:
      type: "integer"
      description: "MySQL server port"
      default: 3306
    mysql_user:
      type: "string"
      description: "MySQL username"
    mysql_password:
      type: "string"
      description: "MySQL password"
      format: "password"
    mysql_database:
      type: "string"
      description: "Default MySQL database"
    server_type:
      type: "string"
      description: "Server type to run (websocket or http)"
      enum: ["websocket", "http"]
      default: "http"
  required: ["mysql_user", "mysql_password"]
startCommand:
  type: 'stdio'
  commandFunction: |
    function getCommand(config) {
      const serverScript = config.server_type === "http" ? "mcp_mysql_server.py" : "mcp_server.py";
      return {
        command: 'python',
        args: [serverScript],
        env: {
          "MYSQL_HOST": config.mysql_host || "localhost",
          "MYSQL_PORT": String(config.mysql_port || 3306),
          "MYSQL_USER": config.mysql_user,
          "MYSQL_PASSWORD": config.mysql_password,
          "MYSQL_DATABASE": config.mysql_database || ""
        }
      };
    } 