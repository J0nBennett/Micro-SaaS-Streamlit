# Micro-SaaS Streamlit (Estado actual)

Aplicacion Streamlit con:
- autenticacion sobre MongoDB
- resumen y traduccion de texto via OpenAI
- verificacion de suscripcion via Stripe
- gestion de cuenta en pagina adicional

## Estructura actual

```
Home.py
utils.py
requirements.txt
mongo_auth/
  authenticate.py
  hasher.py
  exceptions.py
  utils.py
pages/
  Account_Management.py
tests/
  ...
```

## Requisitos

- Python 3.10+ (recomendado)
- MongoDB accesible
- credenciales/API keys configuradas por variables de entorno o `st.secrets`

## Configuracion

Crear `.env` (solo local, no versionar) con las variables usadas por la app:

- `MONGO_AUTH`
- `OPENAI_API_KEY`
- `STRIPE_API_KEY`
- `STRIPE_PAYMENT_URL`
- `VERIFICATION_URL`
- `YOUR_EMAIL`
- `YOUR_EMAIL_PASS`
- `AUTH_COOKIE_NAME`
- `AUTH_COOKIE_KEY`
- `APP_BASE_URL` (ejemplo: `http://localhost:8501`)
- `RESET_TOKEN_EXPIRY_MINUTES` (opcional, default `30`)

Tambien podes usar `.streamlit/secrets.toml` (ver ejemplo en `.streamlit/secrets.toml.example`).

## Seguridad del reset de password

- El flujo de recuperacion ahora envia un link/token de reset de un solo uso.
- Ya no se envia una nueva password por email.
- El token se guarda hasheado en MongoDB y expira.

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion

```bash
streamlit run Home.py
```

## Testing

Desde la raiz del repo:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```
