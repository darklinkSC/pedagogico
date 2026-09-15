from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from datetime import date

from geral.models import Pessoa, STATUS_ATIVO
from pedagogico.models import (
    Turma,
    Matricula,
    AcompanhamentoPedagogicoAluno,
    TipoOcorrencia,
    SessaoParecerTurma,
    ItemParecerAluno
)
from pedagogico.app.formsParecerTurma import SessaoParecerTurmaForm


# 1. LISTAGEM DOS PARECERES
@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def listagemPareceres(request):
    sessoes = SessaoParecerTurma.objects.exclude(status='E').select_related('turma', 'periodoConselho', 'responsavel').order_by('-ano', '-dataRegistro', '-id')

    ano_filtro = request.GET.get('ano')
    turma_filtro = request.GET.get('turma')
    if ano_filtro:
        sessoes = sessoes.filter(ano=ano_filtro)
    if turma_filtro:
        sessoes = sessoes.filter(turma__nome__icontains=turma_filtro)

    paginas = Paginator(sessoes, 15)
    page = request.GET.get('page')
    lista = paginas.get_page(page)

    return render(request, "pareceres/listagemPareceres.html", {
        'lista': lista,
        'ano_filtro': ano_filtro,
        'turma_filtro': turma_filtro
    })


# 2. CRIAR NOVA SESSÃO DE PARECER
@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def criarSessaoParecer(request):
    form = SessaoParecerTurmaForm(request.POST or None, initial={'ano': date.today().year, 'dataRegistro': date.today()})
    if request.method == 'POST' and form.is_valid():
        user = request.user
        responsavel = get_object_or_404(Pessoa, user=user)
        sessao = form.save(commit=False)
        sessao.responsavel = responsavel
        sessao.save()
        messages.success(request, f"Lançamento de Pareceres #{sessao.id} iniciado!")
        return redirect('pedagogico:painelParecerTurma', id=sessao.id)

    return render(request, "pareceres/criarSessaoParecer.html", {'form': form})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def painelParecerTurma(request, id):
    sessao = get_object_or_404(SessaoParecerTurma.objects.select_related('turma', 'periodoConselho'), id=id)
    turma = sessao.turma
    curso = turma.curso

    matriculas = Matricula.objects.filter(
        unidadeCurricular__curso=curso,
        periodo=turma.periodo,
        status=STATUS_ATIVO
    ).select_related('aluno').order_by('aluno__nome')

    alunos_map = {}
    for m in matriculas:
        if m.aluno_id not in alunos_map:
            alunos_map[m.aluno_id] = m.aluno
    lista_alunos = list(alunos_map.values())

    pareceres_existentes = {
        item.aluno_id: item.parecer
        for item in ItemParecerAluno.objects.filter(sessao=sessao)
    }

    # Mapeia o parecer e o acompanhamento gerado para cada aluno
    itens_parecer = {
        item.aluno_id: item
        for item in ItemParecerAluno.objects.filter(sessao=sessao).select_related('acompanhamentoGerado')
    }

    atestados = AcompanhamentoPedagogicoAluno.objects.filter(
        dataAtestadoInicio__year=sessao.ano,
        aluno_id__in=alunos_map.keys()
    ).order_by('dataAtestadoInicio')

    atestados_por_aluno = {}
    for a in atestados:
        atestados_por_aluno.setdefault(a.aluno_id, []).append(a)

    dados_alunos = []
    for aluno in lista_alunos:
        item = itens_parecer.get(aluno.id)
        dados_alunos.append({
            'aluno': aluno,
            'parecer': item.parecer if item else '',
            'acompanhamento_id': item.acompanhamentoGerado_id if item else None,
            'atestados': atestados_por_aluno.get(aluno.id, [])
        })

    if request.method == "POST":
        if sessao.finalizado == 'S':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1':
                return JsonResponse({'status': 'erro', 'mensagem': 'Bloqueado: já finalizado.'}, status=403)
            messages.error(request, "Esta sessão já foi finalizada.")
            return redirect('pedagogico:painelParecerTurma', id=sessao.id)

        # 1. Autosave via AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1':
            aluno_id = request.POST.get('aluno_id')
            parecer_ajax = request.POST.get('parecer', '').strip()

            if aluno_id:
                aluno_obj = get_object_or_404(Pessoa, id=aluno_id)
                item, _ = ItemParecerAluno.objects.get_or_create(sessao=sessao, aluno=aluno_obj)
                item.parecer = parecer_ajax
                item.save()
                return JsonResponse({'status': 'ok', 'aluno_id': aluno_id})

        # 2. Submissão convencional ou Finalização
        acao = request.POST.get('acao')

        tipo_parecer = TipoOcorrencia.objects.filter(nome__iexact='Parecer Descritivo').first()
        if not tipo_parecer:
            tipo_parecer = TipoOcorrencia.objects.filter(nome__icontains='Parecer Descritivo').first()
        if not tipo_parecer:
            tipo_parecer = TipoOcorrencia.objects.filter(parecer='S').first()

        if acao == "finalizar" and not tipo_parecer:
            messages.error(
                request,
                "Erro: Tipo de ocorrência 'Parecer Descritivo' não encontrado. Cadastre-o em Tipo de Ocorrência antes de finalizar."
            )
            return redirect('pedagogico:painelParecerTurma', id=sessao.id)

        user = request.user
        atendente = get_object_or_404(Pessoa, user=user)

        with transaction.atomic():
            for dado in dados_alunos:
                aluno_obj = dado['aluno']
                parecer_texto = request.POST.get(f'parecer_{aluno_obj.id}', '').strip()

                item, _ = ItemParecerAluno.objects.get_or_create(sessao=sessao, aluno=aluno_obj)
                item.parecer = parecer_texto
                item.save()

                if acao == "finalizar" and parecer_texto and tipo_parecer:
                    etapa_nome = sessao.periodoConselho.nome if sessao.periodoConselho else f"{sessao.ano}"
                    descricao_final = f"<strong>Parecer Descritivo ({etapa_nome}) - Turma {turma.nome}</strong><br>{parecer_texto}"

                    if item.acompanhamentoGerado:
                        acomp = item.acompanhamentoGerado
                        acomp.tipoOcorrencia = tipo_parecer
                        acomp.descricao = descricao_final
                        acomp.dataAtendimento = sessao.dataRegistro
                        acomp.save()
                    else:
                        acomp = AcompanhamentoPedagogicoAluno.objects.create(
                            aluno=aluno_obj,
                            atendimento=atendente,
                            tipoOcorrencia=tipo_parecer,
                            dataAtendimento=sessao.dataRegistro,
                            dataOcorrencia=timezone.now(),
                            descricao=descricao_final
                        )
                        item.acompanhamentoGerado = acomp
                        item.save()

            if acao == "finalizar":
                sessao.finalizado = 'S'
                messages.success(request, "Pareceres Descritivos lançados e consolidados com sucesso!")
            else:
                messages.success(request, "Pareceres salvos com sucesso.")

            sessao.save()
            return redirect('pedagogico:painelParecerTurma', id=sessao.id)

    return render(request, "pareceres/painelParecerTurma.html", {
        'sessao': sessao,
        'dados_alunos': dados_alunos,
    })


# 4. EXCLUIR (SOFT-DELETE)
@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def excluirSessaoParecer(request, id):
    sessao = get_object_or_404(SessaoParecerTurma, id=id)
    if sessao.finalizado == 'S':
        messages.error(request, "Esta sessão já está finalizada e não pode ser excluída.")
        return redirect('pedagogico:listagemPareceres')

    sessao.status = 'E'
    sessao.save()
    messages.success(request, f"Lançamento de Pareceres #{id} excluído com sucesso!")
    return redirect('pedagogico:listagemPareceres')