# ✅ CHECKLIST DE DESPLIEGUE AWS

## 📋 ANTES DE DESPLEGAR

### 1. Archivos Necesarios
- [x] `Dockerfile` ✅
- [x] `Dockerrun.aws.json` ✅
- [x] `.ebignore` ✅
- [x] `.elasticbeanstalk/config.yml` ✅
- [x] `requirements.txt` ✅
- [x] CORS configurado en `main.py` ✅

### 2. Software Instalado
- [ ] AWS CLI instalado (`aws --version`)
- [ ] EB CLI instalado (`eb --version`)
- [X] Docker instalado (opcional, para probar localmente)

### 3. Credenciales AWS
- [X] Cuenta AWS creada
- [X] Créditos de $100 activados
- [ ] Access Key ID obtenido
- [ ] Secret Access Key obtenido
- [ ] Credenciales configuradas (`aws configure`)

### 4. Variables de Entorno Preparadas
Prepara estos valores (los necesitarás en el PASO 3):

```bash
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="..."
HUGGINGFACE_TOKEN="hf_..."
SUPABASE_URL="https://..."
SUPABASE_KEY="..."
UPSTASH_REDIS_URL="redis://..."
UPSTASH_REDIS_TOKEN="..."
LLM_PROVIDER="gemini"
EMBEDDING_PROVIDER="openai"
HUGGINGFACE_MODEL="meta-llama/Llama-3.2-1B-Instruct"
```

---

## 🚀 PASOS DE DESPLIEGUE

### PASO 1: Instalar Herramientas
```powershell
# AWS CLI
# Descargar desde: https://aws.amazon.com/cli/
aws --version

# EB CLI
pip install awsebcli
eb --version

# Configurar AWS
aws configure
# Ingresa: Access Key, Secret Key, Region (us-east-1), Format (json)
```

### PASO 2: Inicializar y Crear Entorno
```powershell
cd "C:\Users\hcardenas\Desktop\Material Laptop\Cursos\Proyectos\agent-education"

# Inicializar (opcional, ya está configurado)
eb init

# Crear entorno en AWS
eb create edu-nexus-backend-env --instance-type t3.micro --single
```

⏱️ **Tiempo estimado:** 5-10 minutos

### PASO 3: Configurar Variables de Entorno
```powershell
# Opción A: Desde terminal (reemplaza con tus valores)
eb setenv OPENAI_API_KEY="tu-key" GEMINI_API_KEY="tu-key" HUGGINGFACE_TOKEN="tu-token" SUPABASE_URL="tu-url" SUPABASE_KEY="tu-key" UPSTASH_REDIS_URL="tu-url" UPSTASH_REDIS_TOKEN="tu-token" LLM_PROVIDER="gemini" EMBEDDING_PROVIDER="openai"

# Opción B: Desde AWS Console
# 1. AWS Console → Elastic Beanstalk → edu-nexus-backend
# 2. Configuration → Software → Edit
# 3. Environment properties → Agregar todas las variables
# 4. Apply
```

### PASO 4: Verificar Despliegue
```powershell
# Ver estado
eb status

# Ver logs
eb logs

# Abrir en navegador
eb open

# Probar health check
curl http://tu-url.elasticbeanstalk.com/health
```

### PASO 5: Guardar URL del Backend
```
URL del Backend: _________________________________

Ejemplo: http://edu-nexus-backend-env.eba-abc123.us-east-1.elasticbeanstalk.com
```

---

## 🧪 PRUEBAS POST-DESPLIEGUE

### 1. Health Check
```powershell
curl http://tu-url.elasticbeanstalk.com/health
```
**Respuesta esperada:**
```json
{"status": "healthy", "timestamp": "..."}
```

### 2. Chat Endpoint
```powershell
curl -X POST http://tu-url.elasticbeanstalk.com/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hola\", \"session_id\": \"test123\"}"
```

### 3. Sílabos Disponibles
```powershell
curl http://tu-url.elasticbeanstalk.com/syllabi
```

### 4. Verificar Logs
```powershell
eb logs --stream
```
Busca errores o warnings.

---

## 🌐 SIGUIENTE: FRONTEND EN VERCEL

### 1. Preparar Frontend
```bash
# En tu proyecto de frontend, crear .env.production
NEXT_PUBLIC_API_URL=http://tu-url-backend.elasticbeanstalk.com
```

### 2. Desplegar en Vercel
1. Ve a https://vercel.com
2. Importar proyecto desde GitHub
3. Agregar variable de entorno: `NEXT_PUBLIC_API_URL`
4. Deploy ✅

### 3. Actualizar CORS en Backend
Una vez que tengas la URL de Vercel, actualiza `main.py`:
```python
allow_origins=[
    "https://tu-app.vercel.app",  # Reemplazar con tu URL real
    "http://localhost:3000",
]
```

Luego redespliega:
```powershell
eb deploy
```

---

## 💰 MONITOREO DE COSTOS

### Ver costos actuales:
1. AWS Console → Billing Dashboard
2. Cost Explorer → Ver costos por servicio

### Alertas de costos:
1. Billing → Budgets → Create budget
2. Configurar alerta si supera $10/mes

---

## 🔧 COMANDOS ÚTILES

```powershell
# Ver estado
eb status

# Ver logs en tiempo real
eb logs --stream

# Abrir en navegador
eb open

# Redesplegar después de cambios
eb deploy

# Ver variables de entorno
eb printenv

# Cambiar tipo de instancia
eb scale 1 --instance-type t3.small

# Ver salud de la app
eb health

# Terminar entorno (CUIDADO)
eb terminate edu-nexus-backend-env
```

---

## ❗ TROUBLESHOOTING

### Problema: "eb: command not found"
```powershell
pip install awsebcli --upgrade
```

### Problema: "No credentials found"
```powershell
aws configure
# Ingresa tus credenciales
```

### Problema: "Health check failed"
1. Verifica logs: `eb logs`
2. Verifica que `/health` funcione localmente
3. Verifica puerto 8000 en `Dockerfile`

### Problema: "Application is slow"
```powershell
# Aumentar tipo de instancia
eb scale 1 --instance-type t3.small
```

### Problema: Variables de entorno no funcionan
```powershell
# Verificar variables
eb printenv

# Reconfigurar
eb setenv OPENAI_API_KEY="nueva-key"
```

---

## 📊 MÉTRICAS A MONITOREAR

1. **CPU Usage** - Debe estar < 70%
2. **Memory Usage** - Debe estar < 80%
3. **Response Time** - Debe estar < 2s
4. **Error Rate** - Debe estar < 1%

Ver en: AWS Console → Elastic Beanstalk → Monitoring

---

## ✅ CHECKLIST FINAL

- [ ] Backend desplegado en AWS ✅
- [ ] URL del backend obtenida ✅
- [ ] Health check funciona ✅
- [ ] Chat endpoint funciona ✅
- [ ] Variables de entorno configuradas ✅
- [ ] Logs sin errores críticos ✅
- [ ] URL guardada para el frontend ✅

---

**¡Listo para el siguiente paso: Frontend en Vercel! 🎉**
