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

## Co jest skończone
- Wygenerowano `spec.md` i `ROADMAP.md` na podstawie `prd/000-initial-prd.md`.
- Milestone 0.5 oznaczony jako `done`.
- Milestone 1 oznaczony jako `done`.
- Milestone 2 oznaczony jako `done`.
- Milestone 3 oznaczony jako `done`.

## Co jest w trakcie
- Milestone 4: Fundament pod rozwój.

## Co jest następne
- Dodać podstawowy CI (testy + build check).
- Dopić onboarding i strukturę repo w README.
- Dodać minimalny punkt zaczepienia pod CLI.

## Blokery i ryzyka
- Brak aktywnych blockerów dla M4.

## Ostatnie aktualizacje
- 2026-04-01: zakończono M1, M2 i M3; testy `unittest` przechodzą lokalnie.
