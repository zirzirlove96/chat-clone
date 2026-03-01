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
