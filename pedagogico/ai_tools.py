from langchain.tools import tool
from .models import AcompanhamentoPedagogicoAluno, TipoOcorrencia, Pessoa, Turma
from datetime import datetime
from django.db.models import Q

@tool
def pesquisar_alunos_atrasados(mes: int):
    """
    Busca no banco de dados todos os registros de acompanhamento do tipo 'Atraso' 
    para um determinado mês (1-12). Retorna os nomes e as descrições.
    """
    try:
        # Busca o tipo de ocorrência que contém 'Atraso' no nome
        tipo = TipoOcorrencia.objects.filter(nome__icontains='Atraso').first()
        if not tipo:
            return "Tipo de ocorrência 'Atraso' não configurado no sistema."

        registros = AcompanhamentoPedagogicoAluno.objects.filter(
            tipoOcorrencia=tipo,
            dataOcorrencia__month=mes
        ).select_related('aluno')

        if not registros.exists():
            return f"Nenhum atraso encontrado para o mês {mes}."

        resultado = [f"Aluno: {r.aluno.nome} | Data: {r.dataOcorrencia.strftime('%d/%m')} | Obs: {r.descricao}" for r in registros]
        return "\n".join(resultado)
    except Exception as e:
        return f"Erro na pesquisa: {str(e)}"

@tool
def obter_ficha_e_link_aluno(nome_aluno: str):
    """
    Busca os dados de um aluno e gera o link direto para a página de acompanhamento.
    """
    try:
        aluno = Pessoa.objects.filter(nome__icontains=nome_aluno).first()
        if not aluno:
            return "Aluno não encontrado."
        
        # O link segue o padrão da sua URL: /pedagogico/listAcompanhamentoPedagogico/id
        link = f"/pedagogico/listAcompanhamentoPedagogico/{aluno.id}"
        return f"Ficha de {aluno.nome} encontrada. Matrícula: {aluno.id}. Link para abrir: {link}"
    except Exception as e:
        return f"Erro ao buscar aluno: {str(e)}"

@tool("buscar_contato_aluno")
def buscar_contato_aluno(nome_aluno: str):
    """Busca o dados do aluno. 
       Ele pode buscar por telefone, email, ou um dado especifico.
       Se houver mais de um, retorna a lista para escolha,
       O parâmetro nome_aluno deve ser apenas uma string com o nome."""
    print(f"\n[DEBUG] IA chamou buscar_contato_aluno com o parâmetro: {nome_aluno}")
    
    from geral.models import Pessoa
    
    try:
        # Usando icontains para ser mais flexível
        alunos = Pessoa.objects.filter(nome__icontains=nome_aluno)
        print(f"[DEBUG] Quantidade de alunos encontrados no banco: {alunos.count()}")
        
        if not alunos.exists():
            print(f"[DEBUG] Nenhum aluno encontrado para '{nome_aluno}'")
            return "Nenhum aluno encontrado com este nome."

        aluno = alunos.first()
        resultado = f"Nome: {aluno.nome} | Tel: {aluno.telefone} | Email: {aluno.email}"
        print(f"[DEBUG] Retornando para a IA: {resultado}")
        return resultado

    except Exception as e:
        print(f"[DEBUG] ERRO NA BUSCA: {str(e)}")
        return f"Erro ao acessar o banco de dados: {str(e)}"

@tool
def realizar_lancamento_pedagogico(nome_aluno: str, tipo_ocorrencia: str, descricao: str, data_inicio: str = None, data_fim: str = None):
    """
    Realiza o lançamento de uma nova ocorrência (Atestado, Atraso, Atendimento, etc).
    Para atestados, informe data_inicio e data_fim no formato YYYY-MM-DD.
    """
    try:
        aluno = Pessoa.objects.filter(nome__icontains=nome_aluno).first()
        tipo = TipoOcorrencia.objects.filter(nome__icontains=tipo_ocorrencia).first()
        
        if not aluno or not tipo:
            return "Aluno ou Tipo de Ocorrência não encontrados."

        # Simulando o ID do atendente (atendimento) - Ideal passar via contexto depois
        atendente = Pessoa.objects.first() 

        novo = AcompanhamentoPedagogicoAluno(
            aluno=aluno,
            atendimento=atendente,
            tipoOcorrencia=tipo,
            descricao=descricao,
            dataOcorrencia=datetime.now(),
            dataAtendimento=datetime.now().date()
        )

        if data_inicio:
            novo.dataAtestadoInicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        if data_fim:
            novo.dataAtestadoFim = datetime.strptime(data_fim, "%Y-%m-%d").date()

        novo.save()
        return f"Sucesso: {tipo.nome} registrado para {aluno.nome}."
    except Exception as e:
        return f"Erro ao salvar: {str(e)}"