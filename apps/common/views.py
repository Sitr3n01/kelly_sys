from django.http import HttpResponse
from django.shortcuts import render


def health_check(request):
    """Liveness probe para Docker/orquestradores.

    Sem dependência de banco de propósito: responde 200 enquanto o processo da
    aplicação estiver de pé (liveness, não readiness). Em produção, a rota é
    isenta do redirect HTTPS via ``SECURE_REDIRECT_EXEMPT`` para que a probe
    interna do container (HTTP, sem proxy) não receba 301.
    """
    return HttpResponse('ok', content_type='text/plain')


def robots_txt(request):
    """robots.txt servido pelo Django, e nao por arquivo estatico.

    Dois motivos para ser view: a linha ``Sitemap:`` precisa do host da request
    — ``komuniki.com.br`` e ``kellyfarias.com.br`` compartilham esta aplicacao e
    um caminho absoluto fixo apontaria o crawler para o dominio errado — e o
    WhiteNoise so serve o que passou pelo ``collectstatic``.

    O ``Disallow: /news/search/`` e o que mais pesa: a busca faz
    ``content__icontains`` (ILIKE '%...%') sobre o corpo dos artigos, sem indice
    possivel, e o Paginator executa a consulta duas vezes.
    """
    return render(request, 'robots.txt', content_type='text/plain')
