# Gemini STT (Speech-to-Text)

Gemini API를 이용한 음성 녹음 및 텍스트 변환 프로그램입니다.

## 기능

- 🎤 실시간 오디오 녹음
- 🤖 Gemini API를 이용한 음성-텍스트 변환
- 🌏 한국어 및 영어 지원
- 💾 녹음 파일 저장 옵션

## 설치 방법

### 1. Python 패키지 설치

```bash
pip install -r requirements.txt
```

모든 플랫폼(Windows, macOS, Linux)에서 추가 시스템 의존성 없이 설치됩니다.

### 2. API 키 설정

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 Gemini API 키를 발급받습니다.

2. `.env` 파일을 생성하고 API 키를 설정합니다:

```bash
cp .env.example .env
```

3. `.env` 파일을 편집하여 실제 API 키를 입력합니다:

```
GEMINI_API_KEY=your_actual_api_key_here
```

## 사용 방법

### 기본 사용

```bash
python gemini_stt.py
```

프로그램을 실행하면 인터랙티브 메뉴가 나타납니다:
- 5초 녹음 후 텍스트 변환
- 10초 녹음 후 텍스트 변환
- 사용자 지정 시간으로 녹음
- 오디오 파일 저장 옵션

### 코드에서 사용

```python
from gemini_stt import GeminiSTT

# STT 인스턴스 생성
stt = GeminiSTT()

# 5초 녹음 후 텍스트 변환
text = stt.record_and_transcribe(duration=5)
print(text)

# 10초 녹음 후 오디오 파일 저장
text = stt.record_and_transcribe(duration=10, save_audio=True)
print(text)
```

## 프로젝트 구조

```
.
├── gemini_stt.py       # 메인 STT 프로그램
├── requirements.txt    # Python 의존성
├── .env.example        # 환경 변수 예시
├── .env               # 환경 변수 (생성 필요)
└── README.md          # 프로젝트 문서
```

## 요구 사항

- Python 3.8 이상
- Gemini API 키
- 마이크 (오디오 입력 장치)

## 주의 사항

- 녹음 시간은 1-60초 사이로 설정하는 것을 권장합니다.
- API 사용량에 따라 요금이 발생할 수 있습니다.
- 안정적인 인터넷 연결이 필요합니다.

## 라이선스

MIT License