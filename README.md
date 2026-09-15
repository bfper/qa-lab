# qa-lab

Repositório de testes do **MP Mentoria**. Construído durante a Fase B da
Rota v2 (15/09 → 09/11) como portfólio de Software Quality Engineer.

> Este README está em português porque é documento de trabalho. Na semana 7
> ele é reescrito em inglês, contando a história do pipeline — é o item que
> pesa mais em triagem de recrutador estrangeiro.

## Setup — WSL2

Os arquivos precisam morar **dentro** do sistema de arquivos do Linux
(`~/qa-lab`). Se ficarem em `/mnt/c` ou `/mnt/d`, você perde velocidade de
I/O e ganha problema de permissão.

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip git make
git config --global core.autocrlf input

mkdir -p ~/lab/src && cd ~/lab
# copie o conteúdo deste pacote para ~/lab/qa-lab

cd ~/lab/qa-lab
make setup
source .venv/bin/activate
```

No Docker Desktop: Settings → Resources → WSL Integration, habilitar para
Ubuntu-24.04.

### Estrutura

```
~/lab/
├── qa-lab/          <- ESTE repositório. É o que vai para o GitHub.
│   ├── .venv/
│   ├── conftest.py  <- trava de host
│   ├── tests/
│   ├── docker/
│   └── .env         <- aponta para ../src (absoluto)
└── src/             <- FORA do repositório, de propósito
    ├── mentoria/
    └── auth-service/
```

`src/` é irmão de `qa-lab`, não filho. Se ficasse dentro, bastaria um
`git add -f` distraído para o código do app — e o histórico dele — entrar no
repositório público. Pasta separada torna o acidente impossível em vez de
improvável.

`~/lab/qa-lab` é onde você roda tudo: `make`, `pytest`, `git`.

### O app sob teste

Clone **sem remote**, dentro de `~/lab/src`:

```bash
cd ~/lab/src
git clone --depth 1 <caminho-do-repo-mentoria> mentoria
cd mentoria && git remote remove origin

cd ~/lab/src
git clone --depth 1 <caminho-do-repo-auth> auth-service
cd auth-service && git remote remove origin
```

Um cinto extra em cada clone:

```bash
printf '#!/bin/sh\necho "Cobaia do lab. Push bloqueado."\nexit 1\n' > .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

Depois aponte o `.env` com caminho **absoluto**:

```
MENTORIA_SRC=/home/<user>/lab/src/mentoria
AUTH_SRC=/home/<user>/lab/src/auth-service
```

Caminho relativo resolve diferente para o pytest (relativo ao repo) e para o
docker compose (relativo a `docker/`). Os dois recusam rodar com caminho
relativo, justamente para você não perder uma noite nisso.

O repositório `qa-lab` em si é o oposto: **tem** remote no GitHub, é público,
e é onde o badge verde vive.

## Comandos

```
make help     lista tudo
make unit     semana 1 — regras de escopo, sem container
make up       sobe auth + mentoria + postgres
make down     para, mantém dados
make nuke     para e destrói o volume
make e2e      semanas 2-3
make api      semana 5
make data     semana 6
make all      suíte completa, como o CI roda
make flaky    cinco execuções seguidas
```

## Isolamento

Quatro camadas, e nenhuma delas confia nas outras:

1. **`conftest.py` da raiz** aborta a sessão se `BASE_URL`, `AUTH_BASE_URL`,
   `POSTGRES_HOST` ou `DATABASE_URL` apontarem para fora de `localhost`, ou
   contiverem `perazzo.cloud`.
2. **Compose** usa portas altas (15432 / 18001 / 18002), presas a
   `127.0.0.1`, com rede e volume próprios. Nenhum recurso `external`.
3. **Clones sem remote** com `pre-push` que recusa.
4. **Anonimização obrigatória** em todo restore de dump. O `.gitignore`
   bloqueia `*.dump` e `dumps/`.

Testar que a trava funciona (deve abortar):

```bash
BASE_URL=https://mentoria.perazzo.cloud pytest tests/unit
```

## Roteiro

| Semana | Foco | Entregável |
|---|---|---|
| 1 | pytest + Git | ≥6 testes de `check_scope`, um PR mergeado |
| 2 | Playwright nível 0 | 3 E2E de login, zero `wait_for_timeout` |
| 3 | Playwright nível 1 | `storage_state`, fixtures por API, POM |
| 4 | CI/CD | pipeline verde, badge, trace na falha |
| 5 | API | Postman + Newman, 3 bordas por endpoint |
| 6 | SQL + Docker | 3 oráculos de dados, stack em um comando |
| 7 | Buffer + README | README em inglês, pirâmide de testes |
| 8 | Checkpoint | 10 execuções estáveis, lista de bugs reais |

## O que falta confirmar

Três pontos ficaram em aberto e travam a semana 2, não a 1:

1. **Como o mentoria descobre o auth.** Se for URL fixa no código em vez de
   variável de ambiente, o container do lab tenta falar com a VPS.

   ```bash
   docker exec mentoria-app sh -c "grep -rn --include='*.py' -iE 'auth.*perazzo|AUTH_URL|AUTH_BASE' /code | grep -v site-packages"
   ```

2. **Nome real das variáveis de ambiente** dos dois serviços — o compose usa
   `DATABASE_URL`, `AUTH_BASE_URL` e `JWT_SECRET` como palpite.

   ```bash
   docker inspect mentoria-app --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -iv -E 'secret|key|password|token'
   ```

3. **Colunas reais de `mentorando`**, para o `scripts/anonymize.sql`.

### CI e o app sob teste

O workflow da semana 4 precisa do código do app, que não está versionado
aqui. Duas saídas, ambas defensáveis — a decisão é sua e vira parágrafo do
README em inglês:

- segundo `checkout` do repo privado com token de acesso
- publicar imagem do app num registry e o CI só puxar

## Bug candidato, antes do primeiro teste

`get_proprio_mentorando()` normaliza o e-mail **do login** (`strip().lower()`)
mas compara com o e-mail **armazenado** como está. Se algum `Mentorando` foi
cadastrado com maiúscula ou espaço sobrando, a busca falha e um usuário
legítimo recebe 404 "Cadastro pendente — fale com a mentora".

Confirmar no banco real se o cadastro normaliza na escrita. Se não
normalizar, é item 1 da lista de bugs da semana 8 — e a correção provável é
`func.lower(Mentorando.email) == email`.

Os casos já estão nomeados em `tests/unit/test_scope.py`, marcados
`SUSPECTED_BUG`.
