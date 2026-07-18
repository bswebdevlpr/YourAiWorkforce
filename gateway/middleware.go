package main

// 슬라이스 6: 미들웨어 — 핸들러를 감싸는 데코레이터.
// 미들웨어 하나는 func(http.Handler) http.Handler 다: 핸들러를 받아 감싼 핸들러를 돌려준다.
// 이걸 양파처럼 겹치면 요청이 바깥→안으로 통과하며 각 층을 거친다.

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"sync/atomic"
	"time"
)

// ctxKey — context에 값을 넣을 때 쓰는 전용 키 타입.
// string을 키로 바로 쓰면 다른 패키지가 같은 문자열을 써서 충돌할 수 있다.
// 그래서 이 패키지만의 타입을 만들어 키로 쓴다(Go 관용).
type ctxKey string

const requestIDKey ctxKey = "requestID"

// middleware — 가독성을 위한 별칭. func(http.Handler) http.Handler 와 같다.
type middleware func(http.Handler) http.Handler

// chain — 여러 미들웨어를 하나로 합친다.
// chain(h, A, B, C) 는 A(B(C(h))) 가 되어, A가 가장 바깥(요청이 제일 먼저 통과)이다.
// 뒤에서부터 감싸 올라가면 이 순서가 나온다.
func chain(h http.Handler, mws ...middleware) http.Handler {
	for i := len(mws) - 1; i >= 0; i-- {
		h = mws[i](h)
	}
	return h
}

// reqCounter — 요청 ID 생성용 원자적 카운터.
// 여러 요청이 동시에 Add를 불러도 atomic이라 값이 꼬이지 않는다(뮤텍스 없이 안전).
var reqCounter atomic.Uint64

// requestIDMiddleware — 요청마다 ID를 붙인다.
// 들어온 X-Request-ID가 있으면 존중하고(분산 추적), 없으면 새로 만든다.
// context에 심어두면 뒤의 미들웨어와 핸들러가 어디서든 꺼내 쓸 수 있다.
func requestIDMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		id := r.Header.Get("X-Request-ID")
		if id == "" {
			id = fmt.Sprintf("req-%06d", reqCounter.Add(1))
		}
		w.Header().Set("X-Request-ID", id)
		ctx := context.WithValue(r.Context(), requestIDKey, id)
		next.ServeHTTP(w, r.WithContext(ctx)) // 감싼 핸들러를 부른다 = 다음 층으로
	})
}

// statusRecorder — 응답 상태 코드를 가로채 기록하는 ResponseWriter 래퍼.
// 로깅이 "이 요청 200이었나 500이었나"를 알려면 필요하다.
type statusRecorder struct {
	http.ResponseWriter // 원본을 임베드 — Write 등 나머지 메서드는 그대로 위임된다
	status              int
}

func (r *statusRecorder) WriteHeader(code int) {
	r.status = code
	r.ResponseWriter.WriteHeader(code)
}

// Flush — SSE가 살아있으려면 반드시 필요하다. ★중요★
// ResponseWriter를 struct로 감싸는 순간, 원본이 갖고 있던 http.Flusher 구현이 가려진다.
// 이 메서드로 원본에 다시 위임해주지 않으면, chatHandler의 w.(http.Flusher) 단언이 실패해
// 스트리밍이 통째로 죽는다. 래퍼를 씌울 땐 이 인터페이스 보존을 늘 확인해야 한다.
func (r *statusRecorder) Flush() {
	if f, ok := r.ResponseWriter.(http.Flusher); ok {
		f.Flush()
	}
}

// loggingMiddleware — 요청 1건의 method/path/status/소요시간/reqID를 한 줄로 남긴다.
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rec := &statusRecorder{ResponseWriter: w, status: 200} // 명시적 WriteHeader가 없으면 200
		next.ServeHTTP(rec, r)
		id, _ := r.Context().Value(requestIDKey).(string)
		log.Printf("[%s] %s %s → %d (%s)",
			id, r.Method, r.URL.Path, rec.status, time.Since(start).Round(time.Millisecond))
	})
}

// recoverMiddleware — 핸들러에서 panic이 나도 서버 전체가 죽지 않게 막는다.
// panic은 잡히지 않으면 goroutine을 타고 올라가 프로세스를 종료시킨다.
// recover()로 붙잡아 500으로 바꾸면, 한 요청의 사고가 다른 요청·서버까지 죽이지 않는다.
func recoverMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if v := recover(); v != nil {
				id, _ := r.Context().Value(requestIDKey).(string)
				log.Printf("[%s] panic recovered: %v", id, v)
				// 이미 스트리밍이 시작돼 헤더가 나간 뒤라면 WriteHeader는 무시된다(경고만).
				w.WriteHeader(http.StatusInternalServerError)
			}
		}()
		next.ServeHTTP(w, r)
	})
}
