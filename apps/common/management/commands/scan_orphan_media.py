"""Relatório somente-leitura de arquivos órfãos em MEDIA_ROOT.

Existe porque nenhuma varredura ingênua é segura neste projeto: além dos 17
campos de arquivo espalhados pelos models, o HTML legado de ``Article.content``
e o JSON de ``Article.body`` embutem caminhos ``/media/...`` que **nenhuma
chave estrangeira rastreia**. Apagar por FK sozinho quebraria imagem de artigo
publicado.

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
        embutidos = self._referenciados_em_texto(referenciados)

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
        self.stdout.write(f'Referências embutidas em content/body: {embutidos}')
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
        """Caminhos embutidos no HTML legado e no StreamField, que não têm FK."""
        article = apps.get_model('news', 'Article')
        total = 0
        for content, body in article.objects.values_list('content', 'body'):
            for campo in (content, body):
                if not campo:
                    continue
                for achado in CAMINHO_EMBUTIDO.findall(str(campo)):
                    referenciados.add(achado)
                    total += 1
        return total
