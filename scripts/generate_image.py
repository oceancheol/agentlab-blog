#!/usr/bin/env python3
"""
Gemini 이미지 생성 스크립트
사용법: python3 generate_image.py "이미지 프롬프트" /path/to/output.jpg
"""

import sys
import os
import json

def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        with open(os.path.expanduser("~/.openclaw/openclaw.json")) as f:
            config = json.load(f)
        return config.get("env", {}).get("GEMINI_API_KEY")
    except Exception:
        return None

def generate_image(prompt: str, output_path: str) -> bool:
    api_key = get_api_key()
    if not api_key:
        print("오류: GEMINI_API_KEY를 찾을 수 없습니다.")
        return False

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    print(f"이미지 생성 중: {prompt}")
    try:
        response = client.models.generate_images(
            model="imagen-4.0-fast-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                safety_filter_level="BLOCK_LOW_AND_ABOVE",
            ),
        )

        if response.generated_images:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            image_bytes = response.generated_images[0].image.image_bytes
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"저장 완료: {output_path}")
            return True
        else:
            print("이미지 생성 실패: 결과 없음")
            return False

    except Exception as e:
        print(f"오류: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python3 generate_image.py '프롬프트' 출력경로")
        print("예시: python3 generate_image.py 'AI robots collaborating' content/post/my-post/cover.jpg")
        sys.exit(1)

    success = generate_image(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
