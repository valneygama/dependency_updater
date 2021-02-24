#!/usr/bin/python3

## script que, a partir dos elementos separados por virgula, faz os passos seguintes:
## Descobrir arquivos faltantes
#### Executar CURL pra conseguir infos sobre o artifact
#### baixar o jar a partir da url de arquivo disponibilizada no CURL
#### utilizar mvn deploy na url nova
#### Testar o app

import sys, requests, glob, subprocess

def get_dependencies_data(dependencies):
    data = []
    for dep in dependencies:
        dep_data = dep.split(":")
        #br.com.infowaypi:ClienteMec:jar:1.3.3.1:  // org : file : extension : version
        if len(dep_data)>3:
            data.append({
                'data': dep,
                'id': dep_data[1].strip(),
                'org': dep_data[0].strip(),
                'extension': dep_data[2].strip(),
                'version': dep_data[3].strip(),
                'location': "./download/"+dep_data[1].strip()+"-"+dep_data[3].strip()+"."+dep_data[2].strip(),
                'file': None
            })
            print("  -> dependency read: " + dep)
    return data

def search_file(dependency):
    find = glob.glob(dependency["location"])
    if len(find)>0:
        print("  -> located offline file "+dependency["location"]+" for dependency "+dependency["data"])
        dependency["file"] = dependency["location"]
        return dependency["location"]
    return None
    
def get_dependency_file(endereco, dependency):
    if dependency["file"] is None:
        get_data = "?group="+dependency['org']+"&name="+dependency['id']+"&maven.extension="+dependency['extension']+"&version="+dependency['version']
        search_url = "/service/rest/v1/search/assets"
        download_url = "/service/rest/v1/search/assets/download"
        url = endereco + download_url + get_data
        retorno = requests.get(url, allow_redirects=True)
        if retorno.status_code==200:
            open(dependency['location'], 'wb').write(retorno.content)
            print("  -> downloaded file " + dependency['location'])
            dependency['file'] = dependency['location']
            return dependency['location']
        else:
            print("  -> could not find dependency " + dependency['data'] + ", status code = " + str(retorno.status_code))
            return None
    else:
        print("  -> skipping "+dependency["data"])

def deploy_new_dependency(endereco, dependency):
    if dependency["file"] is None:
        print("  -> could not upload dependency "+dependency["data"])
        return False
    else:
        print("  -> deploying dependency "+dependency["data"])
        command  = "mvn deploy:deploy-file " 
        command += " -DgroupId="+dependency["org"]
        command += " -DartifactId="+dependency["id"]
        command += " -Dversion="+dependency["version"]
        command += " -Dpackaging="+dependency["extension"]
        command += " -Dfile="+dependency["file"]
        command += " -DgeneratePom=true -DrepositoryId=maven-releases"
        command += " -Durl=" + endereco + "/repository/maven-releases/"
        dependency["command"] = command
        subprocess.run(command.split(" "))
        return command

def is_up(url):
    retorno = requests.get(url)
    return retorno.status_code != 404

def main(): 
    # le variaveis
    if len(sys.argv)<4:
        print("Faltam Argumentos. Ex.: python script.py arquivo url_original url_destino")
        return   
    
    # reading args
    origem = sys.argv[2]
    destino = sys.argv[3]
    dep_arquivo = open(sys.argv[1], "r")

    print("# reading dependencies")
    dependencies = []
    for line in dep_arquivo:
        dependencies.append(line.strip())
    dependencies = get_dependencies_data(dependencies)
    print()

    print("# searching files locally by artifact id")
    for dependency in dependencies:
        search_file(dependency)
    print()

    print("# searching files in origin", origem)
    for dependency in dependencies:
        get_dependency_file(origem, dependency)
    print()

    print("# uploading new artifacts to destination", destino)
    for dependency in dependencies:
        dependency["update_result"] = deploy_new_dependency(destino, dependency)
    print()

    print("# commands log")
    for dependency in dependencies:
        if (dependency["update_result"] != True and dependency["update_result"] != False): 
            print(dependency["update_result"])
            
## GO    
main()