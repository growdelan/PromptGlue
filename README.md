# PromptGlue

## Opis
PromptGlue to aplikacja umożliwiająca szybkie połącznie z promptu + załączonych plików w jeden blok tekstowy, dla modeli które aktualnie nie pozwalają dołączać plików. 

Aktualnie aplikacja wspiera:
- final preview outputu,
- eksport do `.md` i `.txt`,
- profile formatu outputu: XML-like, Markdown blocks, Plain text.

## Instalacja UV
[UV](https://github.com/astral-sh/uv) - Ultra szybki manager paczek i projektów dla Python napisany w Rust
```bash
brew install uv
```

## Uruchomienie

W katalogu z repozytorium:
```bash
uv run main.py
```

## Testy

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```

