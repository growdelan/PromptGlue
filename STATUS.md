# Aktualny stan projektu

## Co działa
- Aplikacja GUI uruchamia się przez `uv run main.py`.
- Załączanie plików i katalogów, wykluczanie/usuwanie oraz kopiowanie finalnego outputu.
- Budowanie outputu działa przez warstwę `core` i stan `Session` jako źródło prawdy.
- Final preview pokazuje dokładnie ten sam output, który trafia do kopiowania i eksportu.
- Eksport wyniku do `.md` i `.txt`.
- Profile outputu: XML-like, Markdown blocks, Plain text.

## Co jest skończone
- Wygenerowano `spec.md` i `ROADMAP.md` na podstawie `prd/000-initial-prd.md`.
- Milestone 0.5 oznaczony jako `done`.
- Milestone 1 oznaczony jako `done`:
  - wydzielono warstwę `prompt_assistant/core`,
  - GUI zintegrowano z modelem sesji,
  - dodano testy regresyjne remove/exclude/build.
- Milestone 2 oznaczony jako `done`:
  - dodano final preview oparte o wspólny pipeline renderowania,
  - dodano eksport do `.md` i `.txt`,
  - dodano profile formatu outputu,
  - rozszerzono testy o profile renderera i eksport.

## Co jest w trakcie
- Brak aktywnego milestone'u.

## Co jest następne
- Odblokować Milestone 3 po doprecyzowaniu UX dla filtrów i masowych akcji.

## Blokery i ryzyka
- Milestone 3 i 4 pozostają `blocked` zgodnie z roadmapą.

## Ostatnie aktualizacje
- 2026-04-01: zakończono Milestone 1 i Milestone 2; testy `unittest` przechodzą lokalnie.
