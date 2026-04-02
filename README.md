# PromptGlue

## Opis
PromptGlue to lokalne narzędzie desktopowe do składania jednego wejścia dla LLM z promptu i wielu plików.

Aktualnie aplikacja wspiera:
- final preview outputu,
- eksport do `.md` i `.txt`,
- profile formatu outputu: XML-like, Markdown blocks, Plain text,
- filtrowanie listy plików (nazwa/rozszerzenie/status),
- masowe akcje include/exclude/remove,
- raport importu katalogu z przyczynami pominięć i błędami odczytu.

## Wymagania
- Python 3.13+
- `uv`

Instalacja `uv` (macOS):
```bash
brew install uv
```

## Uruchomienie GUI
W katalogu repozytorium:
```bash
uv run main.py
```

## Minimalny hook CLI
Przykład użycia:
```bash
uv run python -m prompt_assistant.cli --prompt "Przeanalizuj" --format xml README.md spec.md
```

Zapis do pliku:
```bash
uv run python -m prompt_assistant.cli --prompt "Podsumuj" --format markdown --output wynik.md README.md
```

## Testy lokalne
```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```

## Build check lokalny
```bash
uv run python -m compileall -q prompt_assistant main.py tests
```

## CI
Repo zawiera workflow GitHub Actions: `.github/workflows/ci.yml`.
CI uruchamia:
- testy `unittest`,
- check kompilacji (`compileall`).

## Struktura repo (skrót)
- `main.py` - entrypoint GUI
- `prompt_assistant/gui/` - warstwa UI i kontrolery
- `prompt_assistant/core/` - logika domenowa sesji/renderowania
- `prompt_assistant/cli.py` - minimalny punkt zaczepienia pod CLI
- `tests/` - testy jednostkowe
- `spec.md`, `ROADMAP.md`, `STATUS.md` - dokumentacja projektu
