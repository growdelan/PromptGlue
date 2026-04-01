# Roadmapa (milestones)

## Statusy milestone'ów
Dozwolone statusy:
- planned
- in_progress
- done
- blocked

---

## Milestone 0.5: Minimal end-to-end slice (done)

Cel:
- aplikacja uruchamia się
- wykonuje jedno bardzo proste zadanie
- zwraca poprawny wynik

Definition of Done:
- aplikację da się uruchomić jednym poleceniem (opisanym w README.md)
- istnieje co najmniej jeden smoke test
- testy przechodzą lokalnie
- brak placeholderów w kodzie

Zakres:
- minimalny entrypoint aplikacji
- minimalna logika domenowa
- minimalna obsługa IO (jeśli dotyczy)
- smoke test end-to-end

---

## Milestone 1: Spójny model sesji i renderer outputu (done)

Cel:
- usunąć ryzyko rozjazdu między listą wejść a finalnym promptem
- wprowadzić jeden pipeline budowania outputu

Definition of Done:
- istnieje jawny model sesji jako źródło prawdy dla builda
- usunięcie pliku usuwa jego blok z outputu
- wykluczenie pliku usuwa jego blok z outputu
- renderowanie finalnego outputu jest deterministyczne i testowalne bez GUI
- testy jednostkowe dla krytycznych scenariuszy przechodzą lokalnie

Zakres:
- wydzielenie core/domain dla sesji i renderowania
- integracja GUI z core dla akcji add/remove/exclude/copy
- regresyjne testy remove/exclude/build

Uwagi:
- priorytet P0 z PRD (zaufanie i przewidywalność)

---

## Milestone 2: Preview finalnego outputu i eksport (done)

Cel:
- zwiększyć kontrolę użytkownika nad końcowym wynikiem
- zapewnić spójność preview, copy i export

Definition of Done:
- użytkownik może otworzyć final preview całego outputu
- preview pokazuje ten sam wynik co copy
- możliwy eksport do `.md` i `.txt`
- dostępne są profile formatu outputu: plain text, markdown blocks, xml-like
- testy jednostkowe dla renderer/profili i eksportu przechodzą lokalnie

Zakres:
- final preview dialog oparty o wspólny build pipeline
- mechanizm eksportu i wybór formatu
- rozszerzenie renderera o profile wyjścia

Uwagi:
- TODO: doprecyzować domyślny profil wyjścia dla copy/export

---

## Milestone 3: Ergonomia i komunikacja błędów (blocked)

Cel:
- usprawnić pracę na większych zestawach plików
- podnieść transparentność działania

Definition of Done:
- dostępne filtrowanie listy plików (nazwa/rozszerzenie/status)
- dostępne masowe akcje include/exclude/remove
- raport importu katalogu zawiera przyczyny pominięć
- błędy odczytu mają jawny status i powód
- testy dla filtrów/masowych akcji/raportów przechodzą lokalnie

Zakres:
- komponent filtrów i masowych akcji
- standaryzacja raportowania błędów i pominięć
- dopięcie testów scenariuszy UX

Uwagi:
- blocked do czasu domknięcia M1 i M2 oraz doprecyzowania UX dla masowych akcji

---

## Milestone 4: Fundament pod rozwój (blocked)

Cel:
- przygotować repo i proces pod dalszą ewolucję produktu

Definition of Done:
- podstawowy CI uruchamia testy i kontrole jakości
- README zawiera onboarding i aktualne komendy uruchamiania/testów
- struktura repo oraz granice warstw są czytelne
- istnieje minimalny punkt zaczepienia pod przyszłe CLI

Zakres:
- konfiguracja podstawowego CI
- porządki developerskie i dokumentacyjne
- przygotowanie rozszerzalności core

Uwagi:
- blocked do czasu stabilizacji funkcjonalnej po M2
