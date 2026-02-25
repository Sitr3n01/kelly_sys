# Relatório de Correções de Segurança (Pre-Deploy VPS)

Este documento lista todas as vulnerabilidades encontradas no plano original de deploy e as correções já aplicadas neste repositório visando endurecimento de segurança:

## 1. Prevenção contra Auto-DoS pelo Django-Axes (Atrás do Nginx/Docker)
**Problema Original:** Quando publicado atrás de um reverse proxy como Nginx num container Docker, todos os usuários compartilham temporariamente o IP que o Django enxerga (o IP da rede interna Docker `172.x.x.x`). Se um único bot esgotar as tentativas de login, toda a plataforma ficaria bloqueada.
**Correção Aplicada:** 
No `config/settings/base.py`, foram adicionadas as chaves:
- `AXES_PROXY_COUNT = 1`
- `AXES_META_PRECEDENCE_ORDER = ['HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']`
**Por que:** Garante que o Axis olhe o cabeçalho passado pelo Nginx com o IP real do cliente, e não o IP do proxy, bloqueando cirurgicamente apenas o IP ofensor.

## 2. Bloqueio de Uploads Maliciosos na Candidatura (MIME Spoofing)
**Problema Original:** Validação de currículos inspecionava apenas o cabeçalho `content_type`. Um atacante poderia enviar malwares disfarçando o Content-Type como PDF através do Burp Suite e realizar um upload de arquivo intrinsecamente perigoso.
**Correção Aplicada:** 
Na `apps/hiring/forms.py` (método `clean_resume`), incluímos a verificação estrita da extensão do arquivo na submissão, processando com `os.path.splitext()` e limitando forçosamente às extensões `.pdf`, `.doc` e `.docx`.

## 3. Alta Perfomance contra Auto-DoS com Bleach (Sanitização XSS)
**Problema Original:** Fazer o parse completo e substituição de XSS usando a biblioteca Bleach é algo custoso em CPU. Colocar isso na leitura e renderização da página (através de um template filter, renderização n vezes) iria sobrecarregar o container num pico de acesso.
**Correção Aplicada:** 
Aplicamos o método `.clean()` do `bleach` num *override* no método `save()` do modelo `Article` (`apps/news/models.py`).
**Por que:** O esforço computacional se concentra na *escrita* (uma vez), permitindo que na leitura continue sendo rápido usando a tag nativa `|safe` no template com a certeza de que a sujeira nem entrou no banco de dados.

## 4. Segurança de Redirecionamento Dinâmico sem Perda de UX (Open Redirect)
**Problema Original:** Submeter links diretos a views de utilidade (`newsletter_subscribe`, `toggle_like`) permitiria que hackers trocassem o cabeçalho HTTP Referer usando-as para phishing. Se apenas excluíssemos por completo o *referer* (usando hardcode na página detail do content), a usabilidade ao acessar essas features de listagens gerais acabaria quebrada (voltando para a página errada).
**Correção Aplicada:** 
Nas views da app `news`, substituímos o fallback cego a Referer por um envelope `safe_referer_redirect`, que utiliza a função `url_has_allowed_host_and_scheme(url=referer, allowed_hosts={request.get_host()})` nativa do Django. 
**Por que:** O sistema continua aproveitando redirecionamento estático útil mantendo a validação para que domínios externos à `ALLOWED_HOSTS` não funcionem.

## 5. Prevenção de Storage Exhaustion (Hiring App)
**Problema Original:** Um atacante poderia criar um bot para enviar 10.000 inscrições contendo PDFs gigantes para a mesma vaga repetidamente, preenchendo rapidamente os discos da VPS (ex: 5MB * 10k = 50GB) ou a franquia de emails no painel do provedor de mensageria (exaustão ou "Denial of Wallet").
**Correção Aplicada:** Validamos na view do app `Hiring` se o email inserido pelo candidato na vaga já tem status de submissão na base para o Job especificado, rejeitando candidaturas duplicadas logo na camada do Form, antes de aceitar o payload para o File System ou de mandar e-mails.

## 6. Prevenção de Mailbomb (Accounts App)
**Problema Original:** A classe de usuário base (`CustomUserCreationForm`) não forçava um e-mail único. Um hacker de "psicologia reversa" faria o registro de 500 contas falsas com o **seu** e-mail (da vítima), e na sequência pediria um único "Reset Password". O Django, por padrão enviaria de uma vez só 500 caixas de e-mail seguidas à vítima. Isso configuraria o domínio da Kelly Sys em Spamhaus e estouraria limites da API.
**Correção Aplicada:** Sobrescrita da model form inserindo um validador `clean_email()` forçando absoluta unicidade nos e-mails do banco antes de se completarem no registro.

## 7. PostgreSQL Contention DoS (Exibição de Notícia)
**Problema Original:** Todo "F5" dado no detalhe da notícia (ou hit no HTMX) disparava perigosamente no banco um row lock através do `UPDATE` para incrementar a métrica `view_count = view_count + 1`. Por esse endpoint não possuir Rate Limite pesado e ser uma operação transacional de escrita, um hacker genérico de botequim com a ferramenta `wrk` derrubaria as conexões do banco de dados (PG Pool starvation) em menos de 10 segundos, tirando a Kelly Sys inteira do ar.
**Correção Aplicada:** Inserimos o limitador baseado na **sessão** do usuário entre o Banco/View cacheando o estado: Um IP = Um registro em request explícito; requisições repetitivas servem a página num estalar de dedos em memória sem incomodar o disco, a mesma base usada nas melhores arquiteturas de News System.

## 8. Slow-Query DoS (Pesquisa)
**Problema Original:** Os inputs da busca da lupa permitiam queries com espaços ou tamanho irrisório de busca. Como há mapeamento transversal no ORM (`tags`, `content`, `titulos`, etc), o pesquisar de letras minúsculas (e.g. `%a%`), provocava um "Spin Cycle" colossal pelo banco mapeando centenas de combinações em tabelas que não possuem o indíce pra isso, forçando o CPU de Produção para 100%.
**Correção Aplicada:** Rejeição silenciosa e corte via `.strip()` e requerimento severo de busca `len(query) >= 3` imposto aos visitantes.

## 9. Host Header Poisoning & Rate Limiting (Redefinição de Senha)
**Problema Original:** A classe nativa `PasswordResetView` do Django pega o domínio para o link de reset a partir do cabeçalho HTTP de quem faz a requisição. Um invasor poderia falsificar `Host: evil.com` forçando a emissão de emails com links maliciosos para usuários verdadeiros e, em paralelo, atacar a vítima submetendo o input freneticamente (Mailbombing Inbox DoS).
**Correção Aplicada:** Adicionamos a visualização customizada `CustomPasswordResetView`. Usando O ORM `Site` atrelamos `domain_override=site.domain` de forma rígida ao banco de dados bloqueando tentativas de Host Poisoning, além de implantarmos o cache nativo bloqueando múltiplos envios para a mesma conta no prazo de 15 minutos na triagem de envio.
