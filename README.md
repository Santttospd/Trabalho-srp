<<<<<<< HEAD
# Trabalho-srp
=======
# PROJETO DE SRP COM PYTHON
Projeto simples com a implementacao do protocolo SRP para a aula de Sistemas Ubiquos.

## RODANDO O PROJETO
Para rodar o projeto, siga os passos:

### Instale o Virtual Enviroment (venv)
```shell
    python -m venv .venv
```

### Ative o pip

Usando Windows Powershell:
```shell
  .\.venv\Scripts\Activate.ps1
```

Usando o Windows Command Prompt:
```shell
    .\.venv\Scripts\activate
```

Usando Linux ou Mac:
```shell
  source .venv/bin/activate
```

### Instale as dependencias
```shell
    pip install --upgrade pip
    pip install -r requirements.txt
```

### Para rodar usando Uvicorn
```shell
    uvicorn srp_fastapi_gradio:app --reload
```

## Como funciona
A pagina: `http://127.0.0.1:8000/lp` vai ter a landing page com os campos para testar.

O endpoint `http://127.0.0.1:8000/register`, chamado quando o botao `Registrar` foi apertado, vai registrar o usuario na aplicacao teste com o usuario e senha providenciados nos seus respectivos campos.

O endpoint `http://127.0.0.1:8000/login`, chamado quando o botao `Login (Autenticar)` foi apertado, vai tentar autenticar o dados providenciados, com os valores salvos na aplicacao.
>>>>>>> ac58121 (Trablho srp, implementação)
