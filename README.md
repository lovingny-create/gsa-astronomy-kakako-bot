# Astronomical Observation Kakao Chatbot MVP

학교 천문 관측 중 학생들이 겪는 문제를 카카오톡 채널 챗봇으로 안내하는 최소 실행 버전입니다.

이 MVP는 외부 라이브러리 없이 Python 표준 라이브러리만 사용합니다.

## 주요 기능

- 카카오 챗봇 스킬 서버 응답 형식 지원
- 관측 가능 여부 안내
- 망원경/카메라 문제 해결 안내
- 계절별 관측 대상 추천
- 관측 기록 CSV 저장
- 안전/비상 상황 안내

## 실행

```powershell
python .\server.py
```

현재 PC에서 `python` 명령이 없다면 Codex 번들 파이썬으로 실행할 수 있습니다.

```powershell
& "C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\server.py
```

기본 주소:

```text
http://localhost:8000
```

상태 확인:

```powershell
python .\tools\simulate_skill_request.py "초점이 안 맞아요"
```

테스트:

```powershell
python -m unittest discover -s tests
```

## 설정

1. `data/config.example.json`을 복사해 `data/config.local.json`을 만듭니다.
2. 학교 이름, 관측 장소, 위도/경도, 장비, 비상 안내 문구를 수정합니다.
3. 실행할 때 환경변수 `HWBOT_CONFIG`로 설정 파일을 지정합니다.

```powershell
$env:HWBOT_CONFIG="data/config.local.json"
python .\server.py
```

광주과학고등학교용 설정은 `data/config.local.json`에 작성되어 있습니다.
Render Free 배포용 설정은 `data/config.render.json`에 작성되어 있습니다.

## 카카오 연결 개요

1. 카카오톡 채널을 개설합니다.
2. 카카오 챗봇 관리자센터에서 챗봇을 만듭니다.
3. 스킬 서버 URL을 등록합니다.
4. 공개 HTTPS 주소의 `/skill` 엔드포인트를 연결합니다.
5. 기본 블록에서 빠른 답변을 아래 문구로 연결합니다.

```text
오늘 관측 가능?
장비가 이상해요
뭘 보면 좋을까요?
관측 기록하기
안전/비상 안내
```

자세한 준비 정보는 `docs/requested-info.md`를 채워 주세요.

무료 배포는 `docs/free-deploy.md`를 참고하세요.
