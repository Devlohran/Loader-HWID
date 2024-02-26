# Loader-HWID

Este projeto consiste em um banco de dados, página de cadastro e loader HWID para gerenciar suas aplicações Python em ambiente de produção. Ele permite controlar o uso de seus scripts por meio de chaves e verificação HWID.

## Funcionalidades

- **Banco de Dados:** Execute o script "bancodedados.py" para criar o banco de dados necessário para armazenar informações como chaves, HWID dos usuários e o nome do usuário.

- **Gerenciamento de Chaves:** Utilize o menu robusto com interface gráfica disponível em "keys.py" para gerar e manipular chaves. Este aplicativo deve ser mantido em sigilo, pois vazar seu conteúdo pode comprometer a segurança de suas aplicações.

- **Cadastro de Usuários:** Os usuários devem receber uma chave gerada por você para se cadastrar através do script "cadastroback.py". Uma proteção básica contra CSRF foi implementada no script python e no menu front basico, mas é recomendável adicionar medidas adicionais de segurança e melhorar o frontend.

- **Login:** Implemente sua aplicação na função "fazer_login" em "login.py" (a primeira vez que é executado o script, ele pega o hwid do usuario e salva no banco de dados. Então fale para usuario garantir que esta no computador que vai usar o script). Este script conta com proteções contra depuração usando a biblioteca "guardshield", login automático e um menu básico. É aconselhável adicionar verificações de hash para manter a integridade do sistema e implementar mais medidas de segurança. O loader deve ser executado com privilégios de administrador para realizar a verificação HWID.

- **Gerenciamento de Tempo de Chave:** Inclua em seu servidor o script "initservidor.py" para fazer o gerenciamento de tempo de chave e apagá-las quando o tempo delas terminar.

## Como usar

1. Clone o repositório.
2. Execute "bancodedados.py" para criar o banco de dados.
3. Utilize "keys.py" para gerenciar chaves.
4. Envie chaves para os usuários se cadastrarem via "cadastroback.py".
5. Implemente sua aplicação na função "fazer_login" em "login.py".
6. Execute o loader com privilégios de administrador para fazer a verificação HWID.

## Segurança

- Mantenha os scripts sensíveis, como "keys.py" e "cadastroback.py", em sigilo para garantir a segurança do sistema.
- Adicione medidas de segurança adicionais conforme necessário para proteger contra ataques.

## Notas

Este projeto é uma solução inicial e pode exigir personalização adicional para atender às suas necessidades específicas de segurança e funcionalidade. Provavelmente você vai ter que mudar a função 'conectar_bd' nos scripts quando você colocar em servidor. Também será necessário mudar o cadastroback.py, pois ele está configurado para ser executado localmente. Voce tambem pode criar um loader com outra linguagem, aproveitando o sistema de gerenciamento de key e o banco de dados seguindo o exemplo do loader que eu fiz.
