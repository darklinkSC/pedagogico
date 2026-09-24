from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models.query_utils import Q
from django.db import transaction
from .models import ImportAluno, ImportUnidadeCurricularesAluno, Curso, UnidadeCurricular, Matricula, ImportConselhoClasse, Turma, AcompanhamentoPedagogicoAluno
from geral.models import Pessoa
from system.models import Campus
from geral.models import TIPO_PESSOA_ALUNO, STATUS_ATIVO, STATUS_INATIVO
import csv, io
from django.db import transaction
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse


### TELA PARA IMPORTACAO DOS DADOS DO SIGAA
@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def importarDados(request):
    return render(request, "importacao.html")


#        return render(request, "converterBase.html",{'conteudo':"Matrícula",'mensagem':"Base de Matriculas Convertida"})
def converterBaseMatricula(request):
    if request.method == "GET":
        return render(request, "converterBase.html", {'conteudo': "Matrícula"})

    if request.method == "POST":
        # 1. Carregar mapeamentos em memória para evitar milhares de GETs
        # Criamos dicionários onde a chave é o identificador (sigla ou matrícula)
        dict_ucs = {uc.sigla: uc for uc in UnidadeCurricular.objects.all()}
        dict_pessoas = {p.matricula: p for p in Pessoa.objects.all()}

        # 2. Carregar matrículas existentes para decidir entre Update ou Create
        # Chave composta: (id_da_uc, id_da_pessoa)
        dict_matriculas = {
            (m.unidadeCurricular_id, m.aluno_id): m
            for m in Matricula.objects.all()
        }

        listImportAluno = ImportUnidadeCurricularesAluno.objects.all()

        novas_matriculas = []
        matriculas_para_atualizar = []

        with transaction.atomic():
            for importAlunoUC in listImportAluno:
                try:
                    # Busca nos dicionários (O(1) de performance, muito rápido)
                    uc = dict_ucs.get(importAlunoUC.siglaUC)
                    aluno = dict_pessoas.get(importAlunoUC.matricula)

                    if not uc:
                        print(f'NAO EXISTE UC {importAlunoUC.siglaUC}')
                        continue
                    if not aluno:
                        print(f'NAO EXISTE PESSOA {importAlunoUC.matricula}')
                        continue

                    # Tenta pegar matrícula existente no dicionário
                    obj = dict_matriculas.get((uc.id, aluno.id))

                    if obj:
                        # Prepara para UPDATE
                        obj.notaFinal = importAlunoUC.notaUC
                        obj.percentualFalta = importAlunoUC.percentualFrenquencia
                        obj.periodo = importAlunoUC.periodo
                        obj.status = STATUS_ATIVO
                        matriculas_para_atualizar.append(obj)
                    else:
                        # Prepara para CREATE (se o período não for vazio)
                        if importAlunoUC.periodo != "-":
                            nova = Matricula(
                                unidadeCurricular=uc,
                                aluno=aluno,
                                notaFinal=importAlunoUC.notaUC,
                                percentualFalta=importAlunoUC.percentualFrenquencia,
                                periodo=importAlunoUC.periodo,
                                status=STATUS_ATIVO
                            )
                            novas_matriculas.append(nova)

                except Exception as e:
                    print(f'ERROR {importAlunoUC.matricula}: {e}')

            # 3. Executa as operações em lote (Bulk)
            if matriculas_para_atualizar:
                Matricula.objects.bulk_update(
                    matriculas_para_atualizar,
                    ['notaFinal', 'percentualFalta', 'periodo', 'status'],
                    batch_size=1000
                )

            if novas_matriculas:
                Matricula.objects.bulk_create(novas_matriculas, batch_size=1000)

        return render(request, "converterBase.html", {
            'conteudo': "Matrícula",
            'mensagem': f"Convertido: {len(novas_matriculas)} novas, {len(matriculas_para_atualizar)} atualizadas."
        })

####
# Convertendo BASE de dados do SIGAA da tabela ImportUnidadeCurricularAluno para os Models UNIDADE CURRICULAR
####
def converterBaseUnidadeCurricular(request):
    if request.method == "GET":
        return render(request, "converterBase.html",{'conteudo':"Unidade Curricular"})
        
    if request.method == "POST":
        ##
        # Listando ImportAlunos com dados dos Alunos do SIGAA
        ##
        listImportAluno = ImportUnidadeCurricularesAluno.objects.all()
        for importAlunoUC in listImportAluno:
            registro_novo = False
            try:
                aluno = UnidadeCurricular.objects.get(sigla=importAlunoUC.siglaUC)
                registro_novo = False
            except UnidadeCurricular.DoesNotExist:
                registro_novo = True
                print('REGISTRO NOVO',importAlunoUC.nome)
            except UnidadeCurricular.MultipleObjectsReturned:
                registro_novo = False

            try:
                #####
                # CONSEGUINDO CURSO DA UNIDADE CURRICULAR
                #####
                importAluno = ImportAluno.objects.get(matricula=importAlunoUC.matricula)
                curso = importAluno.curso
                inicio = curso.find('[') + 1
                fim = curso.find(']')
                idCurso = curso[inicio:fim]
                curso = Curso.objects.get(id=idCurso)

                if importAlunoUC.periodo != "-":
                    if registro_novo :
                        try:
                            criar = UnidadeCurricular.objects.update_or_create(
                                nome = importAlunoUC.nomeUC,
                                sigla = importAlunoUC.siglaUC,
                                curso = curso,
                                periodo = importAlunoUC.periodo
                            )
                        except:
                            print('ERRO AO CRIAR UC',importAlunoUC.nomeUC, importAlunoUC.siglaUC, importAlunoUC.periodo)        
                    else:
                        upt = UnidadeCurricular.objects.get(sigla=importAlunoUC.siglaUC)
                        upt.nome = importAlunoUC.nomeUC
                        upt.sigla = importAlunoUC.siglaUC
                        upt.curso = curso
                        upt.periodo = importAlunoUC.periodo
                        upt.save()
            except ImportAluno.DoesNotExist:
                print('ALUNO SEM MATRICULA',importAlunoUC.matricula)
            #except:
            #    print('ERRO AO CONSULTAR IMPORT',importAlunoUC.siglaUC)    
        return render(request, "converterBase.html",{'conteudo':"Unidade Curricular",'mensagem':"Base de UC Convertida"})


####
# Convertendo BASE de dados do SIGAA da tabela ImportAluno para os Models (CURSO)
####
def converterBaseCurso(request):
    if request.method == "GET":
        return render(request, "converterBase.html",{'conteudo':"Curso"})
        
    if request.method == "POST":
        ##
        # Listando ImportAlunos com dados dos Alunos do SIGAA
        ##
        listImportAluno = ImportAluno.objects.all()
        for importAluno in listImportAluno:
            #FORMATANDO STR CURSO
            curso = importAluno.curso
            inicio = curso.find('[') + 1
            fim = curso.find(']')
            idCurso = curso[inicio:fim]
            nomeCurso = curso[0:curso.find('[')]
            
            ##CAMPUS ARARANGUA TEMPORARIO
            campus = Campus.objects.get(id=1)

            #criar = Curso.objects.update_or_create(
            #    id = idCurso,
            #    nome = nomeCurso,         
            #    campus = campus
            #)   
            try:
                curso = Curso.objects.get(id=idCurso)
            except Curso.DoesNotExist:
                Curso.objects.create( 
                    id = idCurso,
                    nome = nomeCurso,
                    campus = campus
                )
            else:
                criar = Curso.objects.filter(id=idCurso).update(nome = nomeCurso,campus = campus)
	
        return render(request, "converterBase.html",{'conteudo':"Curso",'mensagem':"Base de Cursos Convertida"})


####
# Convertendo BASE de dados do SIGAA da tabela ImportAluno para os Models PESSOA( ALUNO )
####
def converterBaseAluno(request):
    if request.method == "GET":
        return render(request, "converterBase.html",{'conteudo':"Aluno"})
        
    if request.method == "POST":
        ##
        # Listando ImportAlunos com dados dos Alunos do SIGAA
        ##
        listImportAluno = ImportAluno.objects.all()
        for importAluno in listImportAluno:
            registro_novo = True
            idAluno = 0
            try:
                alunos = Pessoa.objects.filter(cpf=importAluno.cpf)
                for aluno in alunos:
                    idAluno = aluno.id
                    registro_novo = False
            except:
                print('ERRO REGISTRO',importAluno.nome)

            ##CAMPUS ARARANGUA TEMPORARIO
            campus = Campus.objects.get(id=1)

            if registro_novo:
                criar = Pessoa.objects.update_or_create(
                    nome = importAluno.nome,
                    dataNascimento = importAluno.dataNascimento,
                    telefone = importAluno.telefone,
                    email = importAluno.email,
                    cpf = importAluno.cpf,
                    rg = importAluno.rg,
                    matricula = importAluno.matricula,
                    status = STATUS_ATIVO,
                    tipoPessoa = TIPO_PESSOA_ALUNO,         
                    campus = campus
                )
            else:
                pessoa = Pessoa.objects.get(id=idAluno)
                pessoa.nome = importAluno.nome
                pessoa.dataNascimento = importAluno.dataNascimento
                pessoa.telefone = importAluno.telefone
                pessoa.email = importAluno.email
                pessoa.cpf = importAluno.cpf
                pessoa.rg = importAluno.rg
                pessoa.matricula = importAluno.matricula
                pessoa.status = STATUS_ATIVO
                pessoa.tipoPessoa = TIPO_PESSOA_ALUNO
                pessoa.campus = campus
                pessoa.save()
        return render(request, "converterBase.html",{'conteudo':"Aluno",'mensagem':"Base de Alunos Convertida"})


#####
# Importando CSV dos Alunos
#####
def importAluno(request):
    template = "importAluno.html"

    if request.method == "GET":
        data = ImportAluno.objects.all()
        prompt = {
            'order': 'Ordem: idPessoa, Matrícula, Nome, Nacionalidade, UF, Data Nascimento, RG, CPF, Telefone, Email, Necessidade Especial, Sexo, Raça, Forma Ingresso, Curso, Status',
            'profiles': data
        }
        return render(request, template, prompt)

    csv_file = request.FILES.get('file')

    if not csv_file or not csv_file.name.endswith('.csv'):
        messages.error(request, 'POR FAVOR, ENVIE UM ARQUIVO CSV.')
        return render(request, template)

    try:
        # Lendo o arquivo de forma eficiente
        data_set = csv_file.read().decode('ISO-8859-1')  # Geralmente ISO-8859-1 para BR
        io_string = io.StringIO(data_set)
        reader = csv.reader(io_string, delimiter=';', quotechar="|")
        next(reader)  # Pula o cabeçalho

        # Usamos uma transação atômica para garantir integridade e velocidade
        with transaction.atomic():
            # Limpando registros anteriores de forma performática
            ImportAluno.objects.all().delete()

            alunos_para_criar = []

            for column in reader:
                if len(column) >= 15:
                    try:
                        # Tratamento da data
                        dt_nasc = datetime.strptime(column[5].strip(), '%d/%m/%Y').date()

                        # Criamos a instância do objeto na memória (não salva no banco ainda)
                        aluno = ImportAluno(
                            matricula=column[1].strip(),
                            nome=column[2].strip(),
                            nacionalidade=column[3].strip(),
                            estado=column[4].strip(),
                            dataNascimento=dt_nasc,
                            rg=column[6].strip(),
                            cpf=column[7].strip(),
                            telefone=column[8].strip(),
                            email=column[9].strip(),
                            necessidadeEspcial=column[10].strip(),
                            sexo=column[11].strip(),
                            raca=column[12].strip(),
                            ingresso=column[13].strip(),
                            curso=column[14].strip(),
                            status=column[15].strip()
                        )
                        alunos_para_criar.append(aluno)
                    except Exception as e:
                        print(f"Erro na linha {column[0]}: {e}")

            # O "pulo do gato": Salva tudo de uma vez só
            if alunos_para_criar:
                ImportAluno.objects.bulk_create(alunos_para_criar, batch_size=1000)
                messages.success(request, f'{len(alunos_para_criar)} alunos importados com sucesso!')

    except Exception as e:
        messages.error(request, f'Erro crítico ao processar arquivo: {e}')

    return render(request, template, {})

#####
# Importando CSV com Unidades Curriculares
#####
import io
import csv
from django.shortcuts import render
from django.contrib import messages
from django.db import transaction
from .models import ImportUnidadeCurricularesAluno

def importUnidadeCurricular(request):
    template = "importUnidadeCurricular.html"

    if request.method == "GET":
        data = ImportUnidadeCurricularesAluno.objects.all()
        prompt = {
            'order': 'Ordem: Período, Matrícula, Nome, Situação, Código UC, Nome UC, Nota, Frequência, Percentual Infrequencia, ANP',
            'profiles': data
        }
        return render(request, template, prompt)

    csv_file = request.FILES.get('file')
    if not csv_file or not csv_file.name.endswith('.csv'):
        messages.error(request, 'POR FAVOR, ENVIE UM ARQUIVO CSV.')
        return render(request, template)

    try:
        # Lendo o arquivo (ISO-8859-1 costuma ser o padrão Excel/BR para acentos)
        data_set = csv_file.read().decode('ISO-8859-1')
        io_string = io.StringIO(data_set)
        reader = csv.reader(io_string, delimiter=';', quotechar="|")

        # Pula a primeira linha (cabeçalho)
        next(reader)

        with transaction.atomic():
            # Deleta tudo de uma vez de forma eficiente
            ImportUnidadeCurricularesAluno.objects.all().delete()

            ucs_para_criar = []

            # enumerate permite controlar o índice da linha sem precisar de contador manual
            for index, column in enumerate(reader):
                # Seus dados começam após a 5ª linha de conteúdo (conforme seu código original)
                # Como já demos um next(reader) acima, o index 0 aqui é a linha 2 do arquivo.
                # Se você quer pular exatamente 5 linhas de DADOS:
                if index < 5:
                    continue

                if len(column) >= 10:
                    try:
                        # Criando o objeto na memória
                        unidade = ImportUnidadeCurricularesAluno(
                            periodo=column[0].strip(),
                            matricula=column[1].strip(),
                            nome=column[2].strip(),
                            situacao=column[3].strip(),
                            siglaUC=column[4].strip(),
                            nomeUC=column[5].strip(),
                            notaUC=column[6].strip().replace(',', '.'),  # Ajuste para números decimais
                            frequencia=column[7].strip(),
                            percentualFrenquencia=column[8].strip(),
                            anp=column[9].strip()
                        )
                        ucs_para_criar.append(unidade)
                    except Exception as e:
                        print(f"Erro na linha {index + 2}: {e}")

            # Inserção em massa (Batch de 1000 em 1000)
            if ucs_para_criar:
                ImportUnidadeCurricularesAluno.objects.bulk_create(ucs_para_criar, batch_size=1000)
                messages.success(request, f'{len(ucs_para_criar)} registros de UC importados!')

    except Exception as e:
        messages.error(request, f'Erro ao processar arquivo: {e}')

    return render(request, template, {})


#####
# Importando CSV com Notas do Conselho de Classe
#####
def importConselhoClasse(request):
    # declaring template
    template = "importConselhoClasse.html"
    #data = ImportConselhoClasse.objects.all()

    # prompt is a context variable that can have different values      depending on their context
    prompt = {
        'order': 'Ordem do arquivo CSV : Matricula, Nome, Notas, Faltas',
    }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)

    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'Por favor, envie um arquivo CSV válido')
        return render(request, template, prompt)

    try:
        data_set = csv_file.read().decode('UTF-8')
        # setup a stream which is when we loop through each line we are able to handle a data in a stream
        io_string = io.StringIO(data_set)
        
        reader = csv.reader(io_string, delimiter=',')

        #Pega o cabeçalho
        header_row = next(reader)
        # Extrai os nomes das Unidades Curriculares do cabeçalho
        # Assumindo que o formato é Matrícula, Nome, UC1_Nota, UC1_Falta, UC2_Nota, UC2_Falta ...
        unidades_curriculares = [header_row[i] for i in range(2, len(header_row), 2)]

        objetos_para_criar = []

        with transaction.atomic(): # Garante que ou tudo é salvo, ou nada é
            for row in reader:
                if not row: # Pula linhas em branco
                    continue
                
                matricula = row[0]
                
                # Itera sobre as notas e faltas em pares
                for i, uc_nome in enumerate(unidades_curriculares):
                    # Índice da nota é 2*i + 2. Índice da falta é 2*i + 3.
                    nota_idx = 2 * i + 2
                    falta_idx = 2 * i + 3
                    
                    if nota_idx < len(row) and row[nota_idx].strip() != "":
                        nota = row[nota_idx].strip()
                        # Se houver uma coluna de falta correspondente
                        falta = row[falta_idx].strip() if falta_idx < len(row) else 0

                        objetos_para_criar.append(
                            ImportConselhoClasse(
                                matricula=matricula,
                                unidadeCurricular=uc_nome,
                                notas=nota,
                                faltas=int(falta) if falta.isdigit() else 0
                            )
                        )

            # Agora, crie todos os objetos no banco de dados de uma só vez!
            if objetos_para_criar:
                ImportConselhoClasse.objects.bulk_create(objetos_para_criar)

        messages.success(request, 'Arquivo importado com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao processar o arquivo: {e}')

     # Após o POST, é uma boa prática redirecionar para evitar reenvio do formulário
    from django.shortcuts import redirect
    return redirect('/pedagogico/importConselhoClasse/')

### Listas alunos importados
def listAlunosImportados(request):
    lista = ImportAluno.objects.all()
    
    ''' 
        Realizando a busca e filtrando na tabela
    '''
    busca = request.GET.get('search')
    if busca:
        lista = lista.filter(Q(nome__icontains = busca))

    '''
        Criando paginação
    '''
    paginas = Paginator(lista, 50)
    page = request.GET.get('page')
    lista = paginas.get_page(page)  

    return render(request, 'listImportAlunos.html', {'lista':lista})


### Listas matriculas importados
def listMatriculasImportadas(request):
    lista = ImportUnidadeCurricularesAluno.objects.all()
    
    ''' 
        Realizando a busca e filtrando na tabela
    '''
    busca = request.GET.get('search')
    if busca:
        lista = lista.filter(Q(nome__icontains = busca))

    '''
        Criando paginação
    '''
    paginas = Paginator(lista, 50)
    page = request.GET.get('page')
    lista = paginas.get_page(page)  

    return render(request, 'listImportMatricula.html', {'lista':lista})


### Listar alunos com atestado médico para consulta dos professores
from django.db.models import Max
from .models import Matricula, AcompanhamentoPedagogicoAluno
from django.db import connection
from django.utils import timezone


def lista_alunos_atestado(request):
    # 1. Combo de Turmas
    turmas_existentes = Matricula.objects.filter(status='A').values(
        'unidadeCurricular__curso__sigla',
        'periodo'
    ).distinct().order_by('-unidadeCurricular__curso__sigla', 'periodo')

    opcoes_turmas = [
        f"{t['unidadeCurricular__curso__sigla']}-{t['periodo']}"
        for t in turmas_existentes
    ]

    # 2. Recebe as datas de início e fim
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()
    turma_sel = request.GET.get('turma_slug', '').strip()
    acompanhamentos = []

    hoje = timezone.now().date().strftime('%Y-%m-%d')
    if not data_inicio and not data_fim:
        data_inicio = hoje
        data_fim = hoje
    elif data_inicio and not data_fim:
        data_fim = data_inicio
    elif data_fim and not data_inicio:
        data_inicio = data_fim

    # 3. Executa a busca se a turma estiver selecionada
    if turma_sel and "-" in turma_sel:
        sigla, periodo = turma_sel.split("-")

        query = """
            SELECT DISTINCT
                a.id, 
                p.nome, 
                a.dataAtestadoInicio, 
                a.dataAtestadoFim,
                a.aluno_id
            FROM 
                acompanhamento_pedagogico_aluno a
            INNER JOIN pessoa p ON (a.aluno_id = p.id)
            INNER JOIN matricula m ON (m.aluno_id = p.id)
            INNER JOIN unidadeCurricular uc ON (m.unidadeCurricular_id = uc.id)
            INNER JOIN curso c ON (uc.curso_id = c.id)
            WHERE 
                a.tipoOcorrencia_id = 9
                AND (a.status IS NULL OR a.status != 'E')
                AND (m.status IS NULL OR m.status = 'A')
                AND c.sigla = %s
                AND m.periodo = %s
                AND a.dataAtestadoInicio <= STR_TO_DATE(%s, '%%Y-%%m-%%d')
                AND a.dataAtestadoFim >= STR_TO_DATE(%s, '%%Y-%%m-%%d')
            ORDER BY 
                p.nome ASC
        """

        # Parâmetros: sigla, periodo, data_fim, data_inicio
        acompanhamentos = AcompanhamentoPedagogicoAluno.objects.raw(
            query, [sigla, periodo, data_fim, data_inicio]
        )

    return render(request, 'lista_atestados.html', {
        'opcoes_turmas': opcoes_turmas,
        'acompanhamentos': acompanhamentos,
        'turma_sel': turma_sel,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })




# Configuração da API (Coloque sua chave aqui)
import json, re
from groq import Groq
from django.http import JsonResponse
from django.db.models import Q
from .models import Pessoa 

# Crie sua chave em console.groq.com (é rápido e grátis)
client = Groq(api_key="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")
@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def chat_ia_view(request):
    if request.method == "POST":
        mensagem = request.POST.get('mensagem', '')
        
        #Caso tenha mais de um nome e o sistema gere a lista com os nomes
        #Ao clicar em algum executa essa condição.
        if "Detalhes do aluno ID" in mensagem:
            import re
            id_aluno = re.findall(r'\d+', mensagem)[0]
            aluno = Pessoa.objects.get(id=id_aluno)
            return JsonResponse({
                'status': 'sucesso',
                'dados': {
                   'acao': 'contato',
                   'aluno_id': aluno.id,
                   'nome_completo': aluno.nome,
                   'email': aluno.email or 'Não informado',
                   'contato_info': f"Tel: {aluno.telefone or 'N/A'}",
                   'url_ficha': f"/pedagogico/listAcompanhamentoPedagogico/{aluno.id}"
                }
            })
        try:
            print(f">>> Usando Llama 3 via CLOUD (Groq) para: {mensagem}")
            
            
            hoje_str = datetime.now().strftime('%Y-%m-%d')
            system_prompt = (
                f"Hoje é {hoje_str}. Responda apenas JSON puro. "
                "Se o usuário pedir contato ou lançar algo para um aluno específico, use: "
                "{'aluno': 'nome', 'acao': 'contato', 'tipo': 'atraso', 'obs': ''}. "
                "Se o usuário pedir relatórios, faltas ou atrasos de um período, use: "
                "{'acao': 'relatorio', 'tipo': 'nome_do_tipo', 'inicio': 'YYYY-MM-DD', 'fim': 'YYYY-MM-DD'}"
            )

            # Chamada para a Nuvem da Groq
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": mensagem,
                    }
                ],
                model="llama-3.3-70b-versatile", # Modelo potente rodando na nuvem deles
                temperature=0,
                response_format={"type": "json_object"} # Garante o JSON perfeito
            )

            json_ia = chat_completion.choices[0].message.content
            print(f">>> Resposta da Nuvem: {json_ia}")
            
            dados_ia = json.loads(json_ia)

            # 2. NOVA LÓGICA: TRATAMENTO DE RELATÓRIO
            if dados_ia.get('acao') == 'relatorio':
                termo_tipo = dados_ia.get('tipo', 'Atraso')
                inicio = dados_ia.get('inicio')
                fim = dados_ia.get('fim')

                # Busca o ID do tipo no seu MySQL
                tipo_obj = TipoOcorrencia.objects.filter(nome__icontains=termo_tipo).first()
                
                # Se a IA não mandou datas, pegamos o mês atual
                if not inicio or not fim:
                    hoje = datetime.now()
                    inicio = hoje.replace(day=1).strftime('%Y-%m-%d')
                    fim = hoje.strftime('%Y-%m-%d')

                # AQUI ESTÁ O AJUSTE: Usando 'dataDe' e 'dataAte' que sua função espera
                # Adicionei 'detalhado=S' para ele já abrir a lista completa por padrão
                url_relatorio = (
                    f"/pedagogico/listAlunosAtestado/?"
                    f"dataDe={inicio}&"
                    f"dataAte={fim}&"
                    f"tipoOcorrencia={tipo_obj.id if tipo_obj else ''}&"
                    f"detalhado=S"
                )

                return JsonResponse({
                    'status': 'sucesso',
                    'dados': {
                        'acao': 'relatorio',
                        'tipo_nome': tipo_obj.nome if tipo_obj else termo_tipo,
                        'inicio': datetime.strptime(inicio, '%Y-%m-%d').strftime('%d/%m/%y'),
                        'fim': datetime.strptime(fim, '%Y-%m-%d').strftime('%d/%m/%y'),
                        'url': url_relatorio
                    }
                })

            nome_aluno = dados_ia.get('aluno')

            if not nome_aluno or nome_aluno.lower() == "null":
                return JsonResponse({'status': 'sucesso', 'dados': {'acao': 'conversa', 'obs': "Não entendi o nome."}})

            # Busca no seu MySQL Local
            alunos = Pessoa.objects.filter(Q(nome__icontains=nome_aluno) | Q(matricula__icontains=nome_aluno))

            if alunos.count() > 1:
                lista = [{"id": a.id, "nome": a.nome} for a in alunos[:5]]
                return JsonResponse({'status': 'multiplos', 'alunos': lista})

            elif alunos.count() == 1:
                aluno = alunos.first()
                url_ficha = f"/pedagogico/listAcompanhamentoPedagogico/{aluno.id}"
                
                # Lógica de resposta igual ao que já estávamos fazendo
                if any(x in mensagem.lower() for x in ['atraso', 'falta', 'atestado']):
                    return JsonResponse({
                        'status': 'sucesso',
                        'dados': {
                            'acao': 'lancamento', 'aluno_id': aluno.id, 'nome_completo': aluno.nome,
                            'url_ficha': url_ficha, 'tipo': 'Atraso', 'obs': mensagem
                        }
                    })
                
                return JsonResponse({
                    'status': 'sucesso',
                    'dados': {
                        'acao': 'contato', 'aluno_id': aluno.id, 'nome_completo': aluno.nome, 'email' : aluno.email, 
                        'url_ficha': url_ficha, 'contato_info': f"Tel: {aluno.telefone or 'N/A'}"
                    }
                })

            return JsonResponse({'status': 'sucesso', 'dados': {'acao': 'conversa', 'obs': f"O aluno '{nome_aluno}' não foi encontrado."}})

        except Exception as e:
            print(f"!!! ERRO NA NUVEM: {str(e)}")
            return JsonResponse({'status': 'erro', 'message': str(e)})

    return JsonResponse({'status': 'erro', 'message': 'Use POST.'})



###
#   Salvar atraso via CHAT IA
###
from datetime import datetime
from django.http import JsonResponse
from .models import AcompanhamentoPedagogicoAluno, TipoOcorrencia, Pessoa
from django.shortcuts import get_object_or_404

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def salvar_atraso_ia(request):
    if request.method == "POST":
        aluno_id = request.POST.get('aluno_id')
        observacao = request.POST.get('obs')
        
        try:
            # Captura o momento exato agora
            agora = datetime.now()
            data_hora_formatada = agora.strftime('%d/%m/%Y às %H:%M')

            # Pegamos o aluno (Pessoa)
            aluno = Pessoa.objects.get(id=aluno_id)
            
            # Pegamos quem está realizando o atendimento (usuário logado)
            user = request.user 
            atendente = get_object_or_404(Pessoa,user=user)          

            # Buscamos o Tipo de Ocorrência "Atraso" (ou o que a IA mandou)
            # Se não existir, você pode ajustar para um ID fixo que exista no seu banco
            tipo = TipoOcorrencia.objects.get(nome__icontains='Atrasos')
            descricao_final = f"Lançado via IA Pedagógica<br><strong>Chegada em: {data_hora_formatada}</strong><br>{observacao}"

            # 4. Criamos o registro na sua tabela oficial
            novo_registro = AcompanhamentoPedagogicoAluno.objects.create(
                aluno=aluno,
                atendimento=atendente,
                tipoOcorrencia=tipo,
                descricao=descricao_final,
                dataOcorrencia=agora,
                dataAtendimento=agora.date()
            )
            
            return JsonResponse({
                'status': 'sucesso', 
                'message': f'Acompanhamento lançado com sucesso para {aluno.nome}!'
            })
            
        except Exception as e:
            print(f"Erro ao salvar no MySQL: {str(e)}")
            return JsonResponse({'status': 'erro', 'message': f"Erro no banco: {str(e)}"})

    return JsonResponse({'status': 'erro', 'message': 'Método inválido'})

#### TROCAR ANO
# Função para adaptar a troca de Unidades Curriculares quando troca o ano letivo, tirando as UC que do ano anterior que o Aluno.
# deixando somente as ano corrente.
####
@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def atualizarStatusTrocaAno(request):
    # Executa o update em massa no MySQL
    # update matricula set status='C'
    quantidade = Matricula.objects.all().update(status='C')
    
    # Adiciona uma mensagem de feedback para o usuário
    from django.contrib import messages
    messages.success(request, f"Processo concluído! {quantidade} matrículas foram atualizadas para 'C'.")
    
    # Redireciona de volta para a lista de turmas
    return redirect('pedagogico:importarDados')



@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def converterBaseTurma(request):
    if request.method == "GET":
        return render(request, "converterBase.html", {'conteudo': "Turma"})

    if request.method == "POST":
        # 1. Busca todas as combinações únicas de Curso e Período das Matrículas
        combinacoes = Matricula.objects.exclude(periodo__isnull=True).values(
            'unidadeCurricular__curso_id',
            'unidadeCurricular__curso__sigla',
            'periodo'
        ).distinct()

        turmas_criadas = 0
        turmas_atualizadas = 0

        with transaction.atomic():
            for item in combinacoes:
                curso_id = item['unidadeCurricular__curso_id']
                sigla = item['unidadeCurricular__curso__sigla']
                periodo = item['periodo']

                if curso_id and periodo:
                    # Padrão de nome: SIGLA-PERIODO (ex: TADS-1, EMI-INF-3)
                    nome_turma = f"{sigla}-{periodo}"

                    turma_obj, created = Turma.objects.get_or_create(
                        nome=nome_turma,
                        curso_id=curso_id,
                        defaults={'periodo': periodo}
                    )

                    if created:
                        turmas_criadas += 1
                    else:
                        if turma_obj.periodo != periodo:
                            turma_obj.periodo = periodo
                            turma_obj.save()
                            turmas_atualizadas += 1

        return render(request, "converterBase.html", {
            'conteudo': "Turma",
            'mensagem': f"Base de Turmas Sincronizada: {turmas_criadas} novas turmas criadas e {turmas_atualizadas} atualizadas com sucesso!"
        })