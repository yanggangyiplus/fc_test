#!/usr/bin/env python3
"""
Gemini API를 이용한 음성 녹음 및 텍스트 변환 (STT)
"""

import os
import wave
import pyaudio
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
import time

# 환경 변수 로드
load_dotenv()

class GeminiSTT:
    def __init__(self, api_key=None):
        """
        Gemini STT 초기화

        Args:
            api_key: Gemini API 키. 제공되지 않으면 환경 변수에서 로드
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

        # Gemini API 설정
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # 오디오 설정
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.audio = pyaudio.PyAudio()

    def record_audio(self, duration=5, output_file="recorded_audio.wav"):
        """
        오디오 녹음

        Args:
            duration: 녹음 시간 (초)
            output_file: 저장할 파일명

        Returns:
            녹음된 파일 경로
        """
        print(f"\n🎤 녹음을 시작합니다... ({duration}초)")

        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        frames = []

        for i in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)

            # 진행 상황 표시
            elapsed = (i + 1) * self.chunk / self.rate
            print(f"\r녹음 중... {elapsed:.1f}/{duration}초", end='')

        print("\n✅ 녹음 완료!")

        stream.stop_stream()
        stream.close()

        # WAV 파일로 저장
        wf = wave.open(output_file, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        return output_file

    def transcribe_audio(self, audio_file):
        """
        오디오 파일을 텍스트로 변환

        Args:
            audio_file: 오디오 파일 경로

        Returns:
            변환된 텍스트
        """
        print("\n🤖 Gemini API로 텍스트 변환 중...")

        # 오디오 파일을 Gemini API에 업로드
        audio_data = genai.upload_file(path=audio_file)

        # 음성을 텍스트로 변환 요청
        prompt = "이 오디오 파일의 음성을 정확하게 텍스트로 변환해주세요. 한국어와 영어를 모두 지원합니다. 오직 변환된 텍스트만 출력하세요."

        response = self.model.generate_content([prompt, audio_data])

        # 임시 파일 삭제
        genai.delete_file(audio_data.name)

        return response.text

    def record_and_transcribe(self, duration=5, save_audio=False):
        """
        녹음 후 바로 텍스트 변환

        Args:
            duration: 녹음 시간 (초)
            save_audio: 오디오 파일 저장 여부

        Returns:
            변환된 텍스트
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        audio_file = f"recording_{timestamp}.wav"

        # 녹음
        self.record_audio(duration, audio_file)

        # 텍스트 변환
        text = self.transcribe_audio(audio_file)

        # 오디오 파일 삭제 (저장 옵션이 False인 경우)
        if not save_audio:
            os.remove(audio_file)
            print(f"🗑️  임시 파일 삭제됨: {audio_file}")
        else:
            print(f"💾 오디오 파일 저장됨: {audio_file}")

        return text

    def __del__(self):
        """소멸자: PyAudio 종료"""
        self.audio.terminate()


def main():
    """메인 함수"""
    print("=" * 60)
    print("🎯 Gemini API를 이용한 음성-텍스트 변환 (STT)")
    print("=" * 60)

    try:
        # GeminiSTT 인스턴스 생성
        stt = GeminiSTT()

        while True:
            print("\n📋 메뉴:")
            print("1. 녹음 후 텍스트 변환 (5초)")
            print("2. 녹음 후 텍스트 변환 (10초)")
            print("3. 녹음 후 텍스트 변환 (사용자 지정 시간)")
            print("4. 종료")

            choice = input("\n선택하세요 (1-4): ").strip()

            if choice == '1':
                text = stt.record_and_transcribe(duration=5)
                print(f"\n📝 변환된 텍스트:\n{text}\n")

            elif choice == '2':
                text = stt.record_and_transcribe(duration=10)
                print(f"\n📝 변환된 텍스트:\n{text}\n")

            elif choice == '3':
                try:
                    duration = int(input("녹음 시간을 입력하세요 (초): "))
                    if duration <= 0 or duration > 60:
                        print("❌ 1-60초 사이의 값을 입력하세요.")
                        continue

                    save_audio = input("오디오 파일을 저장하시겠습니까? (y/n): ").lower() == 'y'
                    text = stt.record_and_transcribe(duration=duration, save_audio=save_audio)
                    print(f"\n📝 변환된 텍스트:\n{text}\n")

                except ValueError:
                    print("❌ 올바른 숫자를 입력하세요.")

            elif choice == '4':
                print("\n👋 프로그램을 종료합니다.")
                break

            else:
                print("❌ 올바른 번호를 선택하세요.")

    except ValueError as e:
        print(f"\n❌ 오류: {e}")
        print("\n💡 해결 방법:")
        print("1. .env 파일을 생성하고 GEMINI_API_KEY를 설정하세요.")
        print("2. API 키는 https://makersuite.google.com/app/apikey 에서 발급받을 수 있습니다.")

    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")


if __name__ == "__main__":
    main()
