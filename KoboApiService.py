import xlrd
import requests
import json
import os

lista_content = dict()


def imprimir_lista_formularios(u_r_l, u_s_e_r, p_a_s_s_w_o_r_d):
    r = requests.get('https://' + u_r_l + '/api/v1/data', auth=(u_s_e_r, p_a_s_s_w_o_r_d))
    lista_content = json.loads(r.content)
    return lista_content

def retorna_respostas_com_labels(u_r_l, i_d, u_s_e_r, p_a_s_s_w_o_r_d):
    formulario = retorna_lista_com_labels(u_r_l, i_d, u_s_e_r, p_a_s_s_w_o_r_d)
    if u_r_l == 'kobocat.docker.kobo.techo.org':
        u_r_l = 'koboform.docker.kobo.techo.org'
    if u_r_l == 'kc.humanitarianresponse.info':
            u_r_l = 'kobo.humanitarianresponse.info'
    req_url = 'https://' + u_r_l + '/assets/' + formulario[1] + '.json'
    req = requests.get(req_url, auth=(u_s_e_r, p_a_s_s_w_o_r_d))
    lista_content = json.loads(req.content)
    lista_perguntas_labels = dict()
    for item in lista_content['content']['survey']:
        if 'select_from_list_name' in item:
            for pergunta in lista_content['content']['choices']:
                    if pergunta['list_name'] in item['select_from_list_name']:
                        lista_perguntas_labels[item['label'][0]] = pergunta['label'][0]
    for resposta in formulario[0]:
        for key, value in lista_perguntas_labels.items():
            for chave, valor in resposta.items():
                if isinstance(valor,list):
                 for awnser in valor:
                    if key in awnser:
                        awnser[key] = value
                else:
                    if key in resposta:
                        resposta[key] = value

    return formulario[0]

def retorna_key_do_formulario(u_r_l, id, u_s_e_r, p_a_s_s_w_o_r_d):
    req = requests.get(u_r_l, auth=(u_s_e_r, p_a_s_s_w_o_r_d))
    lista_content_id = json.loads(req.content)
    for item in lista_content_id:
        if item['id'] == id:
            return item['id_string']

def retorna_lista_com_labels(u_r_l, i_d, u_s_e_r, p_a_s_s_w_o_r_d):
    global lista_content
    id_string = retorna_key_do_formulario('https://' + u_r_l + '/api/v1/data', i_d, u_s_e_r, p_a_s_s_w_o_r_d)

    if u_r_l == 'kobocat.docker.kobo.techo.org':
        u_r_l_novo = 'koboform.docker.kobo.techo.org'
    if u_r_l == 'kc.humanitarianresponse.info':
        u_r_l_novo= 'kobo.humanitarianresponse.info'
    req = requests.get('https://' + u_r_l_novo + '/assets/' + id_string + '.json', auth=(u_s_e_r, p_a_s_s_w_o_r_d))
    lista_content = json.loads(req.content)
    formulario = importar_xls_grupamento_para_lista('https://' + u_r_l + '/api/v1/data/' + str(i_d) + '.xls', u_s_e_r, p_a_s_s_w_o_r_d,i_d)
    labels_dict = dict()
    for item in lista_content['content']['survey']:
        if 'label' in item:
            labels_dict[item['$autoname']] = item['label']
    for enquete in formulario:
                for key, value in labels_dict.items():
                    if key in enquete:
                        enquete[value[0]] = enquete.pop(key)
    retorno = [formulario, id_string]
    return retorno
def filtra__labels_respostas_grupamento(lista_grupamento):
    lista_perguntas_labels = dict()
    for item in lista_content['content']['survey']:
        if 'select_from_list_name' in item:
            for pergunta in lista_content['content']['choices']:
                if pergunta['list_name'] in item['select_from_list_name']:
                    lista_perguntas_labels[item['label'][0]] = pergunta['label'][0]
    for resposta in lista_grupamento:
        for key, value in lista_perguntas_labels.items():
            for chave, valor in resposta.items():
                if isinstance(valor, list):
                    for awnser in valor:
                        if key in awnser:
                            awnser[key] = value
                else:
                    if key in resposta:
                        resposta[key] = value
    return lista_grupamento
def filtra_labels_perguntas_grupamento(lista_grupamento):
    global lista_content
    labels_dict = dict()
    for item in lista_content['content']['survey']:
        if 'label' in item:
            labels_dict[item['$autoname']] = item['label']
    for enquete in lista_grupamento:
                for key, value in labels_dict.items():
                    if key in enquete:
                        enquete[value[0]] = enquete.pop(key)
    return lista_grupamento


def importar_xls_grupamento_para_lista(u_r_l, u_s_e_r, p_a_s_s_w_o_r_d,i_d):
    req = requests.get(u_r_l, auth=(u_s_e_r, p_a_s_s_w_o_r_d))
    file = "formulario.xls"
    with open('formulario.xls', 'wb') as output:
        output.write(req.content)
    workbook = xlrd.open_workbook('formulario.xls')

    main_sheet = workbook.sheet_by_index(0)
    main_linhas = main_sheet.nrows
    main_colunas = main_sheet.ncols
    table = list()

    for x in range(1, main_linhas):
        record = dict()
        for y in range(main_colunas):
            if main_sheet.cell(x, y).value:
                if '/' in main_sheet.cell(0, y).value:
                    a = main_sheet.cell(0, y).value.split('/')
                    record[a[len(a) - 1]] = main_sheet.cell(x, y).value
                else:
                    record[main_sheet.cell(0, y).value] = main_sheet.cell(x, y).value
        if record:
            table.append(record)
    total = 1
    if workbook.nsheets < 2:
        try:
            os.remove(file)
        except OSError as e:
            print("Error %s - %s" % (e.filename, e.strerror))
        return table
    else:
        while total <= workbook.nsheets - 1:
            linhas = workbook.sheet_by_index(total).nrows
            colunas = workbook.sheet_by_index(total).ncols
            table_grupamento = list()


            for x in range(1, linhas):
                record = dict()
                for y in range(colunas):
                    if workbook.sheet_by_index(total).cell(x, y).value:
                        if '/' in workbook.sheet_by_index(total).cell(0, y).value:
                            a = workbook.sheet_by_index(total).cell(0, y).value.split('/')
                            record[a[len(a) - 1]] = workbook.sheet_by_index(total).cell(x, y).value
                        else:
                            record[workbook.sheet_by_index(total).cell(0, y).value] \
                                = workbook.sheet_by_index(total).cell(x, y).value
                if record:
                    table_grupamento.append(record)
            table_grupamento = filtra_labels_perguntas_grupamento(table_grupamento)
            table_grupamento = filtra__labels_respostas_grupamento(table_grupamento)
            for ele in table_grupamento:
                for element in table:
                    if element['_index'] == ele['_parent_index']:
                        key_value = dict()
                        for key, value in ele.items():
                                key_value[key] = value
                        element.setdefault(workbook.sheet_by_index(total).name, [])
                        element[workbook.sheet_by_index(total).name].append(key_value)
            total = total + 1
        return table

def retorna_lista_perguntas(u_r_l, i_d, u_s_e_r, p_a_s_s_w_o_r_d):
    enquetes_respondidas = retorna_respostas_com_labels(u_r_l, i_d, u_s_e_r, p_a_s_s_w_o_r_d)
    lista = list()
    for enquete in enquetes_respondidas:
        for key, value in enquete.items():
            if key not in lista:
                lista.append(key)

    return lista

