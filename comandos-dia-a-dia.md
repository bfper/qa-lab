# Comandos do dia a dia — WSL2 + qa-lab

Referência rápida. Guarde em `~/lab/qa-lab/` ou no Obsidian.

---

## 1. Abrir o ambiente

### Entrar no Ubuntu

Três caminhos, todos equivalentes:

- Menu Iniciar → **Ubuntu**
- Terminal do Windows → aba nova → **Ubuntu**
- No PowerShell: `wsl` (ou `wsl -d Ubuntu-24.04`)

### A rotina de abertura do lab

```bash
cd ~/lab/qa-lab
source .venv/bin/activate
code .
```

Depois disso o prompt mostra `(.venv)` — é o sinal de que o Python certo
está ativo. Sem isso, `pytest` não existe.

> Atalho: crie um apelido para não digitar sempre.
> ```bash
> echo "alias lab='cd ~/lab/qa-lab && source .venv/bin/activate'" >> ~/.bashrc
> source ~/.bashrc
> ```
> A partir daí, só `lab`.

### Sair

- `exit` — fecha o Ubuntu, volta ao PowerShell
- `deactivate` — sai do venv, continua no Ubuntu
- `wsl --shutdown` (no PowerShell) — desliga o Linux inteiro

---

## 2. Navegar no Linux

| Comando | O que faz |
|---|---|
| `pwd` | onde estou |
| `ls` | lista arquivos |
| `ls -la` | lista tudo, inclusive ocultos (`.env`, `.git`) |
| `ls -lt` | ordena por data, mais recente primeiro |
| `cd pasta` | entra na pasta |
| `cd ..` | sobe um nível |
| `cd ~` | vai para a home (`/home/bfper`) |
| `cd -` | volta para a pasta anterior |
| `tree -L 2` | estrutura em árvore, 2 níveis (`sudo apt install tree`) |

**Atalhos que economizam muito tempo:**

- `Tab` — completa nome de arquivo ou pasta. Use sempre.
- `Ctrl+C` — interrompe o comando que está rodando
- `Ctrl+L` — limpa a tela
- `Ctrl+R` — busca em comandos anteriores (digite parte do comando)
- `↑` / `↓` — navega no histórico
- `Ctrl+A` / `Ctrl+E` — início / fim da linha

### Mapa de pastas

```
~/lab/qa-lab/      o repositório (é daqui que você trabalha)
~/lab/src/         clones do mentoria e auth-service
/mnt/c/            disco C: do Windows
/mnt/c/Users/SEU_USUARIO/Downloads/    seus downloads
/mnt/d/            pendrive, quando montado
```

**Regra:** caminho começando com `/mnt/` é Windows. Bom para buscar
arquivo, ruim para trabalhar.

Montar o pendrive (some a cada reinício):

```bash
sudo mount -t drvfs D: /mnt/d
```

---

## 3. Arquivos

| Comando | O que faz |
|---|---|
| `cat arquivo` | mostra o conteúdo inteiro |
| `head -20 arquivo` | primeiras 20 linhas |
| `tail -20 arquivo` | últimas 20 linhas |
| `less arquivo` | abre para leitura (`q` sai, `/` busca) |
| `cp origem destino` | copia |
| `mv origem destino` | move ou renomeia |
| `rm arquivo` | apaga (**não tem lixeira**) |
| `rm -rf pasta` | apaga pasta e conteúdo — cuidado |
| `mkdir -p a/b/c` | cria pastas aninhadas |

Caminho com espaço ou parêntese precisa de aspas:

```bash
cp "/mnt/c/Users/bfper/Downloads/conftest (1).py" tests/unit/conftest.py
```

### Buscar

```bash
grep -rn "check_scope" .                      # busca recursiva com número de linha
grep -rn --include='*.py' "email" ~/lab/src   # só em arquivos .py
grep -c "padrão" arquivo                      # conta ocorrências
find . -name "*.py"                           # acha por nome
```

---

## 4. VS Code

```bash
code .              # abre a pasta atual
code arquivo.py     # abre um arquivo
```

**Sempre pelo terminal do Ubuntu.** Se abrir pelo Explorer do Windows, ele
roda do lado errado e o terminal integrado vira PowerShell.

Confirme no canto inferior esquerdo: tem que dizer `WSL: Ubuntu-24.04`.

| Atalho | O que faz |
|---|---|
| `Ctrl+P` | abre arquivo por nome |
| `Ctrl+G` | vai para linha |
| `Ctrl+S` | salva |
| `Ctrl+F` | busca no arquivo |
| `Ctrl+Shift+F` | busca em todo o projeto |
| `Ctrl+J` | abre/fecha o terminal |
| `Ctrl+Shift+P` | paleta de comandos |
| `Ctrl+/` | comenta a linha |

---

## 5. Python e pytest

```bash
source .venv/bin/activate     # ativa o ambiente
deactivate                    # desativa
pip install -r requirements.txt
pip list                      # o que está instalado
```

### Rodar testes

```bash
pytest                                  # tudo
pytest tests/unit                       # só uma pasta
pytest tests/unit/test_scope.py         # só um arquivo
pytest -k "viewer"                      # só testes com "viewer" no nome
pytest -m unit                          # só os marcados com @pytest.mark.unit
```

### Enxergar melhor

```bash
pytest -q                     # saída curta
pytest -v                     # nome de cada teste
pytest -x                     # para no primeiro erro
pytest --lf                   # só os que falharam da última vez
pytest --tb=line              # traceback de uma linha por falha
pytest --tb=no -q             # só o placar, sem traceback
pytest -s                     # mostra print() e input()
pytest --collect-only         # lista os testes sem rodar
```

> Quando a saída vier gigante, comece por `pytest --tb=no -q`. Você vê o
> panorama primeiro e escolhe onde entrar.

### Reproduzir uma ordem específica

O `pytest-randomly` embaralha a ordem de propósito — dependência de ordem é
bug. Para reproduzir uma falha:

```bash
pytest -p no:randomly              # desliga o embaralhamento
pytest --randomly-seed=155284794   # repete uma ordem específica
```

---

## 6. Make (atalhos do lab)

```bash
make help     # lista tudo
make unit     # semana 1 — testes de escopo
make up       # sobe auth + mentoria + postgres
make down     # para, mantém dados
make nuke     # para e destrói o volume
make logs     # acompanha os logs
make e2e      # semanas 2-3
make api      # semana 5
make data     # semana 6
make all      # suíte completa, como o CI roda
make flaky    # cinco execuções seguidas
```

---

## 7. Git

### Dia a dia

```bash
git status                    # o que mudou
git status -uall --short      # versão compacta, arquivo por arquivo
git diff                      # o que mudou, linha a linha
git diff --cached             # o que já está no stage
git add -A                    # adiciona tudo
git add arquivo.py            # adiciona um arquivo
git commit -m "mensagem"      # commita
git push                      # envia
git log --oneline -10         # últimos 10 commits
```

### Branch e PR

```bash
git checkout -b feat/scope-tests      # cria e entra no branch
git checkout main                     # volta
git branch                            # lista
git push -u origin feat/scope-tests   # primeiro push do branch
```

O PR é aberto no GitHub, pelo site.

### Desfazer

| Situação | Comando |
|---|---|
| Tirar do stage | `git restore --staged arquivo` |
| Descartar alteração não commitada | `git restore arquivo` |
| Desfazer o último commit, manter alterações | `git reset --soft HEAD~1` |
| Desfazer o último commit e as alterações | `git reset --hard HEAD~1` |
| Desfazer commit já enviado | `git revert <hash>` |

> `reset --hard` apaga trabalho sem volta. `revert` é o certo para commit
> que já foi para o GitHub.

### Hook do lab

```bash
./scripts/install-hooks.sh    # (re)instala o pre-commit
git commit --no-verify -m "x" # ignora o hook — só se tiver certeza
```

---

## 8. Docker

```bash
docker ps                     # containers rodando
docker ps -a                  # inclui os parados
docker images                 # imagens baixadas
docker logs -f qalab-mentoria # acompanha o log de um container
docker exec -it qalab-mentoria bash   # entra no container
docker system prune -a        # libera espaço (apaga o não usado)
docker system df              # quanto está ocupando
```

Com o compose do lab, prefira os alvos do `make` — eles já apontam para o
arquivo e o `.env` certos.

---

## 9. Banco de dados local

```bash
psql -h localhost -p 15432 -U qalab -d mentoria
```

Dentro do `psql`:

| Comando | O que faz |
|---|---|
| `\dt` | lista tabelas |
| `\d mentorando` | descreve a tabela |
| `\l` | lista bancos |
| `\q` | sai |

Uma consulta direto do terminal:

```bash
psql -h localhost -p 15432 -U qalab -d mentoria -c "SELECT id, nome, email FROM mentorando LIMIT 5;"
```

---

## 10. Sistema

```bash
sudo apt update && sudo apt upgrade -y    # atualiza tudo
sudo apt install -y nome-do-pacote        # instala
df -h                                     # espaço em disco
free -h                                   # memória
htop                                      # processos (sudo apt install htop)
```

No PowerShell:

```powershell
wsl -l -v                    # lista distribuições e estado
wsl --shutdown               # desliga o WSL
wsl -d Ubuntu-24.04          # abre
```

---

## 11. Quando der problema

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `pytest: command not found` | venv não ativado | `source .venv/bin/activate` |
| `make: command not found` | pacote ausente | `sudo apt install -y make` |
| `docker: permission denied` | integração WSL desligada | Docker Desktop → Settings → Resources → WSL Integration → Apply & Restart |
| `/mnt/d` vazio | pendrive desmontou | `sudo mount -t drvfs D: /mnt/d` |
| VS Code sem `WSL:` no canto | abriu pelo Explorer | fecha e usa `code .` no Ubuntu |
| `dubious ownership` no git | repo em disco do Windows | `git config --global --add safe.directory '/caminho/.git'` |
| `ModuleNotFoundError` do app | `.env` apontando errado | `ls $(grep MENTORIA_SRC .env \| cut -d= -f2)` |
| Disco cheio | imagens Docker acumuladas | `docker system prune -a` e `make nuke` |

### Ler erro de Python

O traceback é longo, mas **a informação está nas últimas linhas**. Leia de
baixo para cima: a última linha diz o que aconteceu, e a penúltima diz onde.
O meio é a pilha de chamadas do pytest, quase sempre irrelevante.

---

## 12. Rotina sugerida

**Abrir:**

```bash
lab          # ou: cd ~/lab/qa-lab && source .venv/bin/activate
code .
git status   # confere se ficou algo pendente da última vez
```

**Trabalhar:** um teste por vez → `pytest tests/unit -k "nome"` → verde →
commit pequeno em inglês.

**Fechar:**

```bash
git status       # nada pendente?
git push
make nuke        # se tiver usado containers
```
