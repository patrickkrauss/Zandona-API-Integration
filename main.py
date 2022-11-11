import sys
from calendar import monthrange
import requests
import json
import pandas as pd

token = 'insert_api_token_here'

url_base_da_api = 'https://postoweb.redezandona.com.br/rest/'
url_metodo_listar_id_abastecimento = url_base_da_api + 'Abastecimentos/ListarAbastecimentos'
url_metodo_listar_detalhe_abastecimento = url_base_da_api + 'Abastecimentos/BuscaAbastecimento'


def perguntaMesAnoDesejado():
    print('Informe o ano desejado no formato abaixo:')
    print('Exemplos: 2015, 2022, 2023, 2025')
    ano = int(input())

    mes = 0
    while mes < 1 or mes > 12:
        print('Informe o mês desejado conforme o numero abaixo:')
        print('1 - Janeiro      2 - Fevereiro')
        print('3 - Março        4 - Abril')
        print('5 - Maio         6 - Junho ')
        print('7 - Julho        8 - Agosto ')
        print('9 - Setembro     10 - Outubro')
        print('11 - Novembro    12 - Dezembro ')
        mes = int(input())

    print('Você informou o ano: {} e o mês {}'.format(ano, mes))
    return ano, mes


def calculaQuantidadeDeDiasDoMes(ano, mes):
    dias = []
    for i in range(monthrange(ano, mes)[1]):
        dias.append(i + 1)
    return dias


def getIdAbastecimentosDoDia(ano, mes, dia):
    mes_ajustado = mes if mes >= 10 else '0' + str(mes)  # adiciona o 0 no mês quando necessario
    dia_ajustado = dia if dia >= 10 else '0' + str(dia)  # adiciona o 0 no dia quando necessario
    parametro_data_do_abastecimento = {'DataAbastecimento': '{}-{}-{}'.format(ano, mes_ajustado, dia_ajustado)}

    response = requests.get(url_metodo_listar_id_abastecimento, headers={'Authorization': '{}'.format(token)},
                            params=parametro_data_do_abastecimento)

    lista_de_abastecimentos_do_dia = response.json()

    return lista_de_abastecimentos_do_dia


def getIdAbastecimentosMes(ano, mes, dias):
    print('Iniciando envio de requisições a API')

    lista_de_abastecimentos_do_mes = []

    for dia in dias:
        abastecimentos_do_dia = getIdAbastecimentosDoDia(ano, mes, dia)
        if abastecimentos_do_dia:  # apenas adiciona na lista se houve algum abastecimento no dia
            print('Dia {} teve {} abastecimentos'.format(dia, len(abastecimentos_do_dia)))
            lista_de_abastecimentos_do_mes.append(abastecimentos_do_dia)

    if lista_de_abastecimentos_do_mes:  # verifica se foi retornado algum abastecimento no mes
        return lista_de_abastecimentos_do_mes
    else:  # caso nao houve abastecimento no mes houve erro
        sys.exit('ERRO - O mes: {} nao retornou nenhum abastecimento'.format(mes))


def getDetalhesAbastecimentoDia(id_abastecimento):

    parametro_id_do_abastecimento = {'AbastecimentoId': '{}'.format(id_abastecimento)}

    response = requests.get(url_metodo_listar_detalhe_abastecimento, headers={'Authorization': '{}'.format(token)},
                            params=parametro_id_do_abastecimento)

    detalhe_do_abastecimento = response.json()

    if detalhe_do_abastecimento:  # verifica se foi retornado algum detalhe do abastecimento
        return detalhe_do_abastecimento
    else:  # caso nao foi retornado detalhe do abastecimento houve algo de errado
        sys.exit(('ERRO - Não foi retorno as informaçoes do abastecimento id {}'.format_map(id_abastecimento)))


def getDetalhesAbastecimentoMes(lista_ids_abastecimentos):
    print('Iniciando envio das requisições para buscar detalhes dos abastecimentos')
    lista_de_abastecimentos_do_mes = []

    for idAbastecimento in lista_ids_abastecimentos:
        detalhes_abastecimento = getDetalhesAbastecimentoDia(idAbastecimento)
        print(detalhes_abastecimento)
        print('----------------------------------------------------------------------')
        lista_de_abastecimentos_do_mes.append(detalhes_abastecimento)

    # se a quantidade de IDs diferir da quantidade de detalhes
    if len(lista_ids_abastecimentos) != len(lista_de_abastecimentos_do_mes):
        print('Houve uma falha ao buscar as informações de um dos abastecimento')  # indica que alguma requisição falhou
        print('Lista esperada: {}'.format(lista_ids_abastecimentos))
        print('Lista recebida: {}'.format(lista_de_abastecimentos_do_mes))
        sys.exit('Fim do programa')

    print('Fim da busca de detalhes dos abastecimentos')
    return lista_de_abastecimentos_do_mes


def separaSomenteOsIDsDosAbastecimentos(json_lista_dos_abastecimentos):  # recebe um json e retorna os IDs

    lista_id_dos_abastecimentos = []
    for jsonAbastecimentosDoDia in json_lista_dos_abastecimentos:
        for jsonAbastecimento in jsonAbastecimentosDoDia:
            abastecimento = json.dumps(jsonAbastecimento)  # converte o json em str
            abastecimento = json.loads(abastecimento)  # converte o json string em lista

            lista_id_dos_abastecimentos.append(abastecimento['AbastecimentoId'])  # adiciona somente o ID na lista

    return lista_id_dos_abastecimentos


def criaArquivoJsonParaTestes(json_detalhes_abastecimentos):

    with open('json_abastecimentos.json', 'w', encoding='iso-8859-1') as jsonFile:
        json.dump(json_detalhes_abastecimentos, jsonFile)


def criaArquivoCSV(lista_detalhes_abastecimentos):

    dataframe = pd.read_json(json.dumps(lista_detalhes_abastecimentos))  # Le da API
    # dataframe = pd.read_json('json_abastecimentos.json', encoding='iso-8859-1')  # Le do JSON, usado para testes

    resultado = executaOperacoesNosDados(dataframe)

    print('Iniciando criação do arquivo resultado.csv')
    resultado.to_csv('resultado.csv', index=False, decimal=',', sep=';')
    print('Arquivo resultado.csv criado com sucesso')


def converteNomeECodigoDespesas(nomes_despesas_dataframe):
    codigos_despesas = []
    nomes_despesas = []
    nomes_depesas_nao_cadastradas = set()

    for nome in nomes_despesas_dataframe.values.tolist():
        if 'S10' in nome or 'S-10' in nome:
            codigos_despesas.append('158')
            nomes_despesas.append('S10')
        elif 'S500' in nome or 'S-500' in nome:
            codigos_despesas.append('159')
            nomes_despesas.append('S500')
        elif 'ARLA' in nome:
            codigos_despesas.append('64')
            nomes_despesas.append('ARLA')
        elif 'PERFUME CABINE' in nome:
            codigos_despesas.append('85')
            nomes_despesas.append('PERFURME CABINE')
        elif 'OLEO MOTOR' in nome:
            codigos_despesas.append('66')
            nomes_despesas.append('OLEO MOTOR')
        elif 'GASOLINA' in nome:
            codigos_despesas.append('GASOLINA')
            nomes_despesas.append('GASOLINA')
        else:  # cai aqui caso nao encontrou tipo do produto
            codigos_despesas.append('')  # salva como vazio para nao dar erro
            nomes_despesas.append('')  # salva como vazio para nao dar erro
            nomes_depesas_nao_cadastradas.add(nome)

    if len(nomes_depesas_nao_cadastradas) > 0:
        print('Aviso - Há algum Nome de Despesa que não foi cadastrado')
        print('Cadastrar na linha 150 estas despesas')
        print('Despesas: {}'.format(nomes_depesas_nao_cadastradas))

    return codigos_despesas, nomes_despesas


def verificaAbastecimentoCompleto(descricao_despesas):
    lista_abastecimento_completo = []

    for item in descricao_despesas:  # se é abastecimento de S10 ou S500 é abasteciemnto completo
        if 'S10' in item or 'S500' in item:
            lista_abastecimento_completo.append('1')
        else:
            lista_abastecimento_completo.append('0')
    return lista_abastecimento_completo


def adicionaPontuacaoNoCNPJ(lista_cnpjs):  # A API retorna alguns CNPJs com somente 13 numeros
    lista_cnpjs_pontuados = []
    cnpjs_para_verificacao = set()  # aqui são salvos CNPJs com menos de 14 numeros para print ao usuario

    for cnpj in lista_cnpjs:
        cnpj_ajustado = cnpj
        while len(cnpj_ajustado) < 14:  # adiciona 0 na frente enquanto tem menos de 14 numeros
            cnpj_ajustado = '0' + cnpj_ajustado
            cnpjs_para_verificacao.add(cnpj)

        lista_cnpjs_pontuados.append(cnpj_ajustado[:2] + '.' + cnpj_ajustado[2:5] + '.' + cnpj_ajustado[5:8] + '/' +
                                     cnpj_ajustado[8:12] + '-' + cnpj_ajustado[12:])

    if len(cnpjs_para_verificacao) > 0:
        print(
            'Aviso - A API retornou alguns CNPJs dos postos com menos de 14 numeros, serão adicionado Zeros na frente '
            'destes CNPJs:')
        print('Verificar se são CNPJs válidos: {}'.format(cnpjs_para_verificacao))

    return lista_cnpjs_pontuados


def removeLinhasDeAbastecimentoGasolina(dataframe):  # remove linhas onde a coluna Descricao Despesa é Gasolina
    resultado = dataframe.drop(dataframe[dataframe['DESCRICAO_DESPESA'] == 'GASOLINA'].index)
    return resultado


def executaOperacoesNosDados(dataframe):
    data_frame_ajustado = pd.DataFrame()  # aqui são salvos os dados

    data_frame_ajustado['DOCUMENTO'] = dataframe['NumeroDocumento']

    data_frame_ajustado['DATA'] = dataframe['DataAbastecimento']
    data_frame_ajustado['DATA'] = pd.to_datetime(data_frame_ajustado['DATA'],
                                                 format='%Y-%m-%d')  # ajusta formato da data
    data_frame_ajustado['DATA'] = data_frame_ajustado['DATA'].dt.strftime('%d/%m/%Y')  # troca o - pela /

    data_frame_ajustado['PLACA_VEICULO'] = dataframe['PlacaVeiculo']

    codigos_despesa, nomes_despesas = converteNomeECodigoDespesas(dataframe['NomeProduto'])
    data_frame_ajustado['CODIGO_DESPESA'] = pd.DataFrame(codigos_despesa)
    data_frame_ajustado['DESCRICAO_DESPESA'] = pd.DataFrame(nomes_despesas)

    data_frame_ajustado['CNPJ_FORNECEDOR'] = adicionaPontuacaoNoCNPJ(
        dataframe['CNPJFranquia'].apply(str).values.tolist())

    data_frame_ajustado['QUANTIDADE'] = dataframe['LitrosAbastecidos'].round(3)

    data_frame_ajustado['VALOR_UNITARIO'] = dataframe['ValorUnitario'].round(2)

    data_frame_ajustado['VALOR_TOTAL'] = (dataframe['LitrosAbastecidos'] * dataframe['ValorUnitario']).round(
        2)  # calcula valor total

    data_frame_ajustado['TIPO_PAGAMENTO'] = ''
    data_frame_ajustado['PREVISAO_PAGAMENTO'] = ''
    data_frame_ajustado['HODOMETRO'] = dataframe['KMVeiculo']
    data_frame_ajustado['HORIMETRO'] = ''
    data_frame_ajustado['DESCONTAR_COMISSAO'] = ''
    data_frame_ajustado['ABASTECIMENTO_COMPLETO'] = verificaAbastecimentoCompleto(
        data_frame_ajustado['DESCRICAO_DESPESA'])
    data_frame_ajustado['OBSERVACAO'] = ''

    # solicitado para manter gasolina
    # dataFrameAjustadoSemAbastcGasolina = removeLinhasDeAbastecimentoGasolina(dataFrameAjustado)
    return data_frame_ajustado


if __name__ == '__main__':
    print('Inicio do programa')

    ano_informado, mes_informado = perguntaMesAnoDesejado()
    # ano, mes = (2022, 4)  # usado para teste

    listaDosAbastecimentoDoMes = getIdAbastecimentosMes(ano_informado, mes_informado, calculaQuantidadeDeDiasDoMes(ano_informado, mes_informado))

    listaDeIDsAbastecimentos = separaSomenteOsIDsDosAbastecimentos(listaDosAbastecimentoDoMes)

    detalhesDosAbastecimentosDoMes = getDetalhesAbastecimentoMes(listaDeIDsAbastecimentos)

    criaArquivoCSV(detalhesDosAbastecimentosDoMes)

    input("Aperte qualquer tecla para fechar ")
    
