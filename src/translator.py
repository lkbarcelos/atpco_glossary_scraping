import json
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai

# Carrega as variáveis do arquivo .env
load_dotenv()  
api_key = os.getenv("GEMINI_API_KEY")

# Configura a chave da API do Gemini
genai.configure(api_key=api_key)

# Função para extrair o JSON do retorno do Gemini
def extract_json_from_text(text):
    """
    Captura o conteúdo de um JSON dentro de um texto, considerando o primeiro '{' e o último '}'.
    """
    pattern = r'\{.*\}'
    match = re.search(pattern, text, re.DOTALL)  # DOTALL permite capturar múltiplas linhas

    return match.group() if match else None

# função que valida o retorno do Gemini
def validate_gemini_response(dict_to_translate, response):
    # Verifica se response.text não está vazio
    if response.text.strip():
        try:
            # Extrai o JSON do texto da resposta
            response_prep = extract_json_from_text(response.text)
            # Tenta carregar a resposta como JSON
            json_translated = json.loads(response_prep)
            # Converte o texto traduzido de volta para um dicionário
            dict_translated = dict(json_translated)
        except json.JSONDecodeError:
            print(f'Erro ao decodificar JSON: Resposta inválida. \nResposta recebida: {response.text}')
            dict_translated = {}
    else:
        print(f'Erro: Resposta do modelo está vazia. \nResposta recebida: {response.text}')
        dict_translated = {}

    # Lista as chaves que não estão presentes no dicionário traduzido
    missing_keys = [key for key in dict_to_translate if key not in dict_translated]
    if missing_keys:
        is_valid = False
        correction_prompt = f'''
        O JSON traduzido não contém as seguintes chaves do JSON original: {';'.join(missing_keys)}.
        Retorne única e exclusivamente um JSON completo, traduzido e corrigido, mantendo as chaves originais e traduzindo apenas os valores presentes em "definition".
        '''
        return dict_translated, is_valid, missing_keys, correction_prompt
    else:
        is_valid = True
        correction_prompt = None
        return dict_translated, is_valid, missing_keys, correction_prompt

# Função para novamente tentar traduzir o dicionário caso a resposta do Gemini não seja válida
def retry_translate(is_valid, missing_keys, correction_prompt, dict_to_translate, dict_translated, model, response):
    dict_translated, is_valid, missing_keys, correction_prompt = validate_gemini_response(dict_to_translate, response)
    count_try = 0
    while not is_valid or count_try < 3:
        count_try += 1
        print(f"\tErro: O JSON traduzido não contém as seguintes chaves: {missing_keys}")
        # Aplica um novo prompt de correção
        response = model.generate_content(correction_prompt)
        
        # Valida a resposta do Gemini para a nova tentativa
        dict_translated, is_valid, missing_keys, correction_prompt = validate_gemini_response(dict_to_translate, response)
        
        if not is_valid:
            print(f"\t\tTentativa {count_try}: O JSON traduzido ainda não está correto. Chaves faltantes: {missing_keys}")
        else:
            print(f"\t\tTentativa {count_try}: O JSON traduzido está correto.")
    
    if is_valid:
        return dict_translated
    else:
        raise ValueError(f"Erro: O JSON traduzido ainda não está correto após {count_try} tentativas. Chaves faltantes: {missing_keys}")

# Função que traduz um texto usando o Gemini
def translate_dict_with_gemini(dict_to_translate):
    # Converte o dicionário para uma string JSON
    json_string = json.dumps(dict_to_translate, ensure_ascii=False)
    
    # Define o modelo e o contexto para a tradução
    model = genai.GenerativeModel('gemini-2.0-flash')
    context = 'Você é um tradutor especializado em termos de aviação. Sua tarefa é traduzir a definições do inglês para o português do Brasil, mantendo a precisão técnica e o contexto específico da aviação.'
    task = 'Com base nos itens "definition" do JSON fornecido, retorne o mesmo JSON subistituindo os itens "definition" por "definition (pt-br)" e traduzido seu para o português do Brasil. Os demais itens devem permanecer inalterados e o resultado deve ser única e exclusivamente um JSON completo.'
    
    # Cria o prompt
    prompt = f'''
        Contexto: {context}\n
        Tarefa: {task}\n
        JSON:\n{json_string}
    '''
    
    # Gera o conteúdo traduzido usando o modelo Gemini
    response = model.generate_content(prompt)

    # Valida a resposta do Gemini
    dict_translated, is_valid, missing_keys, correction_prompt = validate_gemini_response(dict_to_translate, response)

    # Se a resposta não for válida, tenta corrigir com o prompt de correção
    if not is_valid:
        dict_translated = retry_translate(is_valid, missing_keys, correction_prompt, dict_to_translate, dict_translated, model, response)
    
    return dict_translated


# Carrega o dicionário de termos a serem traduzidos
with open('data/raw_data_glossary.json', 'r', encoding='utf-8') as f:
    raw_data = dict(json.load(f))

# Cria um dicionário para armazenar os termos traduzidos
translated_terms = {}

# Itera sobre cada letra do dicionário
for letter, terms in raw_data.items():
    print(f'Processando letra "{letter}" com {len(terms)} termos...')
    
    # Traduz os termos usando o Gemini
    translated_terms[letter] = translate_dict_with_gemini(terms)

# Salva o dicionário traduzido em um arquivo JSON
with open('data/translated_data_glossary.json', 'w', encoding='utf-8') as f:
    json.dump(translated_terms, f, ensure_ascii=False, indent=2)

