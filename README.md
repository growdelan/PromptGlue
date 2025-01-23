# PromptGlue

## Opis
PromptGlue to aplikacja umożliwiająca szybkie połącznie z promptu + załączonych plików w jeden blok tekstowy, dla modeli które aktualnie nie pozwalają dołączać plików. 

## Instalacja

### 1. Powołanie środowiska wirtualnego
Zaleca się korzystanie ze środowiska wirtualnego, aby zarządzać zależnościami projektu i uniknąć konfliktów między wersjami bibliotek. Aby utworzyć środowisko wirtualne, wykonaj poniższe kroki:

```bash
python -m venv env
```

Aktywuj środowisko wirtualne:
- Na systemie Linux/macOS:
  ```bash
  source env/bin/activate
  ```
- Na systemie Windows:
  ```bash
  .\env\Scripts\activate
  ```

### 2. Instalacja paczek
Zainstaluj wymagane zależności znajdujące się w pliku `requirements.txt`:

```bash
pip install -r requirements.txt
```

Plik `requirements.txt` zawiera następujące biblioteki:
- `PyQt5 == 5.15.11`: Do stworzenia graficznego interfejsu użytkownika.

## Uruchomienie

Po skonfigurowaniu środowiska i zainstalowaniu zależności aplikację można uruchomić, korzystając z poniższego polecenia w terminalu:

```bash
python main.py
```



