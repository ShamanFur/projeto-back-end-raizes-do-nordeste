# Projeto da faculdade UNINTER da trilha Back End "Raizes Do Nordeste"

## Sobre o projeto: O projeto usa um cenário real de mercado com o uso de uma rede de lanchonetes em expansão e tem como objetivo avaliar a capacidade dos alunos de analisar e solucionar os problemas e questões propostas como criar o modelo de casos, implementar API e outros. 

## Requisitos e Dependencias:
Python 3.13+
MySQL 8.0
pip (gerenciador de pacotes do Python)
Git
Todas as dependências estão listadas no arquivo `requerimentos.txt`.
Para instalar todas de uma vez segue o passo a passo do proximo bloco:

## Configurando o ambiente

1- Clone o repositorio do git:
```bash
git clone https://github.com/ShamanFur/projeto-back-end-raizes-do-nordeste.git
```

2- Para criar e ativar o ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate
```

3- Instale as dependencias(tudo no arquivo 'requerimentos.txt'):
```bash
pip install -r requerimentos.txt
```

4- Configure o arquivo `.env` se baseando no `.env.example`:
```env
DATABASE_URL=mysql+pymysql://root:senha@localhost:3306/nome_do_banco_projeto
SECRET_KEY=coloque-sua-chave-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Banco de dados

1. Crie o banco no MySQL:
```sql
CREATE DATABASE projeto_raizes_nordeste CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
2.Para acessar como ADMIN crie no MySQL e apos isso faça login com a senha(god123) no Swegger:
```sql
UPDATE usuarios SET perfil = 'ADMIN' WHERE email = 'dono@gmail.com';
```
3. Execute as migrations:
```bash
alembic upgrade head
```

## Inicie a API

```bash
uvicorn main:app --reload
```

## Acesse a documentação

Após iniciar a API acesse:
- **Swagger**: http://127.0.0.1:8000/docs
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

## Executando os testes

1- Importe o arquivo `Projeto Raizes Do Nordeste.postman_collection.json` no Postman
2- Execute o **T01 - Login valido** primeiro para que possa gerar o token e caso expire é so executar novamente
3- Execute os demais testes na ordem numérica

## Links

**Repositório**: https://github.com/ShamanFur/projeto-back-end-raizes-do-nordeste
**Swagger local**: http://127.0.0.1:8000/docs
**Coleção Postman**: arquivo `Projeto Raizes Do Nordeste.postman_collection.json` no repositório