# transl8, a simple CLI translator

`transl8` is a simple CLI translator that uses LLM running on local PC.

## Install

To install `transl8`, you need the following tools:

* **pipx**: https://pipx.pypa.io/
* **ollama**: https://ollama.com/

After installing them, you can install `transl8` by pipx:

```sh
pipx install git+https://github.com/tos-kamiya/transl8
```

A command `transl8` is installed on the system.

## Usage

```sh
$ transl8 ja -p "Hello."
こんにちは。
```

```sh
$ transl8 ja README.md
# transl8、単純なCLI翻訳ツール
...
```

## Changelog

* v0.5.0
  - Change the default model to Mistral Small 3 (max context size 32k)
  - Add option --num-ctx to specify context size
* v0.4.0
  - Show message after Ctrl+D when reading from standard input
  - Change the default model to Phi-4
* v0.3.0: Keep ANSI escape sequences in text
* v0.2.0: Fix miscellaneous bugs
