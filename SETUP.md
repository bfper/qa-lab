# SETUP — do zero até o primeiro teste rodando

Guia para o **PC pessoal, Windows + WSL2**. Cada etapa termina com uma
verificação: se ela falhar, pare ali e resolva antes de seguir. Descobrir na
etapa 9 que a 3 não funcionou custa a noite inteira.

Tempo estimado: 60 a 90 minutos, a maior parte esperando download.

---

## Etapa 0 — Reconhecimento (5 min)

Antes de instalar qualquer coisa, três checagens.

**Versão do Windows.** `Win+R`, digite `winver`.

- **Windows 11** — segue direto, tudo funciona.
- **Windows 10** — precisa ser build **19044 ou superior**. Se for menor,
  rode o Windows Update antes de qualquer coisa.

**Virtualização.** `Ctrl+Shift+Esc` → Desempenho → CPU. Procure
"Virtualização: Habilitado".

Se estiver desabilitado: reinicie na BIOS (geralmente `Del`, `F2` ou `F10`
no boot) e ative **Intel VT-x** ou **AMD-V** / **SVM Mode**.

**Espaço em C:.** Precisa de pelo menos **20 GB livres**. O lab consome de
10 a 13 GB e o Windows fica instável com o disco quase cheio.

> ✅ **Verificação:** Windows 11 (ou 10 build 19044+), virtualização
> habilitada, 20 GB livres.

---

## Etapa 1 — WSL2 e Ubuntu (15 min)

Abra o **PowerShell como administrador** (botão direito no menu Iniciar →
Terminal (Administrador)).

```powershell
wsl --install -d Ubuntu-24.04
```

Isso instala o WSL2, habilita a Plataforma de Máquina Virtual e baixa o
Ubuntu, tudo de uma vez. **Reinicie o PC quando ele pedir.**

Depois do reboot, o Ubuntu abre sozinho e pede usuário e senha. Use um nome
curto e minúsculo (ex: `bernardo`). Essa senha é do Linux, não do Windows, e
você vai usar ela em todo `sudo` — anote.

Se o Ubuntu não abrir sozinho, procure "Ubuntu" no menu Iniciar.

### Se der erro

- **"O componente solicitado não foi encontrado"** ou similar no Windows 10:
  habilite os recursos manualmente e reinicie:

  ```powershell
  dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
  dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
  ```

- **Erro 0x80370102**: virtualização não está ativa. Volte à etapa 0.

> ✅ **Verificação:** no PowerShell, `wsl -l -v` mostra `Ubuntu-24.04`,
> `Running`, **VERSION 2**. Se aparecer VERSION 1:
> `wsl --set-version Ubuntu-24.04 2`

---

## Etapa 2 — Espaço sob controle (2 min)

Só no **Windows 11**. Faz o WSL devolver espaço em disco automaticamente
quando você apaga arquivos — sem isso o disco virtual só cresce.

No PowerShell (admin):

```powershell
wsl --shutdown
wsl --manage Ubuntu-24.04 --set-sparse true
```

Reabra o Ubuntu depois.

> ✅ **Verificação:** o comando retorna sem erro. No Windows 10 essa opção
> não existe — pule, e rode `docker system prune -a` de tempos em tempos.

---

## Etapa 3 — Pacotes base do Ubuntu (10 min)

**Agora você está dentro do Ubuntu**, não mais no PowerShell. O prompt fica
parecido com `bernardo@DESKTOP:~$`.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip git make unzip curl
```

Configuração de fim de linha — evita a classe inteira de bug de CRLF:

```bash
git config --global core.autocrlf input
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
git config --global init.defaultBranch main
```

> ✅ **Verificação:** `python3 --version` (3.12.x) e `git --version` (2.4x)
> respondem sem erro.

---

## Etapa 4 — Docker Desktop (15 min)

Baixe no Windows: <https://www.docker.com/products/docker-desktop/> →
Download for Windows (AMD64). Instale com as opções padrão, mantendo **"Use
WSL 2 instead of Hyper-V"** marcado. Reinicie se pedir.

Depois de abrir o Docker Desktop:

**Settings → General** → confirme *Use the WSL 2 based engine*.

**Settings → Resources → WSL Integration** → ligue o toggle geral e ligue
**Ubuntu-24.04** na lista. → **Apply & Restart**.

> ✅ **Verificação:** **dentro do Ubuntu**, `docker run --rm hello-world`
> imprime a mensagem de boas-vindas. Se der "permission denied" ou "cannot
> connect", a integração WSL não foi aplicada — volte e confira.

---

## Etapa 5 — Estrutura de pastas (2 min)

Dentro do Ubuntu:

```bash
mkdir -p ~/lab/src
cd ~/lab
```

A estrutura final:

```
~/lab/
├── qa-lab/     <- o repositório público (o pacote vai aqui)
└── src/        <- clones do app, FORA do repositório
```

`src/` fica **fora** do `qa-lab` de propósito. Se ficasse dentro, um
`git add -f` distraído mandaria o código do app para um repositório público.

> ⚠️ Os arquivos **precisam** morar dentro do Linux (`~/lab`). Não use
> `/mnt/c` nem `/mnt/d` para o lab — I/O fica lento e permissão quebra.

---

## Etapa 6 — Instalar o pacote qa-lab (5 min)

Copie o `qa-lab.zip` para a pasta de Downloads do Windows, depois, no Ubuntu:

```bash
cd ~/lab
unzip /mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads/qa-lab.zip
cd qa-lab
chmod +x scripts/*.sh docker/postgres/*.sh
```

Troque `SEU_USUARIO_WINDOWS` pelo nome real da sua pasta de usuário. Se não
souber: `ls /mnt/c/Users/`

Crie o ambiente virtual e instale as dependências:

```bash
make setup
source .venv/bin/activate
```

> ✅ **Verificação:** `make help` lista os comandos coloridos. O prompt agora
> começa com `(.venv)`.

---

## Etapa 7 — Copiar os repos do pendrive (5 min)

Com o pendrive espetado, descubra a letra dele no Windows (geralmente `D:`
ou `E:`). No Ubuntu, o pendrive aparece em `/mnt/<letra>`:

```bash
ls /mnt/d/perazzo-cloud
```

Se a pasta não aparecer, monte manualmente:

```bash
sudo mkdir -p /mnt/d && sudo mount -t drvfs D: /mnt/d
```

Clone os dois repos **cortando o remote na sequência**:

```bash
cd ~/lab/src

git clone --depth 1 /mnt/d/perazzo-cloud/mentoria mentoria
cd mentoria && git remote remove origin && cd ..

git clone --depth 1 /mnt/d/perazzo-cloud/auth-service auth-service
cd auth-service && git remote remove origin && cd ..
```

> Ajuste os nomes das pastas conforme o que aparecer no `ls`.

Cinto extra — hook que recusa push em cada cobaia:

```bash
for r in mentoria auth-service; do
  printf '#!/bin/sh\necho "Cobaia do lab. Push bloqueado."\nexit 1\n' \
    > ~/lab/src/$r/.git/hooks/pre-push
  chmod +x ~/lab/src/$r/.git/hooks/pre-push
done
```

> ✅ **Verificação:** `cd ~/lab/src/mentoria && git remote -v` não imprime
> nada. Se imprimir uma URL, o remote não foi removido.

---

## Etapa 8 — Configurar o .env (5 min)

```bash
cd ~/lab/qa-lab
cp .env.example .env
whoami          # anote seu usuário do Linux
nano .env       # ou: code .env
```

Troque `<user>` pelo resultado do `whoami` nas duas linhas de caminho:

```
MENTORIA_SRC=/home/bernardo/lab/src/mentoria
AUTH_SRC=/home/bernardo/lab/src/auth-service
```

Caminhos **absolutos**, sempre. Relativo resolve diferente para o pytest e
para o docker compose — os dois recusam rodar com caminho relativo,
justamente para você não perder uma noite nisso.

No nano: `Ctrl+O`, `Enter`, `Ctrl+X` para salvar e sair.

> ✅ **Verificação:** `ls $(grep MENTORIA_SRC .env | cut -d= -f2)` lista o
> conteúdo do repo mentoria.

---

## Etapa 9 — Git e GitHub (10 min)

O repo é **público desde o primeiro commit**, então a ordem importa: hook
antes de commit, sempre.

```bash
cd ~/lab/qa-lab
git init
./scripts/install-hooks.sh
```

Gere uma chave SSH **nova, só para o GitHub**:

```bash
ssh-keygen -t ed25519 -C "qa-lab"        # Enter em tudo
cat ~/.ssh/id_ed25519.pub
```

Copie a saída e cole em GitHub → Settings → SSH and GPG keys → New SSH key.

> ⚠️ **Não copie a chave da VPS para o WSL.** Ela não tem função no lab, e
> credencial fora de alcance é acidente que não acontece.

Teste e faça o primeiro commit:

```bash
ssh -T git@github.com          # "Hi <user>! You've successfully authenticated"

git status                     # CONFIRA: .env e .venv NÃO podem aparecer
git add -A
git commit -m "chore: bootstrap test lab structure"
```

Crie o repositório `qa-lab` no GitHub (público, sem README) e conecte:

```bash
git remote add origin git@github.com:SEU_USUARIO/qa-lab.git
git push -u origin main
```

> ✅ **Verificação:** o `git status` antes do `add` não listou `.env`. Se
> listou, pare — o `.gitignore` não foi copiado corretamente.

---

## Etapa 10 — VS Code (5 min)

Instale o VS Code no **Windows** (não no Linux):
<https://code.visualstudio.com/>

Depois, no Ubuntu:

```bash
cd ~/lab/qa-lab
code .
```

Na primeira vez ele baixa o servidor e instala a extensão WSL sozinho.

> ✅ **Verificação:** canto inferior esquerdo do VS Code mostra
> `WSL: Ubuntu-24.04`. Se não mostrar, você abriu pelo lado errado — feche e
> use `code .` de dentro do Ubuntu.

Instale a extensão **Python** (Microsoft) e selecione o interpretador:
`Ctrl+Shift+P` → *Python: Select Interpreter* → o que estiver em `.venv`.

---

## Etapa 11 — Prova real (5 min)

Três testes que provam que o lab está de pé e que as travas funcionam.

**A trava de host aborta:**

```bash
BASE_URL=https://mentoria.perazzo.cloud pytest tests/unit
```

Esperado: `ABORTED: BASE_URL contains 'perazzo.cloud'`. Se rodar os testes
normalmente, a trava não está ativa — pare e confira o `conftest.py`.

**A suíte roda:**

```bash
make unit
```

Esperado: vários `NotImplementedError` e alguns `skip`. **Isso é sucesso** —
os casos estão nomeados, as asserções são suas. O que *não* pode aparecer é
`skip: app source not importable`, que significa `.env` apontando errado.

**O hook de commit bloqueia:**

```bash
echo "email: pessoa.real@gmail.com" > /tmp/x.md && cp /tmp/x.md .
git add x.md && git commit -m "test"
```

Esperado: `COMMIT BLOCKED: real-looking email address staged`. Limpe depois:

```bash
git reset HEAD x.md && rm x.md
```

> ✅ **Verificação final:** as três se comportaram como descrito acima.

---

## Pronto. E agora?

O que fica para a semana 1, e **não depende de Docker**:

1. Abrir `tests/unit/test_scope.py`
2. Ler `test_is_gerente` — é a implementação de referência
3. Preencher as asserções, um `raise NotImplementedError` de cada vez
4. Commit pequeno por vez, mensagem em inglês
5. Abrir um PR contra `main` e fazer o merge você mesmo

Docker só entra na semana 2, quando o Playwright precisar da app de pé. O
`make up` está pronto, mas antes disso falta confirmar os nomes reais das
variáveis de ambiente — os dois comandos estão no fim do `README.md`.

---

## Referência rápida

| Situação | Comando |
|---|---|
| Abrir o lab | `cd ~/lab/qa-lab && source .venv/bin/activate` |
| Rodar semana 1 | `make unit` |
| Ver todos os comandos | `make help` |
| Reiniciar o WSL | `wsl --shutdown` (no PowerShell) |
| Liberar espaço | `docker system prune -a` |
| Acessar o Windows | `/mnt/c/...` |
| Abrir no VS Code | `code .` |

### Problemas comuns

**`make: command not found`** — `sudo apt install -y make`

**`docker: permission denied`** — integração WSL não aplicada. Docker
Desktop → Settings → Resources → WSL Integration → Apply & Restart.

**`skip: app source not importable`** — `.env` aponta para pasta errada.
Confira com `ls $(grep MENTORIA_SRC .env | cut -d= -f2)`.

**Pendrive não aparece em `/mnt/d`** —
`sudo mkdir -p /mnt/d && sudo mount -t drvfs D: /mnt/d`

**VS Code abre sem `WSL:` no canto** — você abriu pelo Explorer. Use
`code .` de dentro do Ubuntu.
