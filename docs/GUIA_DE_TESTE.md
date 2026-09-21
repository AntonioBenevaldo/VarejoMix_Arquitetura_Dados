# VarejoMix V2 - refazer o trabalho e os testes

Este guia permite reproduzir o pacote corrigido em outra instalação. A execução local das 20:39 UTC foi validada, incluindo os EXPLAIN MongoDB. Este guia permite reproduzir o trabalho para estudo; não há pendência de repetição dos testes. Faça uma etapa por vez. Se aparecer erro, guarde uma captura da mensagem inteira antes de prosseguir.

## 1. Preparar a pasta

1. Baixe o ZIP corrigido.
2. Clique com o botão direito e escolha **Extrair Tudo**.
3. Extraia em uma pasta nova, como `VarejoMix_V2`, na Área de Trabalho.
4. Abra a pasta extraída até encontrar `01_PREPARAR_WINDOWS.bat`, `README.md` e `docker-compose.yml` juntos.

Mantenha a pasta anterior guardada. A V2 usa PostgreSQL 5434 e MongoDB 27018. Duas pastas da V2 no mesmo computador compartilham o projeto Docker `varejomix` e seus volumes; uma pasta nova não cria um banco independente. Não copie o ambiente virtual de outra instalação.

## 2. Abrir o Docker Desktop

Abra o Docker Desktop e aguarde o mecanismo terminar de iniciar. A primeira execução precisa baixar as imagens e pode demorar. O projeto usa PostgreSQL 16 e MongoDB 7.

## 3. Preparar Python e bancos

Dê dois cliques em **01_PREPARAR_WINDOWS.bat**.

O arquivo verifica Python e Docker, cria o ambiente virtual, instala as dependências e inicia os bancos. Aguarde:

```text
PREPARACAO CONCLUIDA. Execute agora 02_TESTAR_WINDOWS.bat.
```

Se pedir que pressione uma tecla após a conclusão, pressione qualquer tecla. A primeira preparação é mais demorada; as próximas reutilizam as instalações e os dados.

## 4. Executar os testes completos

Dê dois cliques em **02_TESTAR_WINDOWS.bat**.

| Etapa mostrada | O que ela verifica |
|---|---|
| 1/6 | Serviços Docker disponíveis. |
| 2/6 | Integridade, consultas SQL e EXPLAIN antes/depois do índice. |
| 3/6 | Eventos MongoDB iguais ao JSON e compras conciliadas com PostgreSQL. |
| 4/6 | Funil de conversão, rankings e planos no MongoDB. |
| 5/6 | Notebook inteiro conectado ao PostgreSQL. |
| 6/6 | Contagens finais e registros reais de auditoria. |

Ao terminar corretamente, aparecerá:

```text
APROVADO: evidencias em evidencias/local; dataset em outputs; notebook atualizado.
```

Após a correção de 20/09, o arquivo testes_regressao.txt deve registrar 11 testes com OK, e mongo_local.txt deve conter VAREJOMIX_MONGO_CONSULTAS_CONCLUIDAS sem erros. O comando deve terminar sem `Traceback`, `AssertionError` ou mensagem de falha. A abertura de uma tela ou de um arquivo sozinha não comprova que os testes passaram.

## 5. Conferir o resultado esperado

| Conferência | Valor V2 |
|---|---:|
| Pedidos | 5.000 |
| Itens | 10.068 |
| Vendas confirmadas | 4.730 |
| Valor confirmado | R$ 2.688.893,36 |
| Eventos | 1.088 |
| Sessões | 500 |
| Compras no funil | 78 |
| Dataset | 162 linhas e 13 colunas |
| Recompra = 0 | 41 clientes |
| Recompra = 1 | 121 clientes |
| Nulos e IDs repetidos no dataset | Zero |

O EXPLAIN consulta 285 pedidos entregues no período definido. Tempo, buffers e escolha de plano podem variar com a versão, estatísticas, memória e máquina; não force um plano para imitar a revisão. Registre e explique o resultado local.

A tabela de auditoria começa vazia e recebe uma linha por tentativa de exportação iniciada. Depois de várias execuções, ela terá várias linhas. Isso é esperado.

## 6. Abrir e estudar no JupyterLab

1. Dê dois cliques em **03_ABRIR_JUPYTERLAB.bat**.
2. Mantenha a janela do terminal aberta.
3. No navegador, abra a pasta `notebooks` e o arquivo `analise_recompra.ipynb`.
4. O notebook já terá as saídas produzidas pelo teste. Leia as premissas e a consulta SQL.
5. Para repetir tudo, escolha **Run > Run All Cells**.
6. Aguarde desaparecer o indicador de execução e confira `CONCLUIDO: dataset exportado e auditado.`.
7. Salve com **Ctrl+S**.

Não cole comandos PowerShell dentro das células Python. Os comandos de terminal ficam neste guia; as células do notebook já estão preparadas.

## 7. Onde estão as evidências

- `evidencias/local/06_validacoes.txt`: sete verificações com zero erros e teste do custo histórico aprovado.
- `evidencias/local/04_queries.txt`: consultas analíticas.
- `evidencias/local/05_index_explain.txt`: plano sem e com índice.
- `evidencias/local/eventos_reconciliados.json`: comparação com o MongoDB e reconciliação das 78 compras.
- `evidencias/local/mongo_local.txt`: saídas do funil e dos planos.
- `evidencias/local/notebook_executado.html`: notebook executado, aberto no navegador.
- `evidencias/local/auditoria.json`: fotografia com cinco exportações SUCCESS registradas na coleta de 20/09/2026, por volta de 20:39 UTC.
- `evidencias/local/LEIA_ME.md`: identificação da coleta atual, dos doze snapshots preservados e dos prints atuais e históricos.
- `evidencias/local/prints/Testes_Funcionamento_VarejoMix.docx`: capturas organizadas para apresentação.
- `outputs/customer_repurchase_features.csv` e `.parquet`: dataset mais recente.
- `outputs/manifesto.json`: corte, versão, shape, hashes e origem.
- `outputs/execucoes/`: cópias preservadas de cada exportação.

`evidencias/revisao/` documenta a revisão feita durante a correção, com PostgreSQL embarcado e execução das células por IPython. As evidências do seu computador devem ficar em `evidencias/local/`.

## 8. Fazer capturas para apresentar

Capture a conclusão dos testes, uma consulta SQL, o EXPLAIN, o funil MongoDB e a última célula do notebook. Evite capturar o endereço do Jupyter com token. Guarde as imagens em `evidencias/local/prints`.

Para atualizar o HTML depois de executar manualmente o notebook, rode novamente `02_TESTAR_WINDOWS.bat`; ele executa e exporta o notebook inteiro.

## 9. Completar os links da entrega

O Word preserva o nome do aluno e do professor encontrados no arquivo original. Confira a identificação, incluindo a necessidade de RA/turma segundo a instituição. Preencha os links reais do repositório e do vídeo no Word e no README. Exporte o Word novamente para PDF e mantenha entre **6 e 10 páginas**.

Para o repositório, crie/atualize uma pasta de projeto acessível ao professor, seguindo as regras da disciplina. Inclua código, documentação e evidências. Não envie ambiente virtual, caches, arquivo `.env` com configurações particulares nem dependências instaladas. O ZIP técnico inclui os artefatos; o repositório exige endereço próprio.

## 10. Gravar o vídeo

Use `ROTEIRO_VIDEO.md`. Mostre a arquitetura e as evidências reais do seu computador. Duração máxima: quatro minutos. Publique no YouTube conforme a exigência do enunciado; pode ser não listado. Coloque o endereço no README e no PDF.

## 11. Encerrar e retomar

Feche o JupyterLab com **Ctrl+C** no terminal e confirme, se solicitado. Execute **04_ENCERRAR_WINDOWS.bat** para parar os bancos mantendo os volumes.

Em outro dia, abra o Docker Desktop, execute `01_PREPARAR_WINDOWS.bat` e depois `03_ABRIR_JUPYTERLAB.bat`. Para atualizar evidências, use `02_TESTAR_WINDOWS.bat`.

## Problemas comuns

| Mensagem ou situação | O que fazer |
|---|---|
| Python não encontrado | Instale Python, habilitando a opção de adicionar ao PATH, e abra um novo terminal. |
| Docker não encontrado ou daemon indisponível | Abra o Docker Desktop e aguarde; confira a instalação. |
| Porta 5434/27018 ocupada | Envie a mensagem de erro para ajustar as portas do Compose e do `.env` em conjunto. |
| A carga continua com os números antigos | Confira se abriu a pasta V2. O Compose da V2 usa o projeto `varejomix`. |
| `ModuleNotFoundError` | Execute novamente o preparador; use o lançador do JupyterLab desta pasta. |
| `AssertionError` de eventos ou dados | Pare e envie a captura. Não edite o resultado esperado para fazer o teste passar. |
| Nada abre no navegador | Copie o endereço local mostrado pelo terminal do JupyterLab para o navegador, sem compartilhá-lo. |
| Corte sem cobertura de 90 dias | Use o corte padrão `2025-10-01`; a carga vai até dezembro/2025. |

Não é necessário apagar volumes para repetir consultas e notebook. Uma recriação de banco só deve ser feita se for preciso recarregar o schema/carga da V2 e depois de preservar o que você deseja guardar.
