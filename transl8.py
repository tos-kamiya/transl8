import argparse
import sys
from typing import Optional

import ollama

DEFAULT_LLM_MODEL = "mistral-small:latest"
VERSION = "0.5.0"

TRANSLATION_TEMPLATE = "Translate the text below into '%s'. Output only the translation without any preamble or additional information. Keep ANSI escape sequences in text.\n---\n%s"
TRANSLATION_WITH_ANSI_TEMPLATE = "Translate the text below into '%s'. Output only the translation without any preamble or additional information.\n---\n%s"


def translate(
    language_code: str,
    text: str,
    model: str,
    num_ctx: Optional[int] = None,
    keep_ansi: bool = False,
) -> str:
    template = TRANSLATION_WITH_ANSI_TEMPLATE if keep_ansi else TRANSLATION_TEMPLATE
    context = template % (language_code, text)
    options = {"num_ctx": num_ctx, "num_predict": -2} if num_ctx is not None else {}

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": context}],
            options=options,
        )
        t = response["message"]["content"]
    except ollama.ResponseError as e:
        raise

    return t.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Translate text to a specified language."
    )
    parser.add_argument(
        "language_code",
        help="The target language code (e.g., 'en' for English, 'ja' for Japanese).",
    )
    parser.add_argument(
        "text",
        help="Path of the text file to be translated. Use '-' to read from stdin.",
    )
    parser.add_argument(
        "-p",
        "--plain",
        action="store_true",
        help="Treat the input as plain text instead of a file path.",
    )
    parser.add_argument(
        "-a",
        "--alternative",
        action="store_true",
        help="Provide multiple translation variations.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_LLM_MODEL,
        help=f"Specify the LLM model to use (default: {DEFAULT_LLM_MODEL}).",
    )
    parser.add_argument("--num-ctx", type=int, help="Specify the context length.")
    parser.add_argument(
        "--version",
        action="version",
        version=VERSION,
        help="Show the version number and exit.",
    )

    args = parser.parse_args()

    try:
        ollama.show(args.model)
    except ollama.ResponseError as e:
        print(f"Error: The model '{args.model}' is not installed yet.", file=sys.stderr)
        print(f"Please ensure that the model is correctly downloaded using the following command:\n  ollama pull {args.model}", flush=True, file=sys.stderr)
        exit(1)

    if args.num_ctx is not None:
        if args.num_ctx <= 0:
            print("Error: --num-ctx value should be > 0.", flush=True, file=sys.stderr)
            exit(1)

    if args.plain:
        text_content = args.text
    else:
        if args.text == "-":
            text_content = sys.stdin.read()
            # Check if standard input is TTY
            if sys.stdin.isatty():
                print("\nInfo: Starting translation...", flush=True, file=sys.stderr)
        else:
            with open(args.text, "r", encoding="utf-8") as file:
                text_content = file.read()
    text_content = text_content.strip()

    ansi_included = text_content.find("\033[") >= 0
    if args.alternative:
        translations = []
        for i in range(3):
            translation = translate(
                args.language_code,
                text_content,
                model=args.model,
                num_ctx=args.num_ctx,
                keep_ansi=ansi_included,
            )

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
        translation = translate(
            args.language_code,
            text_content,
            model=args.model,
            num_ctx=args.num_ctx,
            keep_ansi=ansi_included,
        )
        print(translation)


if __name__ == "__main__":
    main()
