import argparse
import sys

import ollama

LLM_MODEL = "qwen2.5:latest"
VERSION = "0.1.1"

def translate(language_code: str, text: str) -> str:
    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user", 
                    "content": f"Translate the text below into '{language_code}'. Output only the translation without any preamble or additional information.\n---\n{text}",
                },
            ],
        )
        t = response['message']['content']
        return t.strip()
    except ollama.ResponseError as e:
        raise


def main():
    for m in ollama.list()["models"]:
        model_name = m["name"]
        if model_name == LLM_MODEL:
            break
    else:
        print(f"Info: Model '{LLM_MODEL}' not found, try to install it...", file=sys.stderr)
        ollama.pull(LLM_MODEL)

    parser = argparse.ArgumentParser(description="Translate text to a specified language.")
    parser.add_argument("language_code", help="The target language code (e.g., 'en' for English, 'ja' for Japanese).")
    parser.add_argument("text", help="The text or path to the text file to be translated. Use '-' to read from stdin.")
    parser.add_argument("-p", "--plain", action="store_true", help="Treat the input as plain text instead of a file path.")
    parser.add_argument("-a", "--alternative", action="store_true", help="Provide multiple translation variations.")
    parser.add_argument("--version", action="version", version=VERSION, help="Show the version number and exit.")

    args = parser.parse_args()

    if args.plain:
        text_content = args.text
    else:
        if args.text == "-":
            text_content = sys.stdin.read()
        else:
            with open(args.text, 'r', encoding='utf-8') as file:
                text_content = file.read()
    text_content = text_content.strip()

    if args.alternative:
        translations = []
        for i in range(3):
            translation = translate(args.language_code, text_content)

            translation = translation.strip()
            while translation.startswith("---\n"):
                translation = translation[4:].strip()
            while translation.endswith("\n---"):
                translation = translation[:-4].strip()

            if translation in translations:
                continue
            translations.append(translation)

            if text_content.find("\n") >= 0:
                print(f"{translation}\n---")
            else:
                print(f"* {translation}")
    else:
        translation = translate(args.language_code, text_content)
        print(translation)
