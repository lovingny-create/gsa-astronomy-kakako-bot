# 무료 배포 추천

광곽현웅봇은 카카오 챗봇 스킬 서버이므로 외부에서 접근 가능한 HTTPS 주소가 필요합니다.

무료로 시작하려면 아래 순서를 추천합니다.

## 1순위: Render Free

장점:

- 무료로 HTTPS URL을 받을 수 있습니다.
- 학교 PC를 계속 켜둘 필요가 없습니다.
- GitHub에 프로젝트를 올리면 자동 배포가 쉽습니다.

주의:

- 무료 인스턴스는 잠들 수 있어 첫 응답이 느릴 수 있습니다.
- 실제 관측회에서 항상 즉시 응답해야 하면 나중에 유료 전환이 필요할 수 있습니다.

### Render 설정

이 프로젝트에는 `render.yaml`이 포함되어 있습니다.

Render에서 새 Web Service를 만들 때 다음 값을 사용합니다.

```text
Build Command: pip install -r requirements.txt
Start Command: python server.py
Environment Variable: HWBOT_CONFIG=data/config.local.json
```

이 저장소의 `render.yaml`은 Render 배포용 공개 설정인 `data/config.render.json`을 사용합니다.

배포 후 Render가 제공하는 주소 뒤에 `/skill`을 붙여 카카오 챗봇 스킬 URL로 등록합니다.

```text
https://배포주소.onrender.com/skill
```

상태 확인 주소:

```text
https://배포주소.onrender.com/health
```

## 2순위: Cloudflare Tunnel

장점:

- 무료로 학교 PC의 로컬 서버를 HTTPS로 공개할 수 있습니다.
- 관측 PC 또는 학교 내부 시스템과 나중에 연동하기 좋습니다.

주의:

- 학교 PC가 켜져 있어야 합니다.
- 학교망 방화벽/보안 정책 확인이 필요합니다.
- 안정적인 주소를 쓰려면 도메인 설정이 필요합니다.

로컬 서버 실행:

```powershell
$env:HWBOT_CONFIG="data/config.local.json"
python .\server.py
```

그 뒤 Cloudflare Tunnel로 `localhost:8000`을 공개합니다.

카카오 스킬 URL:

```text
https://터널주소/skill
```

## 3순위: ngrok 무료

장점:

- 가장 빠르게 테스트할 수 있습니다.

주의:

- 무료 주소가 바뀔 수 있습니다.
- 장기 운영에는 적합하지 않습니다.

## 결론

처음 카카오 연동 테스트는 Render Free가 가장 편합니다.

관측실 PC와 장비 제어까지 가까워져야 한다면 Cloudflare Tunnel이 더 좋습니다.

## Render Free 기록 저장 주의

Render 공식 문서 기준 Free Web Service는 15분 동안 요청이 없으면 잠들 수 있고, 로컬 파일 변경은 재시작/재배포/스핀다운 때 사라집니다.

따라서 현재 FITS 색인 CSV 저장은 카카오 연동 테스트용으로 사용하세요. 실제 장기 관측 기록은 Google Sheets, 학교 NAS API, 또는 별도 데이터베이스 연동으로 옮기는 것을 권장합니다.

참고:

- [Render Free 서비스 문서](https://render.com/docs/free)
- [Render Persistent Disks 문서](https://render.com/docs/disks)
