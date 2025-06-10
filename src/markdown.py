import json

# Lê os arquivos JSON de entrada e transforma em um dicionário
with open('data/raw_data_glossary.json', 'r', encoding='utf-8') as f:
    raw_data = dict(json.load(f))

with open('data/translated_data_glossary.json', 'r', encoding='utf-8') as f:
    translated_data = dict(json.load(f))

# Consolida os dicionários em uma string
consolidated_string = '# Glossário de Termos do ATPCO '
for letter, terms in raw_data.items(): 
    consolidated_string += f'\n\n## {letter.upper()} '
    for term, definition in terms.items():
            try:
                # Acessa a definição traduzida do termo
                translated_definition = translated_data[letter][term]['definition (pt-br)']
                raw_definition = definition['definition']
                # Adiciona o termo e a definição à string consolidada
                consolidated_string += f'\n### {term} '
                consolidated_string += f'\n- **definition:** {raw_definition} '
                consolidated_string += f'\n- **definition (pt-br):** {translated_definition} \n'
            except KeyError:
                print(f'Erro ao acessar a chave "{term}" no dicionário translated_data.')

# Salva a string consolidada em um arquivo Markdown
with open('data/glossary_consolidated.md', 'w', encoding='utf-8') as f:
    f.write(consolidated_string)
    print('Glossário consolidado salvo em "data/glossary_consolidated.md".')


