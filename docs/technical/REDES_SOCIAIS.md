# Redes Sociais (Instagram + TikTok)

App `apps.social`. A home da Komuniki exibe uma seção curta de redes sociais com botão oficial do Instagram e posts recentes como cards próprios salvos no banco. O TikTok permanece no backend para contas, posts e sincronização, mas o botão público do TikTok não aparece na home.

## Visão Geral

A seção tem duas fontes de conteúdo:

1. **Gestão manual no admin:** posts cadastrados à mão em **Posts de Redes Sociais**.
2. **Sincronização automática:** APIs oficiais de Instagram e TikTok via `python manage.py sync_social_posts`.

Os posts são renderizados por `templates/components/social_feed.html` e `templates/components/social_post_card.html`. A home não usa scraping nem iframes pesados para o feed; se a API falhar, continua usando os dados já salvos.

## Modelos

| Modelo | Papel |
|--------|-------|
| `SocialAccount` | Perfil oficial Instagram/TikTok de um `Site`. Guarda link público, credenciais opcionais, status de sync e `on_site`. |
| `SocialPost` | Publicação manual ou sincronizada. Único por `(platform, external_id)`, com miniatura por upload ou URL. |

`SiteExtension` controla:

- `tiktok_url`;
- `social_section_enabled`;
- `social_show_instagram`;
- `social_show_tiktok`;
- `social_section_title` / `_en`;
- `social_section_subtitle` / `_en`.

Os toggles principais são editados no topo de **Posts de Redes Sociais**.

## Como Configurar no Admin

1. Em **Contas de Redes Sociais**, crie uma conta ativa para Instagram ou TikTok.
2. Informe nome de exibição, usuário público e link do perfil.
3. Em **Posts de Redes Sociais**, use os toggles do topo para ligar/desligar a seção, Instagram e TikTok.
4. Para uso manual, adicione posts com permalink, data de publicação, legenda e miniatura.
5. Para sincronização automática, preencha credenciais e rode `sync_social_posts`.

A home mostra até 6 posts visíveis de contas ativas, do mais recente para o mais antigo; no mobile, mostra os 3 primeiros.

## Comando

```bash
python manage.py sync_social_posts
```

| Argumento | Efeito |
|-----------|--------|
| `--platform instagram\|tiktok` | Sincroniza só uma plataforma |
| `--account-id <ID>` | Sincroniza só uma conta |
| `--limit <n>` | Quantidade buscada por conta, padrão 6 |
| `--dry-run` | Mostra o que faria sem gravar |
| `--verbose` | Loga cada post processado |

Comportamento esperado:

- sincroniza contas ativas;
- faz upsert por `(platform, external_id)`;
- preserva `is_visible` e `is_manual` de posts existentes;
- nunca apaga posts antigos;
- falha de uma conta não derruba as demais;
- atualiza `last_sync_at`, `last_sync_status` e `last_sync_error`.

## Cron Sugerido

```cron
0 */2 * * * flock -n /var/lock/kellysys-social.lock docker compose -p kellysys -f /opt/kelly_sys/docker/docker-compose.prod.yml run --rm --no-deps web python manage.py sync_social_posts 2>&1 | logger -t kellysys-social
```

Leia a saída com:

```bash
journalctl -t kellysys-social -n 50 --no-pager
```

Mudou em relação à versão anterior, e cada mudança tem motivo:

- **`run --rm --no-deps` em vez de `exec -T`** — com `exec`, o `manage.py` sobe um
  Django+Wagtail inteiro dentro do container `web`, disputando o teto de 1500M com
  os workers do Gunicorn. Ver [DEPLOY.md](DEPLOY.md) §7.
- **`| logger` em vez de `>> /var/log/social_sync.log`** — o arquivo antigo não tinha
  rotação e crescia sem limite; o `journalctl --vacuum-time=14d` do
  `kellysys-maintenance` não alcança arquivo solto. Ao migrar, remova o resíduo:
  `sudo rm -f /var/log/social_sync.log`.
- **`0 */2` em vez de `*/30`** — as APIs mudam pouco em 30 minutos e a sincronia
  passou a custar um container por execução.
- **`flock`** — impede empilhar execuções quando uma API está lenta.

## Segurança

- Sem scraping: use apenas APIs oficiais.
- Tokens nunca vão para templates, JavaScript ou repositório.
- Campos de token no admin são password-like.
- Chamadas HTTP têm timeout em `apps/social/services/base.py`.
- Links externos usam `target="_blank"` e `rel="noopener noreferrer"`.

## Limitação Conhecida

URLs de miniatura do Instagram podem expirar. O cron renova periodicamente; para posts importantes, prefira upload manual em `thumbnail_image`.
