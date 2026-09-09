from geral.models import Pessoa, STATUS_ATIVO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import date, datetime

from pedagogico.models import (
    AcompanhamentoPedagogicoAluno,
    Curso,
    Matricula,
    UnidadeCurricular,
    ConselhoClasse,
    ConselhoClasseAluno,
    PeriodoConselho,
    Turma,
    TipoOcorrencia,
)
from pedagogico.app.formsAcompanhamentoPedagogico import AcompanhamentoPedagogicoAlunoForm
from pedagogico.app.formsConselhoClasse import ConselhoClasseNovoForm, PeriodoConselhoForm
from django.db.models import Q

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_conselhoclasse', login_url='/geral/paginaSemPermissao')
def listCursoConselhoClasse(request):
    lista = Curso.objects.all()
    busca = request.GET.get('search')
    if busca:
        lista = lista.filter(Q(nome__icontains=busca))
    paginas = Paginator(lista, 10)
    page = request.GET.get('page')
    lista = paginas.get_page(page)
    return render(request, 'listCursoConselhoClasse.html', {'lista': lista})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_conselhoclasse', login_url='/geral/paginaSemPermissao')
def listTurmaConselhoClasse(request, id):
    curso = Curso.objects.get(id=id)
    lista = UnidadeCurricular.objects.filter(curso=curso).values('periodo').distinct().order_by('periodo')
    return render(request, 'listTurmaConselhoClasse.html', {'lista': lista, 'curso': curso})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_conselhoclasse', login_url='/geral/paginaSemPermissao')
def listUnidadeCurricularConselhoClasse(request, curso_id, periodo):
    curso = Curso.objects.get(id=curso_id)
    lista = UnidadeCurricular.objects.filter(curso=curso, periodo=periodo).order_by('nome')
    return render(request, 'listUnidadeCurricularConselhoClasse.html',
                  {'periodo': periodo, 'lista': lista, 'curso': curso})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_conselhoclasse', login_url='/geral/paginaSemPermissao')
def listAlunosConselhoClasse(request, id):
    uc = UnidadeCurricular.objects.get(id=id)
    lista = Matricula.objects.filter(unidadeCurricular=uc, status='A').order_by('aluno')
    return render(request, 'listAlunosConselhoClasse.html', {'lista': lista, 'uc': uc})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_conselhoclasse', login_url='/geral/paginaSemPermissao')
def listAlunoPorUCConselhoClasse(request, curso_id, periodo):
    curso = Curso.objects.get(id=curso_id)
    listaUC = UnidadeCurricular.objects.filter(curso=curso, periodo=periodo)
    listaM = Matricula.objects.filter(unidadeCurricular__in=listaUC, status='A')
    listaA = [m_.aluno.id for m_ in listaM]
    listaAluno = Pessoa.objects.filter(id__in=listaA).order_by('nome')
    return render(request, 'listAlunoPorUCConselhoClasse.html',
                  {'lista': listaAluno, 'curso': curso, 'periodo': periodo})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_conselhoclasse', login_url='/geral/paginaSemPermissao')
def listAlunoConselhoClasse(request, id_aluno, id_curso, periodo):
    pessoa = Pessoa.objects.get(id=id_aluno)
    curso = Curso.objects.get(id=id_curso)
    lista = Matricula.objects.filter(aluno=pessoa, status='A').order_by('aluno')
    anoAtual = date.today().year
    listaAtestado = AcompanhamentoPedagogicoAluno.objects.filter(aluno=pessoa,
                                                                 dataAtestadoInicio__year=anoAtual).order_by(
        'dataAtestadoInicio')
    form = AcompanhamentoPedagogicoAlunoForm()
    if request.method == 'POST':
        form = AcompanhamentoPedagogicoAlunoForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            atendido = get_object_or_404(Pessoa, user=user)
            form.instance.aluno = pessoa
            form.instance.atendimento = atendido
            form.save()
            return render(request, 'listAlunoConselhoClasse.html',
                          {'form': form, 'lista': lista, 'listaAtestado': listaAtestado, 'aluno': pessoa,
                           'curso': curso, 'periodo': periodo})
    return render(request, 'listAlunoConselhoClasse.html',
                  {'form': form, 'lista': lista, 'listaAtestado': listaAtestado, 'aluno': pessoa, 'curso': curso,
                   'periodo': periodo})


# =======================================================
# NOVAS FUNÇÕES DO NOVO FLUXO DO CONSELHO DE CLASSE
# =======================================================

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_conselhoclasse', login_url='/geral/paginaSemPermissao')
def listagemConselhos(request):
    # Exclui tudo que foi marcado como 'E' (Excluído)
    conselhos = ConselhoClasse.objects.exclude(status='E').select_related(
        'turma', 'periodoConselho', 'responsavel'
    ).order_by('-ano', '-dataConselho', '-id')

    ano_filtro = request.GET.get('ano')
    turma_filtro = request.GET.get('turma')
    if ano_filtro:
        conselhos = conselhos.filter(ano=ano_filtro)
    if turma_filtro:
        conselhos = conselhos.filter(turma__nome__icontains=turma_filtro)

    paginas = Paginator(conselhos, 15)
    page = request.GET.get('page')
    lista = paginas.get_page(page)
    return render(request, "conselho/listagemConselhos.html", {
        'lista': lista,
        'ano_filtro': ano_filtro,
        'turma_filtro': turma_filtro
    })


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_conselhoclasse', login_url='/geral/paginaSemPermissao')
def criarConselho(request):
    form = ConselhoClasseNovoForm(request.POST or None,
                                  initial={'ano': date.today().year, 'dataConselho': date.today()})
    if request.method == 'POST' and form.is_valid():
        user = request.user
        responsavel = get_object_or_404(Pessoa, user=user)
        conselho = form.save(commit=False)
        conselho.responsavel = responsavel
        conselho.save()
        messages.success(request, f"Conselho #{conselho.id} criado com sucesso!")
        return redirect('pedagogico:painelConselho', id=conselho.id)
    return render(request, "conselho/criarConselho.html", {'form': form})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_conselhoclasse', login_url='/geral/paginaSemPermissao')
def painelConselho(request, id):
    conselho = get_object_or_404(ConselhoClasse.objects.select_related('turma', 'periodoConselho'), id=id)
    turma = conselho.turma
    curso = turma.curso

    # 1. Pega as disciplinas cadastradas no período da turma
    disciplinas_candidatas = UnidadeCurricular.objects.filter(
        curso=curso,
        periodo=turma.periodo
    ).order_by('nome')

    if not disciplinas_candidatas.exists():
        disciplinas_candidatas = UnidadeCurricular.objects.filter(
            matricula__periodo=turma.periodo,
            matricula__status=STATUS_ATIVO
        ).distinct().order_by('nome')

    # 2. Busca as matrículas ativas da turma
    matriculas = Matricula.objects.filter(
        unidadeCurricular__in=disciplinas_candidatas,
        periodo=turma.periodo,
        status=STATUS_ATIVO
    ).select_related('aluno', 'unidadeCurricular').order_by('aluno__nome')

    # Função auxiliar para checar se a nota é válida e maior que zero
    def nota_valida_maior_zero(valor_str):
        if not valor_str:
            return False
        v = str(valor_str).strip().replace(',', '.')
        try:
            return float(v) > 0.0
        except ValueError:
            return bool(v and v not in ['-', '0', '0.0'])

    # 3. Mapeamento de alunos e identificação de disciplinas com nota
    alunos_dict = {}
    disciplinas_com_dados = set()

    for m in matriculas:
        if m.aluno_id not in alunos_dict:
            alunos_dict[m.aluno_id] = {
                'aluno': m.aluno,
                'disciplinas': {},
                'possui_nota_valida': False
            }

        nota_txt = (m.notaFinal or m.notaParcial or '').strip()
        falta_txt = (m.percentualFalta or '').strip().replace('%', '')

        if nota_valida_maior_zero(nota_txt):
            alunos_dict[m.aluno_id]['possui_nota_valida'] = True
            disciplinas_com_dados.add(m.unidadeCurricular_id)

        alunos_dict[m.aluno_id]['disciplinas'][m.unidadeCurricular_id] = {
            'nota': nota_txt if nota_txt else '-',
            'falta': falta_txt if falta_txt else '0'
        }

    # 4. Filtra apenas alunos que tenham ao menos uma nota > 0
    alunos_filtrados = {
        aluno_id: dados
        for aluno_id, dados in alunos_dict.items()
        if dados['possui_nota_valida']
    }

    # 5. Mantém apenas as disciplinas que tiveram notas entre os alunos válidos
    disciplinas = [d for d in disciplinas_candidatas if d.id in disciplinas_com_dados]

    # Carrega pareceres individuais já salvos
    pareceres_existentes = {
        item.aluno_id: item.parecer
        for item in ConselhoClasseAluno.objects.filter(conselho=conselho)
    }

    # Carrega atestados do ano para os alunos filtrados
    atestados = AcompanhamentoPedagogicoAluno.objects.filter(
        dataAtestadoInicio__year=conselho.ano,
        aluno_id__in=alunos_filtrados.keys()
    ).order_by('dataAtestadoInicio')

    atestados_por_aluno = {}
    for a in atestados:
        atestados_por_aluno.setdefault(a.aluno_id, []).append(a)

    dados_alunos = []
    for aluno_id, dados in alunos_filtrados.items():
        dados_alunos.append({
            'aluno': dados['aluno'],
            'disciplinas': dados['disciplinas'],
            'parecer': pareceres_existentes.get(aluno_id, ''),
            'atestados': atestados_por_aluno.get(aluno_id, []),
        })

    # Tratamento de POST (Salvar tradicional, Finalizar ou AJAX em background)
    if request.method == "POST":
        # BLOQUEIO: Se o conselho já estiver finalizado, rejeita qualquer alteração
        if conselho.finalizado == 'S':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1':
                return JsonResponse({'status': 'erro', 'mensagem': 'Conselho finalizado não permite alterações.'}, status=403)
            messages.error(request, "Este conselho já está finalizado e não pode mais ser alterado.")
            return redirect('pedagogico:painelConselho', id=conselho.id)

        # Suporte para salvar em background (AJAX) quando sai do campo
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1':
            aluno_id = request.POST.get('aluno_id')
            parecer_ajax = request.POST.get('parecer', '').strip()
            parecer_geral_ajax = request.POST.get('parecerGeral')

            if parecer_geral_ajax is not None:
                conselho.parecerGeral = parecer_geral_ajax
                conselho.save()
                return JsonResponse({'status': 'ok', 'tipo': 'geral'})

            if aluno_id:
                aluno_obj = get_object_or_404(Pessoa, id=aluno_id)
                cca, _ = ConselhoClasseAluno.objects.get_or_create(
                    conselho=conselho,
                    aluno=aluno_obj
                )
                cca.parecer = parecer_ajax
                cca.save()
                return JsonResponse({'status': 'ok', 'aluno_id': aluno_id})

        # Processamento do formulário normal
        conselho.parecerGeral = request.POST.get('parecerGeral', '')
        acao = request.POST.get('acao')

        # Busca especificamente o tipo de ocorrência criado para Conselho de Classe
        tipo_conselho = TipoOcorrencia.objects.filter(nome__iexact='Conselho de Classe').first()

        # Fallbacks de segurança caso o nome tenha pequenas variações
        if not tipo_conselho:
            tipo_conselho = TipoOcorrencia.objects.filter(parecer='S').first()
        if not tipo_conselho:
            tipo_conselho = TipoOcorrencia.objects.filter(nome__icontains='Conselho').first()

        if not tipo_conselho:
            messages.error(request, "Erro: Não foi encontrado um Tipo de Ocorrência cadastrado para 'Conselho de Classe'. Cadastre-o antes de finalizar.")
            return redirect('pedagogico:painelConselho', id=conselho.id)

        user = request.user
        atendente = get_object_or_404(Pessoa, user=user)

        with transaction.atomic():
            for dado in dados_alunos:
                aluno_obj = dado['aluno']
                parecer_texto = request.POST.get(f'parecer_{aluno_obj.id}', '').strip()

                cca, _ = ConselhoClasseAluno.objects.get_or_create(
                    conselho=conselho,
                    aluno=aluno_obj
                )
                cca.parecer = parecer_texto
                cca.save()

                if acao == "finalizar" and parecer_texto:
                    desc_completa = f"<strong>Parecer do Conselho ({conselho.periodoConselho.nome}/{conselho.ano})</strong><br>{parecer_texto}"
                    if cca.acompanhamentoGerado:
                        acompanhamento = cca.acompanhamentoGerado
                        acompanhamento.descricao = desc_completa
                        acompanhamento.dataConselho = conselho.dataConselho
                        acompanhamento.dataAtendimento = conselho.dataConselho
                        acompanhamento.save()
                    else:
                        acompanhamento = AcompanhamentoPedagogicoAluno.objects.create(
                            aluno=aluno_obj,
                            atendimento=atendente,
                            tipoOcorrencia=tipo_conselho,
                            dataConselho=conselho.dataConselho,
                            dataAtendimento=conselho.dataConselho,
                            dataOcorrencia=timezone.now(),
                            descricao=desc_completa
                        )
                        cca.acompanhamentoGerado = acompanhamento
                        cca.save()

            if acao == "finalizar":
                conselho.finalizado = 'S'
                messages.success(request, "Conselho finalizado com sucesso! Pareceres registrados nas fichas dos alunos.")
            else:
                messages.success(request, "Alterações salvas com sucesso.")

            conselho.save()
            return redirect('pedagogico:painelConselho', id=conselho.id)

    return render(request, "conselho/painelConselho.html", {
        'conselho': conselho,
        'disciplinas': disciplinas,
        'dados_alunos': dados_alunos,
    })


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.delete_conselhoclasse', login_url='/geral/paginaSemPermissao')
def excluirConselhoClasse(request, id):
    conselho = get_object_or_404(ConselhoClasse, id=id)

    # BLOQUEIO: Não permite excluir conselho já finalizado
    if conselho.finalizado == 'S':
        messages.error(request, f"O Conselho #{id} já está finalizado e não pode ser excluído.")
        return redirect('pedagogico:listagemConselhos')

    # Marca o conselho como excluído (soft delete)
    conselho.status = 'E'
    conselho.save()

    messages.success(request, f"Conselho #{id} foi marcado como excluído com sucesso!")
    return redirect('pedagogico:listagemConselhos')

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_conselhoclasse', login_url='/geral/paginaSemPermissao')
def listConselhoClasse(request):
    conselhos = ConselhoClasse.objects.filter(status='A').select_related('turma', 'periodoConselho').order_by('-ano', '-id')
    return render(request, "conselho/listConselhoClasse.html", {'conselhos': conselhos})
