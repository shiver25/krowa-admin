# Krowa Admin - ustalenia i kierunek rozwoju

## Cel projektu

Krowa Admin ma pozostać prostym narzędziem administracyjnym, które pokazuje stan wybranych elementów systemu po zalogowaniu przez SSH.

Projekt ma też służyć do nauki programowania na praktycznym przykładzie: konfiguracja, modularność, obsługa błędów, wywoływanie komend systemowych, praca z plikami i późniejsza możliwość rozbudowy o panel WWW.

## Obecny problem

Aktualnie wiele rzeczy jest wpisanych na sztywno w kodzie:

- lista monitorowanych usług,
- ścieżka tokena K3s,
- ścieżka backupu tokena,
- lista systemowych namespace'ów,
- logika związana z K3s,
- zakres informacji wyświetlanych przy logowaniu.

To powoduje, że na różnych serwerach trudno szybko włączyć tylko te elementy, które są potrzebne.

## Główny kierunek

Najpierw warto dodać plik konfiguracyjny, a dopiero później myśleć o Flasku.

Przykładowy kierunek:

```yaml
checks:
  services:
    enabled: true
    services:
      - docker
      - ssh
      - k3s

  k3s_cluster:
    enabled: true

  namespaces:
    enabled: true
    system_namespaces:
      - default
      - kube-system
      - kube-public
      - kube-node-lease
      - metallb-system

  k3s_token:
    enabled: false
    token_path: /var/lib/rancher/k3s/server/token
    backup_path: /home/pi/k3s-token-backup/token.bak

  disk:
    enabled: true
    paths:
      - /
      - /home
```

## Proponowana struktura

Docelowo kod można rozdzielić na rdzeń programu i osobne checki:

```text
krowa-admin/
  service-status.py
  config.yaml
  checks/
    services.py
    k3s_cluster.py
    k3s_token.py
    namespaces.py
    disk.py
    docker.py
```

Główny skrypt powinien:

- wczytać konfigurację,
- sprawdzić, które checki są włączone,
- uruchomić odpowiednie moduły,
- zebrać wynik,
- wyświetlić raport w terminalu.

Każdy check może mieć prosty interfejs, np.:

```python
def run(config):
    return "tekst raportu"
```

Na start nie trzeba budować pełnego systemu pluginów. Wystarczy prosty mechanizm osobnych plików i `enabled: true/false` w konfiguracji.

## Flask

Flask ma sens, ale raczej jako kolejny etap, nie pierwszy.

Flask warto dodać, jeśli projekt ma:

- mieć panel WWW,
- udostępniać endpoint `/status`,
- działać z telefonu lub przeglądarki,
- pokazywać historię lub alerty,
- monitorować kilka maszyn,
- udostępniać dane innym narzędziom.

Jeśli główny przypadek użycia to komunikat po zalogowaniu przez SSH, Flask byłby teraz dodatkową warstwą do utrzymania.

Dobrym krokiem po konfiguracji będzie dodanie trybu JSON:

```bash
service-status.py --json
```

Taki tryb ułatwi późniejsze użycie tej samej logiki przez Flaska.

## Etapy rozwoju

1. Wyciągnąć ustawienia do `config.yaml`.
2. Uporządkować obecny kod na mniejsze funkcje.
3. Przenieść checki do osobnych plików w katalogu `checks/`.
4. Dodać opcję `--config`, np.:

   ```bash
   service-status.py --config /etc/krowa-admin/config.yaml
   ```

5. Dodać tryb `--json`.
6. Dopiero później rozważyć prosty panel lub API we Flasku.

## Rzeczy do poprawy w obecnym kodzie

- `get_namespace_report()` uruchamia się nawet wtedy, gdy K3s nie działa.
- `shell=True` przy części komend można ograniczyć.
- Backup tokena K3s jest tworzony przed właściwym sprawdzeniem, co może ukryć zmianę tokena.
- Katalog backupu tokena może nie istnieć.
- Lista usług jest wpisana na sztywno.
- Lista namespace'ów systemowych jest wpisana na sztywno.
- Warto rozdzielić logikę pobierania danych od formatowania outputu.

## Nauka programowania

Ten projekt nadaje się do nauki, bo dotyka realnych problemów administracyjnych:

- konfiguracji,
- modułów,
- obsługi błędów,
- pracy z systemem Linux,
- uruchamiania komend,
- uprawnień,
- K3s,
- SSH,
- późniejszej integracji z WWW.

Warto uczyć się nie przez przepisywanie tutoriali, tylko przez stopniową przebudowę tego projektu.

Najważniejsze pytania przy dalszej pracy:

- czy ta rzecz powinna być w kodzie, czy w konfiguracji?
- co się stanie, gdy komenda systemowa nie odpowie?
- czy błąd może zepsuć logowanie SSH?
- czy nie pokazujemy sekretów w outputcie lub logach?
- czy po miesiącu przerwy nadal będzie wiadomo, jak to działa?

