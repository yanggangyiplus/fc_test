#!/usr/bin/env python3
"""
Gemini API를 이용한 음성 녹음 및 텍스트 변환 (STT) - Google GenAI SDK 버전
"""

import os
import wave
import time
import pyaudio
from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiSTT:
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

        # Google GenAI SDK Client
        self.client = genai.Client(api_key=self.api_key)  # :contentReference[oaicite:5]{index=5}

        # 모델 선택: 가능한 모델 목록에서 우선순위로 고름
        self.model = model_name or self._pick_model()

        # 오디오 설정
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.audio = pyaudio.PyAudio()

    def _pick_model(self) -> str:
        """
        계정/키에 따라 사용 가능 모델이 다를 수 있으니, 실제 list() 결과 기반으로 선택.
        """
        preferred = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.5-pro",
            "gemini-2.0-pro",
        ]

        available = []
        try:
            for m in self.client.models.list():
                # m.name 형식: "models/gemini-2.0-flash" 같은 형태일 수 있음
                name = getattr(m, "name", "") or ""
                # "models/" 접두 제거한 값도 같이 저장
                short = name.replace("models/", "")
                if short:
                    available.append(short)
        except Exception:
            # list가 막히면, 일단 가장 보편적인 모델로 시도
            return "gemini-2.0-flash"

        for p in preferred:
            if p in available:
                return p

        # 여기까지 왔으면, 계정에서 지원 모델이 달라서 수동 지정 필요
        raise ValueError(
            "사용 가능한 Gemini 모델을 찾지 못했습니다.\n"
            f"가능 모델(일부): {sorted(set(available))[:30]}\n"
            "→ 위 목록 중 하나를 model_name으로 지정하세요."
        )

    def record_audio(self, duration=5, output_file="recorded_audio.wav"):
        print(f"\n🎤 녹음을 시작합니다... ({duration}초)")

        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )

        frames = []
        for i in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk, exception_on_overflow=False)
            frames.append(data)

            elapsed = (i + 1) * self.chunk / self.rate
            print(f"\r녹음 중... {elapsed:.1f}/{duration}초", end="")

        print("\n✅ 녹음 완료!")
        stream.stop_stream()
        stream.close()

        wf = wave.open(output_file, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b"".join(frames))
        wf.close()

        return output_file

    def transcribe_audio(self, audio_file: str) -> str:
        print(f"\n🤖 Gemini API로 텍스트 변환 중... (model={self.model})")

        # 1) 파일 업로드 (Files API)
        uploaded = self.client.files.upload(file=audio_file)  # :contentReference[oaicite:6]{index=6}

        try:
            prompt = (
                "이 오디오 파일의 음성을 가능한 한 정확하게 텍스트로 변환해줘. "
                "한국어/영어 모두 지원. "
                "추가 설명 없이 변환된 텍스트만 출력해."
            )

            # 2) generate_content에 [프롬프트, 업로드 파일] 전달
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, uploaded],
            )  # :contentReference[oaicite:7]{index=7}

            return response.text or ""

        finally:
            # 3) 서버에 올린 파일 삭제
            self.client.files.delete(name=uploaded.name)  # :contentReference[oaicite:8]{index=8}

    def record_and_transcribe(self, duration=5, save_audio=False):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        audio_file = f"recording_{timestamp}.wav"

        self.record_audio(duration, audio_file)
        text = self.transcribe_audio(audio_file)

        if not save_audio:
            os.remove(audio_file)
            print(f"🗑️  임시 파일 삭제됨: {audio_file}")
        else:
            print(f"💾 오디오 파일 저장됨: {audio_file}")

        return text

    def __del__(self):
        try:
            self.audio.terminate()
        except Exception:
            pass


def main():
    print("=" * 60)
    print("🎯 Gemini API를 이용한 음성-텍스트 변환 (STT) - google-genai")
    print("=" * 60)

    try:
        stt = GeminiSTT()

        while True:
            print("\n📋 메뉴:")
            print("1. 녹음 후 텍스트 변환 (5초)")
            print("2. 녹음 후 텍스트 변환 (10초)")
            print("3. 녹음 후 텍스트 변환 (사용자 지정 시간)")
            print("4. 종료")

            choice = input("\n선택하세요 (1-4): ").strip()

            if choice == "1":
                text = stt.record_and_transcribe(duration=5)
                print(f"\n📝 변환된 텍스트:\n{text}\n")

            elif choice == "2":
                text = stt.record_and_transcribe(duration=10)
                print(f"\n📝 변환된 텍스트:\n{text}\n")

            elif choice == "3":
                try:
                    duration = int(input("녹음 시간을 입력하세요 (초): "))
                    if duration <= 0 or duration > 60:
                        print("❌ 1-60초 사이의 값을 입력하세요.")
                        continue

                    save_audio = input("오디오 파일을 저장하시겠습니까? (y/n): ").lower() == "y"
                    text = stt.record_and_transcribe(duration=duration, save_audio=save_audio)
                    print(f"\n📝 변환된 텍스트:\n{text}\n")

                except ValueError:
                    print("❌ 올바른 숫자를 입력하세요.")

            elif choice == "4":
                print("\n👋 프로그램을 종료합니다.")
                break

            else:
                print("❌ 올바른 번호를 선택하세요.")

    except ValueError as e:
        print(f"\n❌ 오류: {e}")
        print("\n💡 해결 방법:")
        print("1) .env 파일에 GEMINI_API_KEY를 설정하세요.")
        print("2) 사용 가능한 모델이 계정마다 다르면, 모델명을 출력된 목록에서 골라 model_name으로 지정하세요.")

    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")


if __name__ == "__main__":
    main()
