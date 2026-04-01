# Aktualny stan projektu

## Co działa
- Aplikacja GUI uruchamia się przez `uv run main.py`.
- Załączanie plików i katalogów, wykluczanie/usuwanie oraz kopiowanie finalnego outputu.
- Budowanie outputu działa przez warstwę `core` i stan `Session` jako źródło prawdy.

## Co jest skończone
- Wygenerowano `spec.md` i `ROADMAP.md` na podstawie `prd/000-initial-prd.md`.
- Milestone 0.5 oznaczony jako `done`.
- Milestone 1 oznaczony jako `done`:
  - wydzielono warstwę `prompt_assistant/core`,
  - GUI zintegrowano z modelem sesji,
  - dodano testy regresyjne remove/exclude/build.

## Co jest w trakcie
- Milestone 2: preview finalnego outputu i eksport.

## Co jest następne
- Dodać final preview oparte o wspólny pipeline renderowania.
- Dodać eksport do `.md` i `.txt`.
- Dodać profile outputu: plain, markdown, xml-like.

## Blokery i ryzyka
- Brak doprecyzowanego domyślnego profilu outputu dla copy/export (TODO w roadmapie/spec).

## Ostatnie aktualizacje
- 2026-04-01: zakończono Milestone 1 i uruchomiono testy `unittest` (OK).
