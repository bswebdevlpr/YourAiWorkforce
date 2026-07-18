package main

// 슬라이스 1: SSE 릴레이의 뼈대.
// 아직 파이썬은 안 부른다. 가짜 토큰 생성기로 흘려보내면서
// (1) net/http 서버 (2) SSE 프레이밍 (3) Flusher (4) context 취소
// 네 가지를 손에 익히는 게 목적이다.

import (
	"bytes"
	"context"
	"embed"
	"encoding/json"
	"fmt"
	"io"
	"io/fs"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
)

// 아래 지시어는 빌드 시점에 static/ 폴더를 바이너리 안에 통째로 구워넣는다.
// 배포할 때 실행파일 하나만 옮기면 되고, 실행 시 파일 경로에 의존하지 않는다.
// 주석처럼 생겼지만 컴파일러가 읽는 지시어라 "//"와 "go:embed" 사이에 공백이 있으면 안 된다.
//
//go:embed static
var staticFS embed.FS

// ChatRequest — 브라우저가 보내는 바디. 파이썬 PostBody와 필드를 맞춰둔다.
// Go의 struct 태그(`json:"..."`)가 JSON 키 ↔ 필드 매핑을 정한다.
type ChatRequest struct {
	Message  string `json:"message"`
	ThreadID string `json:"thread_id"`
	Type     string `json:"type"`
}

// upstreamEvent — 슬라이스 3: 채널에 실을 내부 표현.
// 지금까지는 <-chan string으로 토큰 텍스트만 흘렸는데, interrupt는
// {"result":"...","options":[...]}처럼 모양이 다르다. 그래서
// "이벤트 종류(Kind) + 원본 JSON(Data)"으로 감싸서 흘려보낸다.
//
// Data는 json.RawMessage — "파싱하지 말고 바이트 그대로 들고 있어라"는 타입.
// 게이트웨이는 이 페이로드의 내용을 몰라도 되고(파이썬이 뭘 넣든), 그대로 브라우저에 전달만 하면 된다.
type upstreamEvent struct {
	Kind string
	Data json.RawMessage
}

// upstreamBase — 파이썬 FastAPI 앱의 베이스 URL.
// 환경변수로 덮어쓸 수 있게 해두면 docker-compose에서 호스트명만 바꿔 끼울 수 있다.
var upstreamBase = envOr("UPSTREAM_BASE", "http://localhost:8000")

func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", healthHandler)
	mux.HandleFunc("POST /chat", chatHandler)

	// static/index.html을 "/"에서 서빙한다.
	// fs.Sub로 embed.FS의 "static" 하위를 루트로 잘라내면
	// /index.html 이 아니라 / 로 접근할 수 있다.
	sub, err := fs.Sub(staticFS, "static")
	if err != nil {
		log.Fatal(err)
	}
	mux.Handle("GET /", http.FileServerFS(sub))

	// DEBUG_ROUTES가 설정됐을 때만 여는 진단 라우트.
	// recover 미들웨어가 실제로 panic을 잡는지 눈으로 확인하는 용도.
	if os.Getenv("DEBUG_ROUTES") != "" {
		mux.HandleFunc("GET /debug/panic", func(w http.ResponseWriter, r *http.Request) {
			panic("boom (intentional)")
		})
	}

	// 미들웨어 배선. chain의 첫 인자가 가장 바깥이다:
	// requestID(ID 부여) → logging(기록) → recover(사고 방지) → mux(진짜 라우팅)
	// requestID를 맨 바깥에 둬서 logging/recover가 그 ID를 context에서 꺼내 쓸 수 있다.
	handler := chain(mux, requestIDMiddleware, loggingMiddleware, recoverMiddleware)

	addr := ":8080"
	log.Printf("gateway listening on %s (upstream: %s)", addr, upstreamBase)
	if err := http.ListenAndServe(addr, handler); err != nil {
		log.Fatal(err)
	}
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("ok\n"))
}

// chatHandler — 이 함수가 이번 슬라이스의 핵심.
func chatHandler(w http.ResponseWriter, r *http.Request) {
	// (A) 요청 바디(JSON) 디코드. r.Body는 io.Reader — 스트림이다.
	var req ChatRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad json", http.StatusBadRequest)
		return
	}
	// requestID 미들웨어가 context에 심어둔 ID를 여기서 꺼내 쓴다 — 값이 끝까지 흐른다는 증거.
	reqID, _ := r.Context().Value(requestIDKey).(string)
	log.Printf("[%s] chat: thread=%q type=%q msg=%q", reqID, req.ThreadID, req.Type, req.Message)

	// (B) SSE 헤더. 이걸 안 붙이면 브라우저가 일반 응답으로 취급한다.
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	// (C) Flusher 확보.
	// 기본 ResponseWriter는 응답을 버퍼에 모았다가 한 번에 보낸다.
	// SSE는 이벤트마다 즉시 밀어야 하므로, Flusher 인터페이스로 타입 단언(type assertion)한다.
	// "이 w가 http.Flusher도 구현하나?" → 대부분의 http 서버 구현은 yes.
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "streaming unsupported", http.StatusInternalServerError)
		return
	}

	// (D) context. r.Context()는 이 요청에 묶인 컨텍스트다.
	// 브라우저가 탭을 닫거나 연결이 끊기면 ctx.Done() 채널이 닫힌다.
	// 슬라이스 2에서 이 ctx를 파이썬 호출로 그대로 전달하면,
	// "클라가 끊기면 업스트림 파이썬 호출도 취소"가 공짜로 된다.
	ctx := r.Context()

	// (E) 업스트림(파이썬 FastAPI)에 요청.
	// realUpstream이 원시 토큰 스트림을 읽어 구조화된 이벤트 채널로 바꿔준다.
	events := realUpstream(ctx, upstreamBase, &req)

	// (F) 릴레이 루프. select로 두 채널을 동시에 기다린다:
	//   - events에서 새 이벤트가 오면 → 종류에 따라 SSE로 써서 flush
	//   - ctx.Done()이 먼저 닫히면 → 클라가 끊긴 것 → 조용히 종료
	for {
		select {
		case ev, more := <-events:
			if !more {
				// 채널이 닫힘 = 업스트림이 할 말 다 함 = 턴 정상 종료.
				writeSSE(w, "done", map[string]string{"reason": "end"})
				flusher.Flush()
				return
			}
			writeSSE(w, ev.Kind, ev.Data)
			flusher.Flush()

			// interrupt는 "이 턴은 여기서 멈추고 사람 응답을 기다린다"는 뜻.
			// 파이썬 그래프도 여기서 멈춰 있으므로, 뒤이어 "done"을 보낼 필요가 없다.
			// (다음 사람 응답은 새 POST /chat 요청으로 온다 — type=reply/complete/reject)
			if ev.Kind == "interrupt" {
				return
			}
		case <-ctx.Done():
			log.Printf("client disconnected: %v", ctx.Err())
			return
		}
	}
}

// threadState — 파이썬 GET /state/{thread_id}의 응답.
type threadState struct {
	Exists      bool            `json:"exists"`
	Interrupted bool            `json:"interrupted"`
	Interrupt   json.RawMessage `json:"interrupt"`
}

// realUpstream — 파이썬(:8000)을 상대한다.
//
// 파이썬 POST /는 SSE 프레이밍을 하지 않는다. media_type만 text/event-stream이고
// 실제로는 토큰 문자열이 날것으로 흘러나온다(src/main.py의 generate_chat_responses).
// 게다가 interrupt로 멈춰도 스트림이 그냥 끝나버려서, "왜 끝났는지"가 스트림에 안 실린다.
//
// 그래서 게이트웨이가 프로토콜을 조립한다:
//  1. 원시 토큰 조각을 읽어 event:token 으로 감싼다
//  2. 스트림이 끝나면(EOF) GET /state/{thread_id}로 상태를 조회한다
//  3. interrupted면 event:interrupt, 아니면 event:done 을 스스로 판정해 발행
func realUpstream(ctx context.Context, baseURL string, req *ChatRequest) <-chan upstreamEvent {
	out := make(chan upstreamEvent)
	go func() {
		defer close(out)

		// (1) 요청 바디를 채운다. 파이썬 PostBody와 필드가 같으니 그대로 마샬링.
		body, err := json.Marshal(req)
		if err != nil {
			log.Printf("realUpstream: marshal request failed: %v", err)
			return
		}

		// (2) HTTP 요청 만들기. ctx를 꽂아서 취소 전파가 가능하게.
		httpReq, err := http.NewRequestWithContext(ctx, "POST", baseURL+"/", bytes.NewReader(body))
		if err != nil {
			log.Printf("realUpstream: NewRequest failed: %v", err)
			return
		}
		httpReq.Header.Set("Content-Type", "application/json")

		resp, err := http.DefaultClient.Do(httpReq)
		if err != nil {
			log.Printf("realUpstream: Do failed: %v", err)
			return
		}
		// (3) defer Close() — 함수가 끝나면 반드시 resp.Body를 닫는다.
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			msg, _ := io.ReadAll(resp.Body)
			emit(ctx, out, "error", mustJSON(map[string]string{
				"message": fmt.Sprintf("upstream %d: %s", resp.StatusCode, strings.TrimSpace(string(msg))),
			}))
			return
		}

		// (4) io.Reader를 직접 읽는다. Scanner(줄 단위)를 쓰면 안 되는 이유:
		// 파이썬이 뱉는 토큰 조각은 줄바꿈으로 구분되지 않는다("안녕" "하세" "요").
		// 줄 단위로 기다리면 개행이 올 때까지 토큰이 버퍼에 갇혀 스트리밍이 죽는다.
		// Read는 "지금 도착해 있는 만큼"을 buf에 채우고 n을 돌려준다.
		buf := make([]byte, 4096)
		for {
			n, err := resp.Body.Read(buf)
			if n > 0 {
				// buf는 다음 Read에서 덮어써지므로, 채널로 보낼 값은 복사해서 보낸다.
				chunk := string(buf[:n])
				if !emit(ctx, out, "token", mustJSON(map[string]string{"text": chunk})) {
					return // 클라가 끊김
				}
			}
			if err == io.EOF {
				break // 파이썬이 할 말을 다 했다 — 이제 왜 끝났는지 물어볼 차례
			}
			if err != nil {
				log.Printf("realUpstream: read error: %v", err)
				return
			}
		}

		// (5) 스트림 종료 사유 판정. 여기가 이 게이트웨이의 존재 이유다.
		st, err := fetchState(ctx, baseURL, req.ThreadID)
		if err != nil {
			log.Printf("realUpstream: fetchState failed: %v", err)
			emit(ctx, out, "error", mustJSON(map[string]string{"message": err.Error()}))
			return
		}
		if st.Interrupted && len(st.Interrupt) > 0 {
			emit(ctx, out, "interrupt", st.Interrupt)
			return
		}
		// interrupted가 아니면 채널을 그냥 닫는다 → chatHandler가 done을 발행한다.
	}()
	return out
}

// fetchState — 파이썬에 "이 스레드 지금 interrupt로 멈춰 있냐"고 묻는다.
func fetchState(ctx context.Context, baseURL, threadID string) (*threadState, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", baseURL+"/state/"+url.PathEscape(threadID), nil)
	if err != nil {
		return nil, err
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("state endpoint returned %d", resp.StatusCode)
	}
	var st threadState
	if err := json.NewDecoder(resp.Body).Decode(&st); err != nil {
		return nil, err
	}
	return &st, nil
}

// emit — 채널로 이벤트를 보내되, 클라가 끊겼으면 false를 돌려준다.
// select 패턴이 여러 곳에서 반복되길래 헬퍼로 뽑았다.
func emit(ctx context.Context, out chan<- upstreamEvent, kind string, data json.RawMessage) bool {
	select {
	case out <- upstreamEvent{Kind: kind, Data: data}:
		return true
	case <-ctx.Done():
		return false
	}
}

func mustJSON(v any) json.RawMessage {
	b, err := json.Marshal(v)
	if err != nil {
		// map[string]string 마샬링은 실패할 수 없다.
		panic(err)
	}
	return b
}

// writeSSE — 하나의 SSE 이벤트를 규격대로 써준다:
//
//	event: <name>\n
//	data: <json>\n\n   (빈 줄이 이벤트 경계)
func writeSSE(w http.ResponseWriter, event string, payload any) {
	data, _ := json.Marshal(payload)
	fmt.Fprintf(w, "event: %s\ndata: %s\n\n", event, data)
}
