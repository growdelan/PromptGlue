# Aktualny stan projektu

## Co działa
- Aplikacja GUI uruchamia się przez `uv run main.py`.
- Załączanie plików i katalogów, wykluczanie/usuwanie oraz kopiowanie finalnego outputu.
- Budowanie outputu działa przez warstwę `core` i stan `Session` jako źródło prawdy.
- Final preview pokazuje dokładnie ten sam output, który trafia do kopiowania i eksportu.
- Eksport wyniku do `.md` i `.txt`.
- Profile outputu: XML-like, Markdown blocks, Plain text.
- Filtrowanie listy plików po nazwie, rozszerzeniu i statusie.
- Masowe akcje na zaznaczonych elementach: include/exclude/remove.
- Raport importu katalogu zawierający przyczyny pominięć i błędy odczytu.
- Minimalny hook CLI oparty o warstwę `core`.
- CI (GitHub Actions) uruchamia testy i check kompilacji.
- Dolny obszar akcji GUI jest rozdzielony na osobne wiersze (input/output/bulk), co poprawia czytelność przy długich toolbarach.
- Wykluczanie/usuwanie plików z importu katalogu aktualizuje również sekcję `<directories>` (drzewo zawiera tylko aktywne pliki).

## Co jest skończone
- Wygenerowano `spec.md` i `ROADMAP.md` na podstawie `prd/000-initial-prd.md`.
- Milestone 0.5 oznaczony jako `done`.
- Milestone 1 oznaczony jako `done`.
- Milestone 2 oznaczony jako `done`.
- Milestone 3 oznaczony jako `done`.
- Milestone 4 oznaczony jako `done`.

## Co jest w trakcie
- Brak aktywnego milestone'u.

## Co jest następne
- Roadmapa gotowa na kolejny PRD lub nowy milestone funkcjonalny.

## Blokery i ryzyka
- Brak aktywnych blockerów.

## Ostatnie aktualizacje
- 2026-04-01: zakończono M1, M2, M3 i M4; testy `unittest` przechodzą lokalnie.
- 2026-04-02: poprawiono ergonomię layoutu GUI przez rozdzielenie przycisków na kilka pasków akcji.
- 2026-04-02: naprawiono niespójność `<directories>` przy exclude/remove oraz dodano test regresyjny.
