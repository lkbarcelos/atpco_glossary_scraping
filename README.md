# atpco_glossary_scraping  
## Objetivo  
Extrair informações do glossário de termos do ATPCO, realizando a limpeza destes dados, sua tradução para PT-BR e estruturação em um arquivo markdown.

## Contexto
O ATPCO é um ator central na indústria da aviação, fornecendo dados e padrões cruciais que permitem o funcionamento eficiente da precificação e distribuição de passagens aéreas globalmente. Seu glossário é útil para entendimento de termos utilizados pelo ATPCO e na indústria aéra como um todo, possibilitando melhor compreensão de seus significados e contextos.

## Libs Usadas
- selenium: Para realizar a interação com o site dinâmico;
- webdriver-manager: Para uso de web drivers sem a necessidade de download, instalação e atualizações manuais;
- fake-useragent: Gerador de useragents aleatórios;
