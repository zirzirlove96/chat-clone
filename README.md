# chat-clone

## Runner.run_streamed()와 stream_events() 이벤트

`Runner.run_streamed()`로 Agent를 스트리밍 실행할 때, `stream_events()`로 받을 수 있는 이벤트들입니다.

### 기본 사용법 (dummy-agent.ipynb 기준)

```python
from agents import Agent, Runner, function_tool

result = Runner.run_streamed(weather_agent, "서울 날씨 어때?")

async for event in result.stream_events():
    if event.type == "raw_response_event":
        continue  # 토큰 단위 스트리밍 (LLM 응답)
    elif event.type == "agent_updated_stream_event":
        print("Agent updated to:", event.new_agent.name)
```

### 이벤트 타입

| event.type | 설명 |
|------------|------|
| `raw_response_event` | LLM에서 직접 전달되는 토큰 단위 스트리밍 이벤트. `event.data.type`으로 구체 유형 구분 (아래 참고) |
| `run_item_stream_event` | "메시지 완성", "도구 호출", "도구 결과" 등 **단위 작업이 끝났을 때**. `event.name`으로 어떤 일인지 구분 |
| `agent_updated_stream_event` | 현재 실행 중인 Agent가 변경됐을 때 (handoff 시점 등) |

### raw_response_event와 event.data (response.output_text.delta 등)

`raw_response_event` 안의 `event.data`로 **LLM이 지금 뭘 생성하고 있는지** 구체적으로 알 수 있습니다.

#### event.data.type 종류

| event.data.type | 의미 | event.data.delta |
|-----------------|------|------------------|
| `response.output_text.delta` | LLM이 **사용자에게 보낼 텍스트**를 한 토큰씩 생성할 때 | 새로 생성된 텍스트 조각 (문자열) |
| `response.function_call_arguments.delta` | LLM이 **도구 호출 인자**(JSON)를 한 토큰씩 생성할 때 | 새로 생성된 인자 조각 (문자열) |
| `response.completed` | 해당 응답이 **완료**됐을 때 | — |

### run_item_stream_event 쉽게 이해하기

**run_item_stream_event** = Agent가 실행되는 동안 **"뭔가 하나가 완료됐다"**고 알려주는 이벤트입니다.

`raw_response_event`가 토큰 한 글자씩 흘러오는 **저수준** 이벤트라면,  
`run_item_stream_event`는 **"메시지 하나 완성됐어", "도구 호출했어", "도구 결과 왔어"** 같은 **단위 작업이 끝났을 때** 오는 이벤트입니다.

#### event.name — 어떤 일이 끝났는지

| event.name | 의미 (쉽게) |
|------------|-------------|
| `message_output_created` | Agent가 사용자에게 보낼 **메시지가 완성**됐을 때 |
| `tool_called` | Agent가 **도구를 호출**했을 때 (예: get_weather) |
| `tool_output` | 도구 실행이 끝나고 **결과가 돌아왔을** 때 |
| `handoff_requested` | 다른 Agent에게 **일을 넘기려고** 할 때 |
| `handoff_occured` | 다른 Agent로 **실제로 넘어갔을** 때 |
| `reasoning_item_created` | Agent의 **사고 과정**이 하나 생성됐을 때 |
| `mcp_approval_requested` | MCP 도구 사용 **승인을 요청**할 때 |
| `mcp_approval_response` | MCP 승인 **응답**이 왔을 때 |
| `mcp_list_tools` | MCP **도구 목록**을 조회했을 때 |

### Weather Agent 예시에서의 이벤트 흐름

날씨 질문("서울 날씨 어때?")을 실행할 때:

1. `agent_updated_stream_event` — Weather Agent가 실행 시작
2. `raw_response_event` — LLM이 `get_weather` 도구 호출 결정
3. `run_item_stream_event` (name: `tool_called`) — get_weather 호출
4. `run_item_stream_event` (name: `tool_output`) — 도구 결과 수신
5. `raw_response_event` — LLM이 사용자에게 보낼 최종 응답 생성
6. `run_item_stream_event` (name: `message_output_created`) — 최종 메시지 완성

---

## Session (SQLiteSession) — 대화 기록 유지

Agent가 **이전 대화를 기억**하도록 하려면 `SQLiteSession`으로 세션을 만들고 `Runner.run()`에 넘깁니다. 대화 내역은 SQLite DB 파일에 저장됩니다.

### 기본 사용

| 항목 | 설명 |
|------|------|
| **생성** | `SQLiteSession(session_id, db_path)` — `session_id`로 사용자/대화를 구분, `db_path`에 DB 파일 경로 |
| **실행 시 연결** | `Runner.run(agent, "사용자 입력", session=session)` — 매 턴마다 같은 `session`을 넘기면 이전 대화 맥락 유지 |

예: `session_id`를 `"user"`로 두면, 해당 유저의 대화만 그 세션에 쌓입니다.

### Session 메서드 (내장 API)

| 메서드 | 설명 |
|--------|------|
| `await session.get_items(limit=None)` | 저장된 대화 기록 조회. `limit`이 있으면 최근 N개만 반환. **DB 내용을 코드로 볼 때 사용** |
| `await session.add_items(items)` | 대화 항목을 수동으로 추가 (예: 초기 컨텍스트 넣기) |
| `await session.pop_item()` | 가장 최근 항목 하나 제거 후 반환 |
| `await session.clear_session()` | 해당 세션의 대화 기록 전부 삭제 |

### 사용 시 주의

- `add_items`, `get_items`, `clear_session`, `pop_item`은 모두 **async**라서 `await`가 필요합니다.
- `session.add_items(...)`는 코루틴을 반환하므로, `session = await session.add_items(...)`처럼 대입하면 안 됩니다. 그냥 `await session.add_items(...)`만 호출하면 됩니다.

### DB 파일을 보고 싶을 때

- `ai-memory.db` 같은 파일은 **바이너리**라 텍스트 에디터로 열면 깨져 보입니다.
- **방법 1**: 같은 `session_id`와 `db_path`로 `SQLiteSession`을 만들고 `await session.get_items()`로 저장된 대화 목록을 조회합니다.
- **방법 2**: 프로젝트에 있는 `view_db.py`를 실행하면 테이블/컬럼/데이터를 읽기 쉬운 텍스트로 출력합니다.

## handoffs - agent가 다른 agent로 작업을 넘김

- main agent에 'handoffs' 속성을 사용하여 agent를 참조하도록 한다.
- hanoffs 가 안될 수도 있으니 main agent에 instructions에 참조된 agent에 대한 설명과 넘기도록 강하게 바꿔준다.
- 'handoff_description' 는 sub agent에 대한 설명이다.


## streamlit

- python UI
- rerun은 전체 파일이 재실행된다 (memory를 잃게 됨)
