from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import gradio as gr
import hashlib, secrets
from typing import Dict, Tuple

# --- SRP simplificado (mesmo princípio da demo original) ---
N = 0xE487EB1528E2
g = 2


def H(*args: bytes) -> bytes:
    m = hashlib.sha256()
    for a in args:
        m.update(a)
    return m.digest()


def H_int(*args: bytes) -> int:
    return int.from_bytes(H(*args), "big")


k = H_int(
    N.to_bytes((N.bit_length()+7)//8, "big"),
    g.to_bytes((g.bit_length()+7)//8, "big")
)


def compute_x(salt: bytes, username: str, password: str) -> int:
    inner = H((username + ":" + password).encode())
    return int.from_bytes(H(salt, inner), "big")


def compute_v(x: int) -> int:
    return pow(g, x, N)


# --- Servidor em memória ---
# armazenamos username -> (salt: bytes, v: int)
users: Dict[str, Tuple[bytes, int]] = {}


# Funções usadas tanto pelo Gradio quanto pela API

def registrar_logic(username: str, password: str) -> dict:
    if not username or not password:
        raise ValueError("Preencha todos os campos.")
    if username in users:
        raise ValueError("Usuário já registrado.")
    salt = secrets.token_bytes(8)
    x = compute_x(salt, username, password)
    v = compute_v(x)
    users[username] = (salt, v)
    return {"message": f"Usuário '{username}' registrado.", "salt": salt.hex()}


def autenticar_logic(username: str, password: str) -> dict:
    if username not in users:
        raise ValueError("Usuário não registrado.")
    salt, v = users[username]
    # Cliente gera 'a' e A
    a = secrets.randbelow(N - 1)
    A = pow(g, a, N)
    # Servidor gera 'b' e B
    b = secrets.randbelow(N - 1)
    B = (k * v + pow(g, b, N)) % N
    u = H_int(
        A.to_bytes((A.bit_length() + 7) // 8, "big"),
        B.to_bytes((B.bit_length() + 7) // 8, "big")
    )
    x = compute_x(salt, username, password)
    S_client = pow((B - k * pow(g, x, N)) % N, (a + u * x), N)
    S_server = pow((A * pow(v, u, N)) % N, b, N)
    Kc = H(S_client.to_bytes((S_client.bit_length() + 7) // 8, "big"))
    Ks = H(S_server.to_bytes((S_server.bit_length() + 7) // 8, "big"))
    success = Kc == Ks
    return {
        "success": success,
        "message": "Autenticação bem-sucedida." if success else "Falha: chaves diferentes.",
        "key_preview": Kc.hex()[:20] + "..." if success else None,
    }


# --- FastAPI + endpoints ---
app = FastAPI()


class Creds(BaseModel):
    username: str
    password: str


@app.post("/register")
async def api_register(creds: Creds):
    try:
        res = registrar_logic(creds.username, creds.password)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
async def api_login(creds: Creds):
    try:
        res = autenticar_logic(creds.username, creds.password)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Gradio app (não sobe servidor próprio; vamos montá-lo no FastAPI) ---
with gr.Blocks() as demo:
    gr.Markdown("## Demonstração do Protocolo SRP (Simples)")
    username = gr.Textbox(label="Usuário")
    password = gr.Textbox(label="Senha", type="password")
    btn_reg = gr.Button("Registrar")
    btn_login = gr.Button("Login (Autenticar)")
    output = gr.Textbox(label="Resultado", lines=4)

    def reg_ui(u, p):
        try:
            r = registrar_logic(u, p)
            return f"✅ {r['message']}\nSalt: {r['salt']}"
        except ValueError as ex:
            return f"❌ {str(ex)}"

    def login_ui(u, p):
        try:
            r = autenticar_logic(u, p)
            if r['success']:
                return f"🔐 {r['message']}\nChave: {r['key_preview']}"
            else:
                return f"⚠️ {r['message']}"
        except ValueError as ex:
            return f"❌ {str(ex)}"

    btn_reg.click(fn=reg_ui, inputs=[username, password], outputs=output)
    btn_login.click(fn=login_ui, inputs=[username, password], outputs=output)


# monta o Gradio dentro do FastAPI em /lp
# esta chamada integra a UI do Gradio à aplicação FastAPI
gr.mount_gradio_app(app, demo, path="/lp")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("srp_fastapi_gradio:app", host="0.0.0.0", port=8000, reload=True)
