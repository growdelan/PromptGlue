# PRD — PromptGlue v2

## 1. Informacje podstawowe

**Nazwa produktu:** PromptGlue v2  
**Typ produktu:** desktop utility / local-first productivity tool for LAG (LLM-assisted generation)  
**Docelowa platforma:** desktop (macOS / Windows / Linux)  
**Status dokumentu:** propozycja PRD v1  
**Właściciel produktu:** Growdelan  
**Cel dokumentu:** zdefiniowanie kierunku rozwoju PromptGlue v2 tak, aby aplikacja była bardziej użyteczna, przewidywalna, łatwiejsza w utrzymaniu i gotowa do dalszej rozbudowy.

---

## 2. Streszczenie produktu

PromptGlue to narzędzie, które skleja prompt użytkownika i zawartość wybranych plików lub katalogów do jednego tekstu wejściowego dla modeli LLM. Produkt rozwiązuje realny problem użytkowników, którzy pracują z modelami lub interfejsami nieobsługującymi wygodnie wielu plików, chcą kontrolować liczbę tokenów albo przygotować jeden gotowy blok wejściowy do wklejenia.

Wersja v2 ma przekształcić PromptGlue z prostego utility w bardziej dopracowane narzędzie do pracy z kontekstem dla modeli AI. Najważniejsze cele tej wersji to:
- poprawa przewidywalności działania,
- usunięcie błędów w zarządzaniu zawartością promptu,
- lepsza kontrola nad tym, co trafia do finalnego outputu,
- poprawa ergonomii pracy na większej liczbie plików,
- stworzenie fundamentu pod CLI i dalszą automatyzację.

---

## 3. Problem do rozwiązania

Użytkownik chce szybko przygotować jeden końcowy prompt zawierający:
- instrukcję,
- kontekst z plików,
- wybrane fragmenty kodu / dokumentów,
- kontrolę nad rozmiarem wejścia.

Obecne ograniczenia:
1. Aplikacja jest przydatna, ale ma jeszcze poziom MVP.
2. Praca na większym katalogu staje się mniej wygodna.
3. Brakuje mocniejszej kontroli nad finalnym wynikiem.
4. Istnieje krytyczny problem spójności:  
   **po załadowaniu katalogu i usuwaniu poszczególnych plików, odpowiadające im bloki nie znikają z finalnego promptu**.  
   To powoduje rozjazd między tym, co użytkownik widzi jako „załączone”, a tym, co faktycznie trafia do wyniku.

Ten ostatni punkt jest kluczowy, bo uderza w zaufanie do produktu.

---

## 4. Wizja v2

PromptGlue v2 ma być:
- **local-first**,
- **przewidywalny**,
- **transparentny**,
- **szybki w obsłudze**,
- **dobry zarówno dla pojedynczego promptu, jak i pracy na całym repozytorium**.

Wersja v2 nie ma być jeszcze pełną platformą do zarządzania kontekstem dla AI. Ma być bardzo dobrym, niezawodnym narzędziem do:
- ładowania plików,
- selekcji kontekstu,
- usuwania / wykluczania treści,
- podglądu końcowego wyniku,
- eksportu do formatów przydatnych w pracy z LLM.

---

## 5. Cele biznesowe i produktowe

### Cele główne
1. Zwiększyć zaufanie do działania aplikacji.
2. Zmniejszyć liczbę błędów użytkownika przy budowie promptu.
3. Poprawić wygodę pracy na większej liczbie plików.
4. Ułatwić rozwój produktu w kolejnych wersjach.
5. Przygotować architekturę pod przyszłe CLI i workflow z agentami AI.

### Mierniki sukcesu
- 0 znanych przypadków rozjazdu między listą plików a finalnym promptem.
- Skrócenie czasu przygotowania promptu z wielu plików.
- Mniejsza liczba ręcznych korekt po skopiowaniu promptu.
- Możliwość bezpiecznego rozwijania aplikacji dzięki wydzieleniu core od GUI.
- Dodanie co najmniej 3 nowych funkcji zwiększających użyteczność bez pogorszenia prostoty.

---

## 6. Grupa docelowa

### Segment podstawowy
- developerzy,
- DevOps / Cloud engineers,
- osoby pracujące z repozytoriami i kodem,
- użytkownicy LLM, którzy chcą ręcznie kontrolować kontekst.

### Segment wtórny
- PM / analitycy kopiujący dokumenty do modeli,
- technical writers,
- konsultanci przygotowujący duże prompty z wielu źródeł,
- osoby robiące code review z pomocą AI.

---

## 7. Najważniejsze przypadki użycia

1. **Załaduj katalog projektu i zbuduj prompt do analizy repozytorium.**
2. **Dodaj kilka plików konfiguracyjnych i instrukcję, a potem skopiuj finalny prompt.**
3. **Załaduj katalog, wyklucz część plików i wygeneruj mniejszy, czystszy kontekst.**
4. **Przejrzyj podgląd końcowego outputu przed skopiowaniem.**
5. **Wyeksportuj wynik do pliku `.md` lub `.txt`.**
6. **Pracuj iteracyjnie: dodawaj/usuwaj pliki i miej pewność, że wynik zawsze odzwierciedla aktualny stan.**

---

## 8. Najważniejsze problemy obecnej wersji

### 8.1 Problem krytyczny — niespójność przy usuwaniu plików
Po załadowaniu katalogu usunięcie pliku z listy nie usuwa odpowiadającego mu bloku z finalnego promptu.

### Dlaczego to jest krytyczne
- użytkownik traci zaufanie do narzędzia,
- może przypadkiem wysłać do modelu niechciane dane,
- wynik jest nieprzewidywalny,
- UI pokazuje inny stan niż rzeczywisty output.

### Wniosek produktowy
W v2 finalny prompt **musi być zawsze renderowany ze stanu źródłowego**, a nie aktualizowany „doklejaniem” lub częściowym mutowaniem tekstu wynikowego.

---

## 9. Zakres v2

### In scope
- przebudowa modelu danych,
- poprawa logiki generowania outputu,
- przewidywalne usuwanie plików,
- final preview,
- eksport,
- lepsze zarządzanie listą plików,
- lepsze komunikaty błędów,
- przygotowanie pod CLI/core.

### Out of scope
- chmura / synchronizacja online,
- multi-user collaboration,
- wbudowane połączenia z API LLM,
- zaawansowane AI features typu automatyczny summarization pipeline,
- pełna wersja webowa.

---

## 10. Wymagania produktowe

## 10.1 Zarządzanie wejściem

### Funkcja: dodawanie plików
Użytkownik może dodać pojedyncze pliki do sesji.

**Wymagania:**
- pliki pojawiają się na liście wejść,
- każdy plik ma status: aktywny / wykluczony / błąd odczytu,
- użytkownik widzi ścieżkę, rozmiar i typ,
- pliki binarne są oznaczane i domyślnie pomijane.

### Funkcja: dodawanie katalogu
Użytkownik może dodać cały katalog.

**Wymagania:**
- rekursywne skanowanie,
- respektowanie `.gitignore`,
- własne wzorce wykluczeń,
- pomijanie `.git`,
- zabezpieczenie przed zbyt dużym wejściem,
- raport: ile plików dodano, ile pominięto, dlaczego.

---

## 10.2 Zarządzanie listą plików

### Funkcja: usuwanie pliku
Użytkownik może usunąć plik z sesji.

**Krytyczne wymaganie:**
- po usunięciu pliku z listy odpowiadający blok **musi zniknąć z finalnego promptu**.

### Funkcja: wykluczanie bez usuwania
Użytkownik może oznaczyć plik jako „nie uwzględniaj w wyniku”, ale zostawić go na liście.

**Wymagania:**
- plik pozostaje widoczny,
- nie trafia do finalnego outputu,
- status jest czytelny w UI,
- liczniki tokenów uwzględniają tylko aktywne pliki.

### Funkcja: masowe akcje
- zaznacz wiele plików,
- usuń zaznaczone,
- wyklucz zaznaczone,
- przywróć zaznaczone,
- filtruj po nazwie / rozszerzeniu / statusie.

---

## 10.3 Budowa finalnego promptu

### Główna zasada architektoniczna
Finalny prompt ma być **renderowany od zera** na podstawie aktualnego modelu sesji:
- instrukcja użytkownika,
- aktywne pliki,
- kolejność plików,
- ustawienia formatowania.

### Zabronione podejście
- ręczne „doklejanie” bloków do tekstu wynikowego,
- częściowa mutacja wcześniej wygenerowanego outputu,
- przechowywanie finalnego promptu jako źródła prawdy.

### Wymagania
- wynik zawsze odzwierciedla aktualny stan sesji,
- po każdej zmianie możliwe jest odświeżenie preview,
- kolejność bloków jest deterministyczna,
- format jest spójny.

---

## 10.4 Preview finalnego outputu

### Funkcja: final preview
Użytkownik może otworzyć podgląd całego wygenerowanego promptu przed kopiowaniem lub eksportem.

**Wymagania:**
- pełny tekst końcowy,
- możliwość szybkiego wyszukania fragmentu,
- widoczna liczba tokenów,
- możliwość kopiowania z preview,
- możliwość eksportu z preview.

### Wartość
- większe zaufanie,
- łatwiejsza kontrola jakości,
- szybsze wykrywanie niechcianych fragmentów.

---

## 10.5 Tokeny i limity

### Funkcja: token accounting
System pokazuje:
- tokeny promptu użytkownika,
- tokeny per plik,
- sumę końcową,
- progi ostrzegawcze.

**Wymagania:**
- liczenie tylko dla aktywnych elementów,
- szybka aktualizacja po każdej zmianie,
- osobny widok breakdownu,
- ostrzeżenia przy przekroczeniu progów.

### Usprawnienie v2
- cache tokenów per plik,
- przeliczanie tylko dla zmienionych elementów,
- osobne przeliczenie końcowe dla aktywnej sesji.

---

## 10.6 Eksport i formaty wyjścia

### Funkcja: kopiowanie
Użytkownik może skopiować finalny prompt do schowka.

### Funkcja: eksport do pliku
Użytkownik może zapisać wynik do:
- `.md`,
- `.txt`.

### Funkcja: profile formatu
Co najmniej 3 profile:
1. Plain text
2. Markdown blocks
3. XML-like / structured context

**Cel:** lepiej dopasować output do różnych modeli i stylów pracy.

---

## 10.7 Błędy i komunikacja

### Wymagania
- brak cichego ignorowania błędów,
- każdy nieczytelny plik powinien mieć status i powód,
- użytkownik powinien wiedzieć:
  - czego nie dodano,
  - co pominięto,
  - dlaczego.

### Minimalny standard
- toast / dialog / status bar z informacją,
- raport po wczytaniu katalogu,
- logika błędów odseparowana od GUI.

---

## 11. Wymagania UX

### Zasady
- prostota,
- przewidywalność,
- minimum ukrytej magii,
- UI ma odzwierciedlać rzeczywisty stan danych.

### Główne elementy ekranu v2
1. Pole na instrukcję / prompt użytkownika
2. Panel listy plików
3. Panel szczegółów / preview pliku
4. Pasek akcji
5. Pasek statusu z tokenami i liczbą aktywnych plików

### Usprawnienia UX
- wyszukiwarka po liście plików,
- sortowanie,
- szybkie filtry:
  - wszystkie,
  - aktywne,
  - wykluczone,
  - błędy,
- czytelne badge statusów,
- kontekstowe akcje pod prawym przyciskiem.

---

## 12. Wymagania techniczne

## 12.1 Nowa architektura logiczna

W v2 należy oddzielić GUI od logiki produktu.

### Proponowane warstwy
1. **UI layer**
   - PyQt
   - tylko prezentacja i event handling

2. **Application layer**
   - operacje na sesji
   - use case’y: add files, remove files, exclude, build output, export

3. **Domain / Core layer**
   - model danych sesji,
   - renderer finalnego promptu,
   - ignore engine,
   - token service,
   - file ingestion rules

4. **Infrastructure layer**
   - filesystem,
   - clipboard,
   - export,
   - config storage

---

## 12.2 Model danych

### Encje
#### Session
- prompt_text
- list of entries
- output_format
- settings
- derived metadata

#### Entry
- id
- path
- source_type (file / dir import)
- content
- status
- include_in_output (bool)
- token_count
- read_error
- is_binary
- size
- last_loaded_at

#### BuildResult
- rendered_output
- total_tokens
- included_entries
- excluded_entries
- warnings
- errors

### Ważna zasada
`BuildResult` jest wynikiem renderowania, a nie źródłem prawdy.  
Źródłem prawdy jest `Session`.

---

## 12.3 Logika usuwania plików — wymaganie krytyczne

### Stan docelowy
Usunięcie pliku:
- usuwa `Entry` z `Session.entries`,
- invaliduje cache builda,
- invaliduje cache tokenów zależnych od sesji,
- po kolejnym buildzie plik nie istnieje w wyniku.

### Kryterium akceptacji
Jeżeli użytkownik:
1. załaduje katalog z 20 plikami,
2. usunie 3 z nich,
3. otworzy final preview,

to w preview i kopiowanym outputcie nie może być żadnego bloku odpowiadającego tym 3 plikom.

### Regresja do uniknięcia
Nie może istnieć sytuacja, w której:
- lista plików pokazuje A, B, C,
- a output dalej zawiera A, B, C, D.

---

## 12.4 Testowalność

W v2 należy dodać testy dla:
- renderowania finalnego outputu,
- usuwania plików z sesji,
- exclude/include,
- `.gitignore`,
- custom exclude patterns,
- wykrywania binarek,
- liczenia tokenów,
- eksportu.

### Test obowiązkowy
**Po dodaniu katalogu i usunięciu pliku jego blok nie może występować w wynikowym promptcie.**

---

## 12.5 Wydajność

### Oczekiwania
- UI nie może się zacinać przy większym katalogu,
- odczyt plików powinien być raportowany,
- build outputu powinien być szybki,
- tokeny powinny być cache’owane.

### Działania
- cache tokenów per entry,
- lazy preview dla dużych plików,
- odświeżenie builda tylko po zmianach,
- opcjonalnie background worker do cięższych operacji.

---

## 12.6 Konfiguracja i developer experience

### Wymagania
- czytelna struktura repo,
- prosty entrypoint,
- sensowny `pyproject.toml`,
- jasna instrukcja uruchamiania,
- spójne wersjonowanie,
- podstawowy CI:
  - testy,
  - lint,
  - build check.

---

## 13. Wymagania niefunkcjonalne

### Niezawodność
- brak rozjazdu między UI i outputem,
- brak cichego gubienia plików,
- czytelne błędy.

### Utrzymanie
- rozdzielenie warstw,
- testowalne core,
- ograniczenie logiki w kontrolerach GUI.

### Bezpieczeństwo
- aplikacja lokalna,
- bez obowiązkowych zewnętrznych połączeń,
- ostrożne obchodzenie się z dużymi / binarnymi plikami.

### Skalowalność produktu
- gotowość do dodania CLI,
- możliwość przyszłego reuse core w wersji terminalowej lub webowej.

---

## 14. User stories

### US-01
Jako użytkownik chcę dodać katalog projektu, aby szybko zbudować kontekst dla LLM.

### US-02
Jako użytkownik chcę usunąć wybrane pliki z listy i mieć pewność, że ich treść zniknie też z finalnego promptu.

### US-03
Jako użytkownik chcę wykluczyć plik bez usuwania go z listy, aby testować różne warianty promptu.

### US-04
Jako użytkownik chcę zobaczyć finalny output przed kopiowaniem, aby uniknąć pomyłek.

### US-05
Jako użytkownik chcę wyeksportować wynik do pliku, aby użyć go później lub przekazać dalej.

### US-06
Jako użytkownik chcę widzieć tokeny tylko dla aktywnych elementów, aby świadomie zarządzać limitem kontekstu.

### US-07
Jako developer chcę mieć wydzielony core, aby łatwo testować logikę i rozwijać CLI.

---

## 15. Kryteria akceptacji

## 15.1 Kryteria obowiązkowe
1. Po usunięciu pliku z sesji jego blok nie występuje w finalnym promptcie.
2. Po wykluczeniu pliku z sesji jego blok nie występuje w finalnym promptcie.
3. Final preview pokazuje dokładnie to samo, co trafia do schowka i eksportu.
4. Licznik tokenów odpowiada tylko aktywnym elementom.
5. Błędy odczytu są jawnie raportowane.
6. Wczytanie katalogu pokazuje raport z plikami dodanymi i pominiętymi.
7. Logika budowy outputu działa niezależnie od GUI.

## 15.2 Kryteria jakościowe
1. Kod core ma testy jednostkowe.
2. Repo ma podstawowy CI.
3. README zawiera realny onboarding.
4. Struktura projektu jest czytelna dla nowego developera.

---

## 16. Priorytety funkcji

### P0 — must have
- naprawa usuwania bloków z outputu,
- renderowanie outputu ze stanu sesji,
- final preview,
- poprawne include/exclude,
- czytelne błędy,
- podstawowe testy.

### P1 — should have
- eksport do `.md` i `.txt`,
- wyszukiwarka po liście plików,
- masowe akcje,
- cache tokenów,
- raport z importu katalogu.

### P2 — nice to have
- profile outputu,
- drag & drop,
- preset pod konkretne workflow,
- CLI,
- zapis / odczyt sesji.

---

## 17. Proponowana roadmapa implementacyjna

## Faza 1 — stabilność i zaufanie
Cel: naprawić podstawy.
- wprowadzić `Session` jako source of truth,
- przebudować build outputu,
- naprawić usuwanie / exclude,
- dodać testy regresyjne,
- dodać final preview.

## Faza 2 — ergonomia
Cel: ułatwić pracę.
- wyszukiwarka i filtrowanie,
- masowe akcje,
- eksport,
- raporty i lepsze komunikaty.

## Faza 3 — fundament pod rozwój
Cel: umożliwić dalszą ewolucję.
- wydzielony core,
- CI,
- CLI,
- możliwość serializacji sesji.

---

## 18. Ryzyka

1. **Ryzyko regresji przy przebudowie logiki builda**  
   Mitigacja: testy snapshotowe outputu.

2. **Ryzyko przekombinowania UI**  
   Mitigacja: v2 ma pozostać prostym desktop utility.

3. **Ryzyko utrzymania starej logiki równolegle z nową**  
   Mitigacja: jeden spójny model danych i jeden renderer.

4. **Ryzyko spadku wydajności po każdej zmianie stanu**  
   Mitigacja: cache tokenów i lekki build pipeline.

---

## 19. Decyzje technologiczne

### Obecny stack
Python + PyQt pozostaje sensownym wyborem dla v2.

### Rekomendacja
Nie robić pełnego rewrite'u na tym etapie.

### Co warto zrobić zamiast rewrite'u
- rozdzielić core od GUI,
- zaprojektować architekturę pod późniejsze CLI,
- dopiero potem ocenić, czy część core / CLI ma sens przenieść np. do Go.

### Kiedy Go zaczyna mieć sens
- gdy pojawi się osobne CLI,
- gdy liczy się prosty single-binary deployment,
- gdy narzędzie ma być używane szeroko w terminalu i automatyzacjach,
- gdy wydajność I/O i concurrency staną się realnym bottleneckiem.

---

## 20. Plan wdrożenia na 30 dni

### Tydzień 1
- zaprojektować `Session`, `Entry`, `BuildResult`,
- wydzielić renderer finalnego promptu,
- przygotować test regresyjny dla buga z usuwaniem plików.

### Tydzień 2
- wdrożyć nowy flow add/remove/exclude,
- dopiąć final preview,
- poprawić liczenie tokenów dla aktywnego stanu.

### Tydzień 3
- dodać eksport,
- dodać raport ładowania katalogu,
- dodać wyszukiwarkę i filtry listy plików.

### Tydzień 4
- uporządkować repo,
- dodać CI i testy,
- poprawić README,
- przygotować bazę pod CLI.

---

## 21. Definicja sukcesu v2

PromptGlue v2 będzie sukcesem, jeśli:
- użytkownik ufa, że to co widzi w aplikacji jest dokładnie tym, co trafia do outputu,
- usuwanie i wykluczanie działa bezbłędnie,
- praca na katalogach jest wygodniejsza,
- produkt pozostaje prosty,
- architektura pozwala rozwijać wersję v3 bez chaosu.

---

## 22. Podsumowanie

PromptGlue v2 nie powinien być „większy dla zasady”. Powinien być przede wszystkim **bardziej przewidywalny, bardziej spójny i bardziej użyteczny**. Najważniejsza zmiana to przejście z myślenia o promptcie jako o ręcznie utrzymywanym tekście na myślenie o nim jako o **wyniku renderowania aktualnej sesji**. To rozwiązuje obecny błąd z usuwaniem bloków, porządkuje architekturę i tworzy fundament pod dalszy rozwój produktu.

