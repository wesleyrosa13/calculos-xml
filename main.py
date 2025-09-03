import xml.etree.ElementTree as ET
import pandas as pd
import os
import shutil
from datetime import datetime

# --- FUNÇÕES AUXILIARES ---
def obter_texto_xml(elemento, nome_tag, uri_namespace):
    if elemento is None:
        return ''
    elemento_encontrado = elemento.find(f'{uri_namespace}{nome_tag}')
    return elemento_encontrado.text.strip() if elemento_encontrado is not None and elemento_encontrado.text else ''

def float_seguro(valor_str):
    try:
        if valor_str == '':
            return 0.0
        return float(str(valor_str).replace(',', '.'))
    except (ValueError, TypeError):
        return 0.0

def calcular_custo_item(dados_item, aliquota_difal_fixa):
    vProd = float_seguro(dados_item.get('vProd', '0.0'))
    qCom = float_seguro(dados_item.get('qCom', '0.0'))
    vDesc = float_seguro(dados_item.get('vDesc', '0.0'))
    vIPI = float_seguro(dados_item.get('vIPI', '0.0'))
    vICMSST = float_seguro(dados_item.get('vICMSST', '0.0'))
    cst_icms = dados_item.get('CST_ICMS', 'N/A')

    custo_base_sem_desconto = vProd + vIPI
    valor_difal_aplicado = 0.0
    valor_icms_st_aplicado = 0.0
    regra_aplicada = "N/A"

    if vICMSST > 0:
        custo_com_impostos_adicionais = custo_base_sem_desconto + vICMSST
        valor_icms_st_aplicado = vICMSST
        regra_aplicada = "C/ ICMS ST Destacado (Base: Prod+IPI)"
    else:
        valor_difal_aplicado = custo_base_sem_desconto * aliquota_difal_fixa
        custo_com_impostos_adicionais = custo_base_sem_desconto + valor_difal_aplicado
        regra_aplicada = f"S/ ICMS ST (DIFAL {aliquota_difal_fixa*100:.0f}% sobre Prod+IPI)"

    custo_total_item = custo_com_impostos_adicionais - vDesc
    custo_unitario_final = custo_total_item / qCom if qCom > 0 else 0.0

    return {
        'Produto': dados_item.get('xProd', 'N/A'),
        'NCM': dados_item.get('NCM', 'N/A'),
        'EAN': dados_item.get('cEAN', 'N/A'),
        'CST_ICMS': cst_icms,
        'Codigo_Produto_XML': dados_item.get('cProd', 'N/A'),
        'Qtd': qCom,
        'Valor Prod NF': vProd,
        'Valor IPI': vIPI,
        'Valor Desconto Item': vDesc,
        'Valor ICMS ST NF (Aplicado)': valor_icms_st_aplicado,
        'Valor DIFAL (Aplicado)': valor_difal_aplicado,
        'Regra Aplicada': regra_aplicada,
        'Custo Total Item (Calculado)': custo_total_item,
        'Custo Unitario Final (Calculado)': custo_unitario_final
    }

def processar_xml_nota(caminho_xml, aliquota_difal_fixa):
    try:
        arvore = ET.parse(caminho_xml)
        raiz = arvore.getroot()
        uri_namespace = ''
        if '}' in raiz.tag:
            uri_namespace = raiz.tag.split('}')[0] + '}'
        if not uri_namespace or "portalfiscal.inf.br/nfe" not in uri_namespace:
            uri_namespace = '{http://www.portalfiscal.inf.br/nfe}'

        itens_calculados = []

        for det in raiz.findall(f'.//{uri_namespace}det'):
            prod = det.find(f'{uri_namespace}prod')
            imposto = det.find(f'{uri_namespace}imposto')

            dados_item = {'vIPI':'0.0','CST_ICMS':'000','vICMSST':'0.0','vDesc':'0.0'}

            if prod is not None:
                dados_item['xProd'] = obter_texto_xml(prod, 'xProd', uri_namespace)
                dados_item['NCM'] = obter_texto_xml(prod, 'NCM', uri_namespace)
                dados_item['vProd'] = obter_texto_xml(prod, 'vProd', uri_namespace)
                dados_item['qCom'] = obter_texto_xml(prod, 'qCom', uri_namespace)
                dados_item['vDesc'] = obter_texto_xml(prod, 'vDesc', uri_namespace)
                dados_item['cProd'] = obter_texto_xml(prod, 'cProd', uri_namespace)
                dados_item['cEAN'] = obter_texto_xml(prod, 'cEAN', uri_namespace)
                if dados_item['cEAN'] == '':
                    dados_item['cEAN'] = obter_texto_xml(prod, 'cEANTrib', uri_namespace)

            if imposto is not None:
                ipi_tag = imposto.find(f'{uri_namespace}IPI')
                if ipi_tag is not None:
                    ipi_subtag = ipi_tag.find(f'{uri_namespace}IPITrib') or ipi_tag.find(f'{uri_namespace}IPINT')
                    if ipi_subtag is not None:
                        dados_item['vIPI'] = obter_texto_xml(ipi_subtag, 'vIPI', uri_namespace)
                icms_tag = imposto.find(f'{uri_namespace}ICMS')
                if icms_tag is not None:
                    for icms_subtag in icms_tag:
                        cst_icms_nome_completo_tag = icms_subtag.tag.replace(uri_namespace, '')
                        if cst_icms_nome_completo_tag.startswith('ICMS'):
                            dados_item['CST_ICMS'] = cst_icms_nome_completo_tag.replace('ICMS', '')
                        elif cst_icms_nome_completo_tag.startswith('ICMSSN'):
                            dados_item['CST_ICMS'] = cst_icms_nome_completo_tag.replace('ICMSSN', '')
                        else:
                            dados_item['CST_ICMS'] = 'N/A_CST'
                        dados_item['vICMSST'] = obter_texto_xml(icms_subtag, 'vICMSST', uri_namespace)
                        break
            resultado_item = calcular_custo_item(dados_item, aliquota_difal_fixa)
            itens_calculados.append(resultado_item)

        return itens_calculados

    except Exception as e:
        print(f"Erro ao processar {caminho_xml}: {e}")
        return []

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    try:
        aliquota_input = input("Digite a alíquota DIFAL em % (ex: 14 para 14%): ").replace(',', '.')
        ALIQUOTA_DIFAL_FIXA = float(aliquota_input)/100
    except:
        print("Valor inválido. Usando alíquota padrão de 14%")
        ALIQUOTA_DIFAL_FIXA = 0.14

    PASTA_XMLS_ENTRADA = 'XMLsEntrada'
    PASTA_XMLS_PROCESSADOS = 'XMLsProcessados'
    PASTA_PLANILHAS_RETORNADAS = 'Planilhas'

    os.makedirs(PASTA_XMLS_PROCESSADOS, exist_ok=True)
    os.makedirs(PASTA_PLANILHAS_RETORNADAS, exist_ok=True)

    todos_os_resultados = []

    xmls_na_pasta = [f for f in os.listdir(PASTA_XMLS_ENTRADA) if f.lower().endswith('.xml')]
    print(f"Encontrados {len(xmls_na_pasta)} arquivos XML para processar.")

    for nome_arquivo in xmls_na_pasta:
        caminho_xml = os.path.join(PASTA_XMLS_ENTRADA, nome_arquivo)
        print(f"Processando {nome_arquivo}...")
        resultados_do_xml = processar_xml_nota(caminho_xml, ALIQUOTA_DIFAL_FIXA)
        if resultados_do_xml:
            todos_os_resultados.extend(resultados_do_xml)
            shutil.move(caminho_xml, os.path.join(PASTA_XMLS_PROCESSADOS, nome_arquivo))

    if todos_os_resultados:
        df_resultados = pd.DataFrame(todos_os_resultados).round(2)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_excel = os.path.join(PASTA_PLANILHAS_RETORNADAS, f'Custos_{timestamp}_Detalhes.xlsx')
        df_resultados.to_excel(nome_excel, sheet_name='Detalhe por Item', index=False)
        print(f"\nPlanilha gerada: {nome_excel}")
    else:
        print("Nenhum dado processado.")
