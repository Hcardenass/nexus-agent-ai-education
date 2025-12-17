# 🚀 Guía de Despliegue en AWS Elastic Beanstalk

## ✅ Archivos Preparados

Ya tienes todo listo:
- ✅ `Dockerfile` - Configuración del contenedor
- ✅ `Dockerrun.aws.json` - Configuración para Elastic Beanstalk
- ✅ `.ebignore` - Archivos a ignorar al subir
- ✅ `.elasticbeanstalk/config.yml` - Configuración del proyecto
- ✅ `requirements.txt` - Dependencias de Python

---

## 📋 REQUISITOS PREVIOS

### 1. Instalar AWS CLI
```powershell
# Descargar e instalar desde:
# https://aws.amazon.com/cli/

# Verificar instalación
aws --version
```

### 2. Instalar EB CLI (Elastic Beanstalk CLI)
```powershell
# Instalar con pip
pip install awsebcli

# Verificar instalación
eb --version
```

### 3. Configurar Credenciales AWS
```powershell
# Configurar AWS CLI con tus credenciales
aws configure

# Te pedirá:
# - AWS Access Key ID: [tu access key]
# - AWS Secret Access Key: [tu secret key]
# - Default region name: us-east-1
# - Default output format: json
```

**¿Dónde obtener las credenciales?**
1. Ve a AWS Console → IAM → Users → Tu usuario
2. Security credentials → Create access key
3. Guarda el Access Key ID y Secret Access Key

---

## 🚀 PASOS DE DESPLIEGUE

### PASO 1: Inicializar Elastic Beanstalk

```powershell
# Navegar a tu proyecto
cd "C:\Users\hcardenas\Desktop\Material Laptop\Cursos\Proyectos\agent-education"

# Inicializar EB (ya está configurado, pero por si acaso)
eb init

# Selecciona:
# - Region: us-east-1 (o la que prefieras)
# - Application name: edu-nexus-backend
# - Platform: Docker
# - Platform version: Docker running on 64bit Amazon Linux 2023
# - SSH: No (por ahora)
```

### PASO 2: Crear Entorno en AWS

```powershell
# Crear entorno de producción
eb create edu-nexus-backend-env --instance-type t3.micro --single

# Opciones:
# --instance-type t3.micro = Gratis en Free Tier
# --single = Una sola instancia (no load balancer, más barato)
```

**Este comando:**
- ✅ Crea la aplicación en AWS
- ✅ Sube tu código
- ✅ Construye la imagen Docker
- ✅ Despliega el contenedor
- ✅ Configura el load balancer
- ✅ Te da una URL pública

**Tiempo estimado:** 5-10 minutos ⏱️

### PASO 3: Configurar Variables de Entorno

```powershell
# Configurar TODAS tus variables de entorno
eb setenv \
  OPENAI_API_KEY="tu-openai-key" \
  GEMINI_API_KEY="tu-gemini-key" \
  HUGGINGFACE_TOKEN="tu-hf-token" \
  SUPABASE_URL="tu-supabase-url" \
  SUPABASE_KEY="tu-supabase-key" \
  UPSTASH_REDIS_URL="tu-redis-url" \
  UPSTASH_REDIS_TOKEN="tu-redis-token" \
  LLM_PROVIDER="gemini" \
  EMBEDDING_PROVIDER="openai" \
  HUGGINGFACE_MODEL="meta-llama/Llama-3.2-1B-Instruct"
```

**O configúralas desde la consola web:**
1. AWS Console → Elastic Beanstalk → Tu aplicación
2. Configuration → Software → Edit
3. Environment properties → Agregar todas las variables

### PASO 4: Verificar Despliegue

```powershell
# Ver el estado
eb status

# Ver logs en tiempo real
eb logs --stream

# Abrir la aplicación en el navegador
eb open
```

**Tu URL será algo como:**
```
http://edu-nexus-backend-env.eba-xxxxxxxx.us-east-1.elasticbeanstalk.com
```

### PASO 5: Probar el Backend

```powershell
# Probar health check
curl http://tu-url.elasticbeanstalk.com/health

# Probar endpoint de chat
curl -X POST http://tu-url.elasticbeanstalk.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "session_id": "test123"}'
```

---

## 🔄 ACTUALIZACIONES FUTURAS

### Opción A: Despliegue Manual
```powershell
# Después de hacer cambios en tu código
git add .
git commit -m "Actualización"

# Desplegar a AWS
eb deploy

# Ver logs
eb logs --stream
```

### Opción B: Con GitHub Actions (Automático)
Después configuraremos GitHub Actions para que se despliegue automáticamente en cada `git push`.

---

## 🌐 CONFIGURAR CORS PARA TU FRONTEND

Antes de desplegar, asegúrate de que tu backend permita requests desde Vercel:

```python
# main.py - Ya debería estar configurado
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://edu-nexus.vercel.app",  # Tu frontend (lo tendrás después)
        "http://localhost:3000",          # Desarrollo local
        "*"                               # TEMPORAL: permite todos (quitar en producción)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 MONITOREO Y LOGS

### Ver logs en tiempo real:
```powershell
eb logs --stream
```

### Ver logs históricos:
```powershell
eb logs
```

### Ver métricas en AWS Console:
1. AWS Console → Elastic Beanstalk → Tu aplicación
2. Monitoring → Ver CPU, memoria, requests, etc.

---

## 💰 COSTOS ESTIMADOS

### Con Free Tier (primer año):
- ✅ **$0/mes** - 750 horas de t3.micro gratis
- ✅ **$0/mes** - 5GB de almacenamiento S3 gratis
- ✅ **$0/mes** - 1GB de transferencia de datos gratis

### Después del Free Tier:
- 💵 **~$15-20/mes** - t3.micro 24/7
- 💵 **~$5-10/mes** - Transferencia de datos (depende del tráfico)
- **Total: ~$20-30/mes**

### Optimización de costos:
```powershell
# Si quieres ahorrar, puedes usar t2.micro (más barato pero menos potente)
eb scale 1 --instance-type t2.micro
```

---

## 🔧 COMANDOS ÚTILES

```powershell
# Ver estado del entorno
eb status

# Ver logs
eb logs

# Abrir en navegador
eb open

# Ver configuración
eb config

# Escalar instancias
eb scale 2  # 2 instancias (para alta disponibilidad)

# Cambiar tipo de instancia
eb scale 1 --instance-type t3.small

# Ver salud de la aplicación
eb health

# SSH a la instancia (si configuraste SSH)
eb ssh

# Terminar el entorno (CUIDADO: elimina todo)
eb terminate edu-nexus-backend-env
```

---

## ❗ TROUBLESHOOTING

### Error: "No module named 'app'"
- **Solución:** Verifica que el `Dockerfile` copie correctamente la carpeta `app/`

### Error: "Health check failed"
- **Solución:** Verifica que el endpoint `/health` funcione localmente
- Revisa los logs: `eb logs`

### Error: "Port 8000 not accessible"
- **Solución:** Verifica que el `Dockerfile` exponga el puerto 8000
- Verifica que `Dockerrun.aws.json` tenga el puerto correcto

### Error: Variables de entorno no funcionan
- **Solución:** Configúralas con `eb setenv` o desde la consola web
- Verifica con: `eb printenv`

### La aplicación es muy lenta
- **Solución:** Aumenta el tipo de instancia: `eb scale 1 --instance-type t3.small`

---

## 🎯 SIGUIENTE PASO: FRONTEND EN VERCEL

Una vez que tengas la URL del backend:

1. **Copia la URL:**
   ```
   http://edu-nexus-backend-env.eba-xxxxxxxx.us-east-1.elasticbeanstalk.com
   ```

2. **Configúrala en tu frontend:**
   ```bash
   # .env.production (en tu proyecto de frontend)
   NEXT_PUBLIC_API_URL=http://tu-url.elasticbeanstalk.com
   ```

3. **Despliega en Vercel:**
   - Conecta tu repo de GitHub
   - Vercel detecta automáticamente Next.js
   - Agrega las variables de entorno
   - Deploy automático ✅

---

## 📞 SOPORTE

Si tienes problemas:
1. Revisa los logs: `eb logs --stream`
2. Verifica el estado: `eb health`
3. Revisa la consola web de AWS
4. Pregúntame y te ayudo 🚀

---

**¡Listo para desplegar! 🎉**
