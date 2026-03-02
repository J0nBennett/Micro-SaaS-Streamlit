# Micro-SaaS Streamlit (Estado actual)

Aplicacion Streamlit con:
- autenticacion sobre MongoDB
- resumen y traduccion de texto via OpenAI
- verificacion de suscripcion via Stripe
- gestion de cuenta en pagina adicional

## Estructura actual

```
saas/
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
```

## Requisitos

- Python 3.10+ (recomendado)
- MongoDB accesible
- credenciales/API keys configuradas por variables de entorno o `st.secrets`

## Configuracion

Crear `saas/.env` (solo local, no versionar) con las variables usadas por la app:

- `MONGO_AUTH`
- `OPENAI_API_KEY`
- `STRIPE_API_KEY`
- `STRIPE_PAYMENT_URL`
- `VERIFICATION_URL`
- `YOUR_EMAIL`
- `YOUR_EMAIL_PASS`
- `AUTH_COOKIE_NAME`
- `AUTH_COOKIE_KEY`

## Instalacion

Desde la carpeta `saas`:

```bash
pip install -r requirements.txt
```

## Ejecucion

Desde la raiz del repo:

```bash
streamlit run saas/Home.py
```

o desde `saas/`:

```bash
streamlit run Home.py
```
