# Specyfikacja techniczna

## Cel
PromptGlue v2 to lokalna aplikacja desktopowa do budowania jednego, kontrolowanego wejścia dla modeli LLM z treści promptu oraz plików/katalogów.

- Rozwiązuje problem niespójności i nieprzewidywalności przy pracy z wieloma plikami (szczególnie przy usuwaniu i wykluczaniu).
- Główni użytkownicy: developerzy, DevOps/Cloud engineers i osoby pracujące na repozytoriach.
- Poza zakresem v2: chmura/synchronizacja online, integracje z API LLM, multi-user collaboration, pełna wersja webowa.

---

## Zakres funkcjonalny (high-level)
Kluczowe funkcjonalności v2:

- ładowanie pojedynczych plików i całych katalogów (rekurencyjnie),
- respektowanie `.gitignore`, własnych wzorców wykluczeń i pomijanie binarek,
- zarządzanie listą wejść (remove / exclude / include),
- budowanie finalnego outputu z aktualnego stanu sesji,
- podgląd finalnego outputu przed kopiowaniem,
- kopiowanie do schowka i eksport do `.md` / `.txt`,
- kontrola tokenów (prompt, pliki, suma, ostrzeżenia).

Główne przepływy użytkownika:

- użytkownik wpisuje instrukcję, dodaje pliki/katalog, selekcjonuje kontekst, sprawdza preview i kopiuje/eksportuje wynik,
- użytkownik iteracyjnie usuwa/wyklucza elementy i oczekuje, że finalny output zawsze odzwierciedla stan listy wejść.

Czego aplikacja nie robi:

- nie wysyła danych do modeli AI ani zewnętrznych API,
- nie realizuje funkcji collaborative/online,
- nie wykonuje automatycznego pipeline'u AI (np. auto-summarization).

Bez wchodzenia w szczegóły implementacyjne.

---

## Architektura i przepływ danych
Docelowy model koncepcyjny:

1. Główne komponenty systemu
- UI layer (PyQt): prezentacja stanu i obsługa zdarzeń użytkownika.
- Application layer: use-case'y operacyjne (add/remove/exclude/build/preview/export).
- Domain/Core layer: model sesji, renderer outputu, logika tokenów i walidacji wejścia.
- Infrastructure layer: filesystem, clipboard, eksport plików, konfiguracja.

2. Przepływ danych między komponentami
- Zdarzenie z UI aktualizuje stan sesji.
- Renderer buduje finalny output na podstawie bieżącej sesji.
- Preview/copy/export korzystają z tego samego wyniku renderowania.
- Token service wylicza metryki dla aktywnych elementów sesji.

3. Granice odpowiedzialności
- UI nie utrzymuje logiki domenowej jako źródła prawdy.
- Core odpowiada za spójność i deterministyczne generowanie wyniku.
- Integracje systemowe (plik/schowek) są odseparowane od logiki budowania outputu.

---

## Komponenty techniczne
Kluczowe komponenty i odpowiedzialności:

- `Session`: źródło prawdy o aktualnym stanie promptu i listy wejść.
- `Entry`: pojedynczy element wejścia (plik/element pochodzący z importu katalogu).
- `BuildResult`: wynik renderowania (tekst, tokeny, ostrzeżenia/błędy, statystyki include/exclude).
- Prompt renderer: deterministyczna budowa finalnego outputu od zera.
- Ignore engine: `.gitignore` i custom patterns.
- Token service: liczenie i progi ostrzegawcze.
- Import/reporting: ładowanie katalogu z raportem dodanych/pominiętych plików i powodów.
- Preview/export bridge: spójny kanał do podglądu, kopiowania i zapisu pliku.
- Minimalny CLI hook: uruchomienie renderowania bez GUI dla prostych workflow terminalowych.
- CI pipeline: automatyczna walidacja testów i check kompilacji.

---

## Decyzje techniczne
- Decyzja: Python + PyQt pozostają bazowym stackiem v2 (bez pełnego rewrite'u).
- Uzasadnienie: PRD wskazuje na potrzebę szybkiego zwiększenia niezawodności i utrzymania ciągłości rozwoju.
- Konsekwencje: rozwój koncentruje się na wydzieleniu core od GUI i testowalności logiki domenowej.

- Decyzja: Finalny output jest renderowany od zera na podstawie `Session`; `BuildResult` nie jest źródłem prawdy.
- Uzasadnienie: eliminuje krytyczny rozjazd między listą plików a treścią wynikową.
- Konsekwencje: copy/preview/export muszą używać wspólnego pipeline'u renderowania.

- Decyzja: Wprowadzenie cache tokenów per entry jako optymalizacji v2.
- Uzasadnienie: PRD wymaga płynności pracy na większych katalogach i szybkiej aktualizacji liczników.
- Konsekwencje: potrzebna strategia invalidacji cache po zmianach stanu sesji.

- Decyzja: Domyślny profil outputu dla copy/export to XML-like.
- Uzasadnienie: zachowuje kompatybilność wsteczną z dotychczasowym formatem bloków `<file ...>`.
- Konsekwencje: użytkownik może ręcznie przełączyć się na profile markdown/plain zależnie od workflow.

- Decyzja: Bazowy CI obejmuje `unittest` i check kompilacji (`compileall`).
- Uzasadnienie: szybka walidacja regresji i podstawowa kontrola jakości bez rozbudowy narzędzi.
- Konsekwencje: każda zmiana przechodzi przez jednolity minimalny pipeline.

- Decyzja: Dodany minimalny punkt zaczepienia CLI bez zmiany głównego entrypointu GUI.
- Uzasadnienie: przygotowuje fundament pod dalszy rozwój narzędzia terminalowego.
- Konsekwencje: logika renderowania pozostaje współdzielona przez GUI i CLI przez warstwę core.

TODO: [Jaka ma być dokładna polityka sortowania/kolejności wpisów w finalnym outputcie przy mieszanym imporcie plików i katalogów?]

---

## Jakość i kryteria akceptacji
Wymagania jakościowe v2:

- brak znanego rozjazdu między listą aktywnych wejść a finalnym outputem,
- deterministyczne renderowanie outputu,
- jawne raportowanie błędów odczytu i pominięć,
- testowalny core niezależny od GUI,
- testy regresyjne dla remove/exclude i build pipeline,
- zgodność preview/copy/export (ten sam wynik),
- uruchamianie i testowanie opisane w README.

---

## Zasady zmian i ewolucji
- zmiany funkcjonalne -> aktualizacja `ROADMAP.md`
- zmiany architektoniczne -> aktualizacja tej specyfikacji
- nowe zależności -> wpis do `## Decyzje techniczne`
- refactory tylko w ramach aktualnego milestone'u

---

## Powiązanie z roadmapą
- Szczegóły milestone'ów i ich statusy znajdują się w `ROADMAP.md`.

---

## Status specyfikacji
- Data utworzenia: 2025-03-07
- Ostatnia aktualizacja: 2026-04-01
- Aktualny zakres obowiązywania: PromptGlue v2 (stabilność, spójność outputu, ergonomia i fundament pod dalszy rozwój)
