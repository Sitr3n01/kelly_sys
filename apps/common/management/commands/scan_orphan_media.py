"""Relatório somente-leitura de arquivos órfãos em MEDIA_ROOT.

Existe porque nenhuma varredura ingênua é segura neste projeto: além dos campos
de arquivo espalhados pelos models, vários campos de texto embutem caminhos
``/media/...`` que **nenhuma chave estrangeira rastreia** — o HTML legado de
``Article.content``, o StreamField ``Article.body`` e o ``school.Page.content``.
Apagar por FK sozinho quebraria imagem de página publicada.

Por isso o comando nunca apaga. Ele classifica:

- ``original_images/`` é onde o Wagtail guarda o ORIGINAL. Remover um arquivo
  de lá que ainda esteja em uso destrói a regeneração de todas as renditions
  daquela imagem, e renditions são justamente o que se costuma purgar para
  liberar espaço. Sempre RISCO ALTO, sempre revisão manual.
- o resto vem com a linha ``rm`` pronta, para conferência e execução manual.

Dotfiles (``.gitkeep``) são marcadores estruturais e ficam fora do relatório.
"""

import os
import re
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import FileField

# Nomes em MEDIA_ROOT são slugificados; classe explícita evita depender de
# escapes que se perdem ao colar o comando em um shell remoto.
CAMINHO_EMBUTIDO = re.compile('/media/([A-Za-z0-9._/-]+)')

ORIGINAIS_WAGTAIL = 'original_images/'

# `get_internal_type()` e nao `isinstance`: o StreamField do Wagtail herda direto de
# `models.Field` — nao de TextField nem de JSONField — mas se declara como JSONField no
# banco. Um `isinstance(f, models.JSONField)` perderia `Article.body`.
TIPOS_DE_TEXTO = {'TextField', 'JSONField'}


class Command(BaseCommand):
    help = 'Relata arquivos em MEDIA_ROOT sem referência no banco. Nunca apaga nada.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int, default=50,
            help='Quantos órfãos listar. Default: 50.',
        )

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.is_dir():
            self.stderr.write(self.style.ERROR(f'MEDIA_ROOT não existe: {media_root}'))
            return

        referenciados, campos = self._referenciados_por_campo()
        embutidos, campos_de_texto = self._referenciados_em_texto(referenciados)

        em_disco = {
            str(p.relative_to(media_root)).replace(os.sep, '/')
            for p in media_root.rglob('*') if p.is_file()
        }
        orfaos = sorted(
            caminho for caminho in (em_disco - referenciados)
            if not any(parte.startswith('.') for parte in caminho.split('/'))
        )
        risco_alto = [o for o in orfaos if o.startswith(ORIGINAIS_WAGTAIL)]
        seguros = [o for o in orfaos if o not in risco_alto]
        megabytes = sum((media_root / o).stat().st_size for o in orfaos) / 1048576

        self.stdout.write(f'MEDIA_ROOT: {media_root}')
        self.stdout.write(f'Campos de arquivo varridos: {len(campos)}')
        self.stdout.write(f'Campos de texto varridos: {campos_de_texto}')
        self.stdout.write(f'Referências embutidas em texto: {embutidos}')
        self.stdout.write('')
        self.stdout.write(f'Arquivos em disco: {len(em_disco)}')
        self.stdout.write(f'Referenciados:     {len(referenciados & em_disco)}')
        self.stdout.write(f'Órfãos:            {len(orfaos)} ({megabytes:.1f} MB)')

        if risco_alto:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                f'{len(risco_alto)} órfão(s) em {ORIGINAIS_WAGTAIL} — originais do Wagtail. '
                'Confira um a um; são a fonte de todas as renditions.'
            ))
            for caminho in risco_alto[:options['limit']]:
                self.stdout.write(f'  RISCO ALTO  {caminho}')

        if seguros:
            self.stdout.write('')
            self.stdout.write('Órfãos de baixo risco — confira e remova à mão:')
            for caminho in seguros[:options['limit']]:
                self.stdout.write(f"  rm '{media_root / caminho}'")

        if not orfaos:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Nenhum órfão: todo arquivo em disco tem referência.'))

    def _referenciados_por_campo(self):
        """Todo valor de todo FileField/ImageField de todo model instalado."""
        referenciados = set()
        campos_vistos = []
        for model in apps.get_models():
            campos = [f.name for f in model._meta.get_fields() if isinstance(f, FileField)]
            if not campos:
                continue
            campos_vistos.append(f'{model._meta.label}: {",".join(campos)}')
            for linha in model._default_manager.values_list(*campos):
                if not isinstance(linha, tuple):
                    linha = (linha,)
                for valor in linha:
                    if valor:
                        referenciados.add(str(valor).replace(os.sep, '/'))
        return referenciados, campos_vistos

    def _referenciados_em_texto(self, referenciados):
        """Caminhos ``/media/...`` embutidos em texto, que nenhuma FK rastreia.

        Varre TODO campo de texto de TODO model. A primeira versão deste comando
        olhava apenas ``Article.content`` e ``Article.body``, e por isso reportava
        como órfã uma imagem citada em ``school.Page.content`` — que é TextField com
        HTML sanitizado, exatamente o mesmo caso do ``content`` legado do artigo.

        Deliberadamente abrangente: uma referência a mais só faz deixar de reportar
        um órfão, enquanto uma a menos manda apagar arquivo em uso. Por isso entram
        também os snapshots de ``wagtailcore.Revision.content`` — a imagem de uma
        revisão restaurável ainda está em uso.
        """
        total = 0
        campos_varridos = 0
        for model in apps.get_models():
            if model._meta.proxy:
                continue
            campos = [
                f.name for f in model._meta.concrete_fields
                if f.get_internal_type() in TIPOS_DE_TEXTO
            ]
            if not campos:
                continue
            campos_varridos += len(campos)
            linhas = model._default_manager.values_list(*campos).iterator(chunk_size=200)
            for linha in linhas:
                if not isinstance(linha, tuple):
                    linha = (linha,)
                for valor in linha:
                    if not valor:
                        continue
                    for achado in CAMINHO_EMBUTIDO.findall(str(valor)):
                        referenciados.add(achado)
                        total += 1
        return total, campos_varridos
