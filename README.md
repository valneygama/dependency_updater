# Dependency Updater

Script [Python](https://www.python.org/) de atualização de dependências entre servidores [Maven](https://maven.apache.org/).

## Configuração
1. A aplicação necessita que estejam instalados e disponíveis para execução:
   - [Python 3](https://www.python.org/)
   - [Maven](https://maven.apache.org/)

2. O arquivo settings.xml precisa ser editado com as configurações de login e senha do servidor maven destino, e precisa ser posicionado no diretório *~/.m2* do usuário que estiver executando. Ou seja, em <code>C:/Users/$USERNAME/.m2/settings.xml</code> em *ambiente Windows* ou <code>/home/$USER/.m2/settings.xml</code> em *ambiente Unix*.
    ```xml
    <!-- settings.xml -->
    <settings>
    <servers>
        <server>
        <id>maven-releases</id>
        <username>__LOGIN__</username>
        <password>__PASSWORD__</password>
        </server>
    </servers>
    </settings>
    ```

3. O arquivo de entrada (exemplificado pelo dependencies.xml) deverá conter a lista de dependências a serem movidas, no formato padrão de pacotes do maven:
    ```bash
    # br.com.empresa:artefato:extensao:versao
    br.com.empresa:meuArtefatoJava:jar:1.0.1
    ```
    > **Observação**: O arquivo de entrada não aceita comentários de qualquer tipo.

## Rodando: Como Funciona?
```bash
# Forma de Execução
$ python3 update_dependencies.py arquivo origem destino
# Exemplo:
$ python3 update_dependencies.py dependencies.txt https://repo1.maven.org/maven2/ http://mavendestino.minhaempresa.com.br/
```
1. O script lê o **arquivo** de entrada, reconhecendo todas as dependências que precisarão de atualização.
2. Para cada dependência, o script pesquisará se o ela existe na **origem** via urls REST. Se existir, baixa o arquivo no formato *Artefato-Versao.extensão*.
    -   Se um arquivo neste formato representando um artefato já existir em download, ele não efetua download (para economizar recursos).
3. Para cada dependência com arquivo baixado, efetua o upload via comando <code>mvn deploy:deploy-file</code>. Para a execução deste comando, é necessário um arquivo *pom.xml* (incluído no projeto). Este arquivo contém um projeto falso, que não compila (*Unknown lifecycle phase ""*). Mesmo não compilando, é suficiente para que o artefato seja submetido e copiado para o *destino*. 

Por fim, o script finaliza.


## TODOS:
 - Ajustar pom.xml para que a build ocorra normalmente, evitando erros de entendimento.
 - Aceitar comentários no arquivo de entrada
 - Alterar padrão de formato de arquivo baixado para <code>org.artefato-versão.extensao</code>.

---

## Exemplificando:

Dependencies.txt
```
org.apache.commons:commons-math:jar:1.2
br.com.myorg:myartifact:jar:1.0.0
```
Script:
```
python3 update_dependencies.py dependencies.txt https://repo1.maven.org/maven2/ http://mavendestino.minhaempresa.com.br/
```
