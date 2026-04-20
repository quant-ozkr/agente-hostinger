# LiqExpert: Plan de Evolución Agéntica con MCP
**Documento Estratégico para Evaluación Multidisciplinar (v2.1)**

## Tabla de Contenidos
1. [Visión General](#1-visión-general)
2. [Eje Central: Arquitectura Técnica para la Convivencia](#2-eje-central-arquitectura-técnica-para-la-convivencia)
3. [Transformación por Componentes](#3-transformación-por-componentes)
4. [Estrategia de Inteligencia y Costos](#4-estrategia-de-inteligencia-y-costos)
5. [Seguridad, Cumplimiento y Gobernanza](#5-seguridad-cumplimiento-y-gobernanza)
6. [Escalabilidad, Rendimiento y Operaciones](#6-escalabilidad-rendimiento-y-operaciones)
7. [Testing, Calidad y Evolución](#7-testing-calidad-y-evolución)
8. [Hoja de Ruta de Implementación Granular](#8-hoja-de-ruta-de-implementación-granular)
9. [Conclusión](#9-conclusión)
10. [Apéndice A: Diagnóstico de Paperclip para MCP](#apéndice-a-diagnóstico-de-paperclip-para-mcp)

---

## 1. Visión General
LiqExpert evoluciona hacia un **Ecosistema Agéntico** basado en el protocolo **MCP (Model Context Protocol)**. El objetivo es democratizar la liquidación fiscal mediante una IA que asesora, calcula y explica, manteniendo la robustez matemática del motor original y cumpliendo con todos los estándares definidos en:
- `AGENTS.md`
- `.agent/RULES.md` 
- `.agent/RULES_ISO27001.md`
- `.agent/INTERVENTION_PROTOCOL.md`

Este plan sigue el criterio diario de prioridad: 1) seguridad y no regresión, 2) continuidad operativa del MVP, 3) claridad de arquitectura, 4) velocidad de entrega, 5) refinamiento cosmético.

## 2. Eje Central: Arquitectura Técnica para la Convivencia
La estrategia se basa en la **bimodalidad**, asegurando que el sistema sea potente para expertos y accesible para novatos.

### 2.1 Convivencia en PC (Dashboard + Copiloto)
- **Dashboard Tradicional:** Mantenido para carga masiva (Excel) y control visual total.
- **Copiloto Agéntico:** Panel lateral integrado que sincroniza el estado con React.
- **Núcleo Compartido:** Ambos enfoques consumen la misma lógica vía REST (Síncrono) y MCP (Agéntico).

### 2.2 Enfoque Agent-First en Móvil
- **WhatsApp/Telegram:** Interfaz principal para el contribuyente ocasional.
- **Mini-UIs:** Tarjetas interactivas que evitan muros de texto en pantallas pequeñas.

## 3. Transformación por Componentes

### 3.1 Backend: De API REST a Servidor MCP
FastAPI expone capacidades mediante:
- **Tools:** `calcular_liquidacion`, `generar_plan_pagos`, `explicar_normativa`.
- **Resources:** `normativa://estatuto_tributario` (RAG), `tasas://historico` (CSV/DB).

### 3.2 Frontend: Host MCP Personalizado
LiqExpert actúa como su propio **Host**, permitiendo:
- **Control de UI:** Renderizado de componentes React reales en el chat.
- **Seguridad Nativa:** Uso de la base de usuarios y roles (RBAC) existente.

## 4. Estrategia de Inteligencia y Costos

### 4.1 Orquestación Multinivel
1. **Nivel 1 (Ahorro):** `gemini-1.5-flash` (90% de tareas). Costo: <$0.10/1M tokens.
2. **Nivel 2 (Experto):** `claude-3.5-sonnet` (Tareas críticas/normativas).
3. **Nivel 3 (Razonamiento):** Modelos de razonamiento denso para nuevas leyes.

### 4.2 Estimación de OpEx (1,000 liquidaciones/mes)
- **IA (Tokens + Cache Semántico):** ~$4.25 USD.
- **Infraestructura (Railway + DB):** ~$25.00 USD.
- **Costo por liquidación:** ~$120 COP (Margen > 95%).

## 5. Seguridad, Cumplimiento y Gobernanza

### 5.1 Gestión de Secrets y Privilegios
- **Secrets Management:** Uso de variables de entorno seguras en Railway y bóvedas de secretos (Vault) para claves de APIs (DIAN, Superfinanciera).
- **Principio de Least Privilege:** El Agente tiene acceso limitado a través de herramientas; no posee credenciales directas de DB.

### 5.2 Estándares de Encriptación y Privacidad
- **Datos en Tránsito:** TLS 1.3 obligatorio.
- **Datos en Reposo:** AES-256 para campos sensibles en PostgreSQL.
- **Taint Tracking:** Marcado de datos confidenciales para evitar su salida hacia LLMs externos sin anonimización previa.
- **GDPR / Ley 1581:** Implementación de flujos para el ejercicio de derechos (acceso, rectificación y supresión).

### 5.3 Respuesta a Incidentes
- Procedimientos documentados para contención y notificación de brechas según `.agent/INTERVENTION_PROTOCOL.md`.

## 6. Escalabilidad, Rendimiento y Operaciones

### 6.1 Arquitectura de Memoria y Proactividad (OpenClaw Pattern)
Para dotar a LiqExpert de continuidad y autonomía superior:
- **Estructura de Memoria Persistente:** Uso de archivos Markdown para definir comportamiento y recordar contextos:
    - `SOUL.md`: Define la personalidad del contador experto, su ética y tono de voz.
    - `MEMORY.md`: Almacena hechos fiscales del usuario a largo plazo (Régimen, NITs frecuentes, preferencias).
    - `HEARTBEAT.md`: Checklist de tareas proactivas (vencimientos, cambios de tasas).
- **Heartbeat (Proactividad):** Ciclo de revisión cada 30 minutos para monitorear el calendario tributario y notificar proactivamente al usuario.
- **Normalización de Entrada:** Capa de adaptadores que convierte notas de voz o adjuntos de WhatsApp/Telegram en objetos de mensaje normalizados antes de la inferencia.
- **Serialización por Sesión:** Cola de comandos que procesa mensajes de forma secuencial por usuario, evitando conflictos en el estado de las liquidaciones.

### 6.2 Escalado y Caching
- **Escalado Horizontal:** Replicación de contenedores FastAPI en Railway tras balanceador de carga.
- **Estrategia de Caching:**
  - **L1:** Caché en memoria para parámetros frecuentes (UVT, Tasas).
  - **L2:** Redis para sesiones de agentes y caché semántica de respuestas LLM.

### 6.3 SLAs y Observabilidad
- **SLA de Latencia:** <2s para consultas simples, <5s para cálculos complejos.
- **Métricas:** Monitoreo de costo por token, tasa de aciertos de caché y errores de razonamiento IA.

## 7. Testing, Calidad y Evolución

### 7.1 Niveles de Testing
- **Unitario:** Cobertura >90% en `backend/app/motor/logic.py`.
- **Integración:** Flujos MCP end-to-end y validación de la fórmula de pricing (§ Regla de Oro).
- **Adversarial:** Pruebas de inyección de prompts para validar la robustez de los interceptores.

### 7.2 Sostenibilidad Técnica
- **Control de Context Bloat:** Límites estrictos en el tamaño de herramientas y recursos expuestos.
- **Evolucionabilidad:** Versionado de herramientas MCP para garantizar compatibilidad hacia atrás.

## 8. Hoja de Ruta de Implementación Granular

### Fase 1: Cimientos y Seguridad (Semanas 1-2)
- **Tarea 1.1:** Configuración del SDK MCP y orquestador en `backend/app/mcp_server.py`.
- **Tarea 1.2:** Implementación de Secrets Management y Baseline de seguridad (pip-audit).
- **Tarea 1.3:** Envolver motor matemático y validar fórmula de pricing inmutable.
- **Tarea 1.4:** Interceptores de validación y anonimización.

### Fase 2: Inteligencia y Calidad (Semanas 3-4)
- **Tarea 2.1:** Conexión de RAG normativo y DSL de explicabilidad.
- **Tarea 2.2:** Documentación de prompts estándar y testing adversarial.
- **Tarea 2.3:** Implementación de Evals automáticos para lógica fiscal.

### Fase 3: Experiencia y Host (Semanas 5-6)
- **Tarea 3.1:** Host MCP en React y UI basada en Shadcn.
- **Tarea 3.2:** Testing de accesibilidad (WCAG 2.1 AA) y pruebas con usuarios reales.
- **Tarea 3.3:** Checkpoint de build: `cd frontend && npm run build` -> `backend/static/`.

### Fase 4: Despliegue y Mantenimiento (Semana 7-8)
- **Tarea 4.1:** Integración certificada de WhatsApp/Telegram.
- **Tarea 4.2:** Workers de actualización de tasas y modo offline para PWA.
- **Tarea 4.3:** Capacitación de soporte y puesta en producción (Railway $PORT).

### Fase 5: Autonomía Operativa de Negocio (Business-in-a-Box) (Semanas 9-10)
**Fundamento:** Transformar a LiqExpert de un "Asesor Técnico" a una "Empresa Autónoma" (modelo Medvi), fusionando el cerebro creativo/social (Agencia Agentica) con el cerebro lógico/transaccional (LiqExpert). El objetivo es operar todo el ciclo B2B/B2C (prospección, onboarding, facturación, retención y resolución de quejas) con cero intervención humana.

- **Tarea 5.1: Herramientas MCP Transaccionales (Cierre sin Fricción):**
  - Exponer la billetera virtual (`crud_wallet.py`) como herramienta MCP.
  - Implementar generación de links de pago dinámicos (Stripe/MercadoPago) en el flujo conversacional.
  - Habilitar el cierre de ventas directamente en WhatsApp/Telegram sin obligar al usuario a usar el dashboard web tradicional.

- **Tarea 5.2: Bucle de Inteligencia de Negocio (Webhooks Inversos):**
  - Configurar webhooks y telemetría de eventos desde LiqExpert hacia la Agencia Agentica.
  - Disparar alertas empíricas basadas en el uso de la plataforma (ej. "Pico del 40% en liquidaciones por extemporaneidad esta semana").
  - Permitir a la Agencia redactar y lanzar campañas de marketing predictivo (Newsletters, TikToks) de forma automática basadas en los datos de la plataforma en tiempo real.

- **Tarea 5.3: Agente de Customer Success (Onboarding Proactivo):**
  - Configurar el módulo `HEARTBEAT.md` para rastrear firmas o promotores recién captados por la Agencia (`intent=firma` o `intent=promotor`).
  - Iniciar secuencias de onboarding autónomo desde el agente MCP: bienvenida por WhatsApp/Email, envío de un tutorial interactivo para carga masiva en Excel, y recordatorio de uso del bono de $50,000 COP.

- **Tarea 5.4: Resolución Autónoma de Conflictos (Zero-Touch Ops):**
  - Empoderar al Agente MCP con el `ExplainabilityService` para atender quejas de usuarios sobre los cálculos (ej. "¡Me están cobrando mucho interés!").
  - Proveer explicaciones jurídicas detalladas y empáticas basadas en la normativa DIAN.
  - Habilitar autonomía limitada al Agente para emitir reembolsos parciales o descuentos de retención directamente a la wallet del usuario si el ticket escala, evitando intervención humana de Nivel 2.

### Fase 6: Autonomía Operativa de Infraestructura (Cerebro Técnico) (Semanas 11-12)
**Fundamento:** Para garantizar que LiqExpert opere sin mantenimiento humano (Zero-Touch Ops), se debe integrar el "Cerebro Técnico" (Agente DevOps). Este agente actúa como el sistema nervioso e inmunológico de la plataforma, asegurando resiliencia, protección de datos y aprovisionamiento automático de recursos para que el Cerebro Lógico y Social nunca se detengan.

- **Tarea 6.1: Orquestación de Infraestructura Vía MCP:**
  - Instalar un servidor MCP local en el VPS (basado en `hostinger_mcp.py`) que exponga herramientas de administración (ej. `verificar_estado_servidor`, `ejecutar_script_deploy`, `reiniciar_servicio`).
  - Integrar este servidor al anillo principal para que el Cerebro Social pueda invocar aumentos de capacidad si detecta picos de tráfico.

- **Tarea 6.2: Resiliencia y Self-Healing (Recuperación Autónoma):**
  - Implementar scripts de diagnóstico activo acoplados al `Restart=on-failure` de Systemd. 
  - Si UptimeRobot detecta una caída, el webhook dispara una alerta al Cerebro Técnico para que lea los logs vía `journalctl`, identifique el cuello de botella (ej. OOM en Uvicorn) y aplique la mitigación sin despertar al equipo humano.

- **Tarea 6.3: Guardián de Integridad de Datos (Startup Chain):**
  - Consolidar la cadena de inicio inmutable (`ensure_alembic.py` → `alembic upgrade` → `verify_schema.py` → `uvicorn`) administrada autónomamente por el Cerebro Técnico.
  - Implementar rollback automático de la base de datos si `verify_schema.py` falla durante un despliegue CI/CD.

- **Tarea 6.4: Gestión de Disco y Backups Inmutables:**
  - Delegar al Cerebro Técnico la rotación autónoma de logs (`logrotate`) para evitar saturación de disco por el RAG (ChromaDB) y el Motor Transaccional.
  - Sincronización automática de respaldos PostgreSQL (`pg_dump`) hacia bóvedas de almacenamiento externo (Google Drive/S3) usando `rclone` cronificado.

## 9. Conclusión
Este plan garantiza una transición segura hacia el paradigma agéntico, respetando la integridad científica de la tesis y los estándares de seguridad industrial, asegurando que LiqExpert lidere la automatización fiscal en la región.

---

## Apéndice A: Diagnóstico de Paperclip para MCP

**Fecha de análisis:** 20 de abril de 2026  
**Repositorio analizado:** https://github.com/paperclipai/paperclip.git  
**Versión del repositorio:** Commit actual (clonado el 20/04/2026)

### A.1 Resumen Ejecutivo

Paperclip es un framework MCP completo que proporciona runtime de agentes mediante heartbeats, adaptadores para modelos locales (Claude, Codex, Gemini) y estructura de servidor MCP. El análisis concluye que **SÍ se puede adoptar y adaptar** como base para LiqExpert, pero requiere modificaciones significativas para cumplir con los requisitos específicos de dominio, seguridad e integración.

### A.2 Hallazgos del Análisis de Paperclip

#### A.2.1 Componentes Identificados

| Componente | Descripción | Relevancia para LiqExpert |
|------------|-------------|---------------------------|
| **Runtime de Agentes** | Ejecución en "heartbeats" (ventanas de ejecución cortas) | Alta - Similar al patrón HEARTBEAT.md |
| **Adaptadores de Modelos** | claude-local, gemini-local, codex-local, cursor-local, opencode-local, pi-local | Alta - Reutilizables para orquestación multinivel |
| **Servidor MCP** | Estructura modular en `/server` con TypeScript | Media - Referencia para implementación FastAPI |
| **Herramientas y Recursos** | Exposición de capacidades via tools y resources | Alta - Modelo idéntico al plan de LiqExpert |
| **Dockerfiles** | Contenedores para despliegue (openclaw-smoke, untrusted-review) | Media - Punto de partida para Docker de LiqExpert |
| **Documentación de API** | Endpoints detallados en `/docs/api` | Baja - No aplicable al dominio de LiqExpert |

#### A.2.2 Arquitectura Técnica Observada

```
Paperclip Architecture:
├── .agents/              # Definiciones de agentes y skills
├── packages/
│   ├── adapters/        # Adaptadores para modelos (claude, gemini, etc.)
│   ├── adapter-utils/  # Utilidades comunes
│   └── [otros]
├── server/             # Servidor MCP principal
├── cli/                # Interfaz de línea de comandos
├── docker/             # Dockerfiles para despliegue
├── docs/               # Documentación (API, guías, specs)
└── evals/              # Framework de evaluación
```

#### A.2.3 Patrón de Heartbeat

El sistema de Paperclip implementa heartbeats de la siguiente manera:
1. Inicia el adaptador de agente configurado (ej: Claude CLI)
2. Proporciona el contexto/prompt actual
3. Permite trabajo hasta que termine, expire o sea cancelado
4. Almacena resultados (estado, uso de tokens, errores, logs)
5. Actualiza la UI en tiempo real

**Relevancia:** Este patrón es directamente aplicable al concepto de `HEARTBEAT.md` descrito en la Sección 6.1 de este plan.

### A.3 Evaluación de Compatibilidad

#### A.3.1 Aspectos que SÍ se pueden complementar/adaptar

| Aspecto | Descripción | Nivel de Adaptación |
|---------|-------------|---------------------|
| Runtime de agentes | Patrón de heartbeats ejecutable | Directamente aplicable |
| Adaptadores de modelos | Wrappers para Claude, Gemini, Codex | Alto - Necesita integración con Vault de secrets |
| Patrones de servidor | Estructura del servidor MCP | Medio - Referencia, FastAPI es más flexible |
| Herramientas/Recursos | Modelo de exposición de capacidades | Bajo - Idéntico al plan |
| Testing adversarial | Framework de evals | Medio - Adaptar para lógica fiscal |
| Dockerfiles | Contenedores para despliegue | Medio - Punto de partida |

#### A.3.2 Aspectos que requieren adaptación significativa

| Aspecto | Problema | Solución Propuesta |
|---------|----------|-------------------|
| Dominio específico | Framework genérico vs. liquidación fiscal | Implementar tools propias: `calcular_liquidacion`, `explicar_normativa` |
| Seguridad ISO 27001 | No tiene mecanismos de seguridad | Aplicar `.agent/RULES.md` y `.agent/RULES_ISO27001.md` |
| Integración RBAC | No contempla autenticación de usuarios | Integrar con sistema existente de usuarios y roles |
| WhatsApp/Telegram | Solo adapters para modelos de IA | Implementar normalización de entrada (Sección 6.1) |
| SOUL/MEMORY/HEARTBEAT | Solo heartbeat básico | Extender con archivos Markdown para personalidad y memoria |

#### A.3.3 NO recomendados para adopción directa

- **Sistema de companies/teams**: No es relevante para el modelo B2B de LiqExpert
- **UI de Paperclip**: LiqExpert necesita su propio Host MCP personalizado
- **Sistema de pricing/costs**: LiqExpert tiene su propia lógica de costos

### A.4 Recomendaciones de Adopción

#### A.4.1 Estrategia Óptima: Biblioteca de Referencia

**NO usar Paperclip como herramienta aparte (microservicio independiente)** porque:
1. Necesita modificaciones profundas para herramientas específicas de liquidación
2. La integración con sistemas existentes de LiqExpert sería más compleja
3. Perdería control sobre aspectos críticos de seguridad y cumplimiento

#### A.4.2 Elementos a Reutilizar

| Elemento | Cómo Reutilizar |
|----------|-----------------|
| **Patrón de heartbeats** | Implementar en `backend/app/mcp_server.py` siguiendo el patrón de Paperclip |
| **Adaptadores de modelos** | Copiar estructura y adaptar para usar claves del Vault de LiqExpert |
| **Dockerfiles** | Usar como base en `docker/Dockerfile.mcp-server` |
| **Concepto de tools/resources** | Mantener consistencia con el estándar MCP |
| **Testing adversarial** | Extender evals para incluir lógica fiscal colombiana |

#### A.4.3 Implementación Recomendada

```
LiqExpert Architecture (con inspiración Paperclip):
├── backend/
│   ├── app/
│   │   ├── mcp_server.py     # Servidor MCP (FastAPI, inspirado en Paperclip)
│   │   ├── motor/            # Motor de liquidación (existente)
│   │   ├── adapters/         # Adaptadores de modelos (basados en Paperclip)
│   │   ├── memory/           # SOUL.md, MEMORY.md, HEARTBEAT.md
│   │   └── security/         # Interceptores ISO 27001
│   └── docker/
│       └── Dockerfile        # Basado en Paperclip + adaptaciones
├── frontend/
│   └── host-mcp-react        # Host MCP personalizado (no Paperclip UI)
└── integrations/
    ├── whatsapp/             # Normalización de entrada
    └── telegram/              # Normalización de entrada
```

### A.5 Veredicto Final

| Criterio | Resultado |
|----------|-----------|
| **¿Se puede complementar?** | Sí - Proporciona framework de referencia sólido |
| **¿Se puede adoptar y adaptar?** | Sí - Con modificaciones significativas para dominio y seguridad |
| **¿Usar como herramienta aparte (Docker)?** | **NO** - Requiere control directo para cumplimiento |
| **¿Compatible con ISO 27001?** | Parcial - Framework base sí, implementación de seguridad no |

### A.6 Próximos Pasos Derivados del Análisis

1. **Semana 0 (Pre-Fase 1):** Estudiar en detalle los adaptadores de Paperclip para entender cómo integrar las claves del Vault
2. **Fase 1 (Tarea 1.1):** Implementar servidor MCP inspirado en la estructura de `/server` de Paperclip
3. **Fase 1 (Tarea 1.2):** Asegurar que los adaptadores de modelos usen el sistema de secrets de LiqExpert
4. **Fase 3 (Tarea 3.1):** Implementar Host MCP en React (no reutilizar UI de Paperclip)

---

*Documento generado tras análisis del repositorio https://github.com/paperclipai/paperclip.git*  
*Análisis realizado el 20 de abril de 2026*

---

## Apéndice B: Comparación con Soluciones Existentes del Ecosistema MCP

**Fecha de elaboración:** 20 de abril de 2026  
**Propósito:** Evaluar alternativas del ecosistema MCP para validar la estrategia de LiqExpert

### B.1 Soluciones Evaluadas

| Solución | Tipo | Fortalezas | Debilidades | Adecuación para LiqExpert |
|----------|------|-----------|------------|-------------|-------------------------|
| **Paperclip** | Framework MCP | Runtime de agentes maduro, adaptadores múltiples | Sin seguridad integrada, dominio genérico | Alta (ver Apéndice A) |
| **TableTalk** | Herramienta MCP | Convierte DB en herramientas MCP | Limitado a consultas SQL | Baja - No procesa lógica fiscal |
| **Claude Code** | Agent CLI | Integración nativa avec Claude | Solo modelo único | Media - Necesita orquestación |
| **MCP SDK ( oficial)** | SDK TypeScript | Estándar oficial | Requiere implementación custom | Alta - Base del servidor |
| **Anthropic MCP** | reference-implementation | EjemploReferenceimplementation completo | Solo demostración | Media - Referencia técnica |

### B.2 Matriz de Decisión

```
Criterios de Selección:
├── Facilidad de Integración     ████████████ 80% → Paperclip/SDK oficial
├── Seguridad Nativa          ████████ 60% → SDK oficial + adaptaciones
├── Soporte a Modelos Múltiples ████████████ 80% → Paperclip
├── Mantenimiento Activo       ██████████ 70% → Paperclip
└── Comunidad y Documentación ████████████ 90% → SDK oficial
```

### B.3 Selección Recomendada

| Componente | Solución adoptada | Justificación |
|-----------|-----------------|-------------|
| **Runtime de Agentes** | Paperclip (como referencia) + implementación propia | Patrón de heartbeats maduro |
| **Servidor MCP** | FastAPI con SDK oficial de MCP | Control total sobre seguridad |
| **Adaptadores** | Basados en Paperclip + integración con Vault | Consistencia con el ecosistema |
| **Host MCP** | Implementación propia en React | Integración con RBAC existente |

### B.4 Alternativas de Fallback

Si Paperclip no está disponible o no cumple con requisitos:
1. **Opción 1:** Implementar servidor MCP desde cero usando SDK oficial
2. **Opción 2:** Usar Anthropic reference-implementation como base
3. **Opción 3:** Usar TableTalk solo para咨询服务 (no como servidor principal)

---

## Apéndice C: Arquitectura de Microservicios (Docker)

**Fecha de elaboración:** 20 de abril de 2026  
**Propósito:** Definir la estrategia de contenedorización para despliegue

### C.1 Principios de Diseño

| Principio | Descripción | Aplicación en LiqExpert |
|----------|-------------|-------------------------|
| **Single Responsibility** | Cada contenedor una responsabilidad | Separar MCP Server, Worker, API Gateway |
| **Security First** | Contenedores seguros por defecto | imagenes minimal, sin secrets hardcoded |
| **Observabilidad** | Logging y métricas integrados | Prometheus + Grafana |
| **Portabilidad** | Funciona igual en dev/prod | Docker Compose para ambos |

### C.2 Arquitectura de Contenedores Propuesta

```yaml
# docker-compose.yml (versión simplificada)
services:
  # Servidor MCP principal
  mcp-server:
    build: ./docker/mcp-server
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DB_URL}
      - VAULT_ADDR=${VAULT_ADDR}
    depends_on:
      - postgres
      - redis
    secrets:
      - api-keys  # Referencia a external secret

  # Worker para tareas proactivas (HEARTBEAT)
  heartbeat-worker:
    build: ./docker/worker
    environment:
      - HEARTBEAT_INTERVAL=1800  # 30 minutos
    depends_on:
      - mcp-server

  # API Gateway (seguridad adicional)
  api-gateway:
    build: ./docker/gateway
    ports:
      - "443:443"
    depends_on:
      - mcp-server
    volumes:
      - ./certs:/certs:ro

  # Base de datos
  postgres:
    image: postgres:15-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data

  # Caché y sesiones
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}

volumes:
  pgdata:
```

### C.3 Imágenes Docker Recomendadas

| Servicio | Imagen Base | Tamaño | Justificación |
|----------|-------------|--------|---------------|
| **mcp-server** | python:3.11-slim | ~150MB | FastAPI + dependencias |
| **worker** | python:3.11-slim | ~150MB | Comparte dependencias |
| **gateway** | nginx:alpine | ~25MB | Solo proxying |
| **postgres** | postgres:15-alpine | ~80MB | Datos persistentes |
| **redis** | redis:7-alpine | ~35MB | Caché en memoria |

### C.4 Consideraciones de Seguridad

| Medida | Implementación | Prioridad |
|--------|-----------------|-----------|
| **No ROOT** | USER 1001 en Dockerfile | Alta |
| **Secrets externos** | Docker secrets o Vault | Alta |
| **TLS 1.3** | Certificados en /certs | Alta |
| **Health checks** | /health endpoint en cada servicio | Media |
| **Resource limits** | memory: 512M, cpu: 0.5 | Media |

### C.5 CI/CD Recomendado

```dockerfile
# Ejemplo: docker/mcp-server/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar solo dependencias necesarias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# No ejecutar como root
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### C.6 Despliegue en Railway (Producción)

| Variable de Entorno | Descripción | Fuente |
|--------------------|-------------|--------|
| DATABASE_URL | Conexión a PostgreSQL | Railway Secrets |
| REDIS_PASSWORD | Contraseña de Redis | Railway Secrets |
| VAULT_ADDR | Dirección del Vault | Railway Variables |
| OPENAI_API_KEY | Clave de OpenAI | Vault externo |
| ANTHROPIC_API_KEY | Clave de Anthropic | Vault externo |
| DIAN_API_KEY | Clave de DIAN | Vault externo |

---

*Apéndices B y C añadidos el 20 de abril de 2026*

---

## Apéndice D: Integración Macro del Ecosistema (Business-in-a-Box Autónomo)

**Fecha de elaboración:** 20 de abril de 2026  
**Propósito:** Definir cómo **LiqExpert** (Motor Transaccional), la **Agencia Agéntica** (Motor Comercial) y herramientas satélite como **Scrapling** (Ojos/OSINT) se fusionan en un solo ecosistema corporativo de "Cero Intervención Humana".

### D.1 Fusión de Hemisferios Agénticos

Para lograr el nivel de **Fase 5 (Autonomía Operativa de Negocio)**, la empresa ya no se divide por software, sino por "Cerebros" interconectados a través de la base de datos central PostgreSQL y el bus de eventos corporativos (Webhooks / Heartbeat).

| Hemisferio | Rol | Componentes | Integración MCP |
|------------|-----|-------------|-----------------|
| **Cerebro Lógico (Left Brain)** | Asesoría Fiscal, Cálculos, Compliancy (ISO27001) | `mcp_server.py`, Motor de liquidación, DB Segura, Vault | Se expone vía `calcular`, `explicar_normativa`. Es reactivo (responde al cliente). |
| **Cerebro Social (Right Brain)** | Prospección (Outbound), Onboarding, Retención, Búsqueda de Influencers | `webhook_server.py`, `telegram_bot.py`, Agentes de Flujo, **Scrapling** | Múltiples agentes paralelos alimentando la DB. Es proactivo (busca clientes). |
| **Cerebro Técnico (Brainstem)** | DevOps, Self-Healing, Backups, CI/CD, Seguridad Perimetral | `hostinger_mcp.py`, Systemd, Nginx, UFW, GitHub Actions, Rclone | Se expone vía `verificar_estado`, `reiniciar_servicio`. Respalda a los otros dos cerebros y garantiza el uptime. |

### D.2 El Rol de los Frameworks Adoptados (Scrapling & Paperclip)

La adopción estratégica de frameworks externos evita reinventar la rueda y provee "habilidades sensoriales" a la IA:

1. **Paperclip (El Pulso / Nervios):** Nos inspira el patrón de `heartbeats`. Le da a la Agencia la capacidad de "despertarse" cada 30 minutos, revisar si un Lead nuevo (detectado por un webhook) necesita seguimiento, o si LiqExpert reportó que un usuario no pudo realizar su cálculo fiscal.
2. **Scrapling (Los Ojos / OSINT):** Resuelve el problema de la "ceguera de API". En lugar de depender de fragmentos limitados de Google que bloquean al agente con CAPTCHAs, Scrapling provee la herramienta `read_full_website`. Permite a la Agencia Agéntica navegar sitios web corporativos en modo Stealth (saltando Cloudflare Turnstile/Datadome), extraer contactos (NITs, RUES) de manera perfecta y leer los perfiles completos de influenciadores para calcular métricas ocultas antes de contactarlos.

### D.3 Flujo Vital Integrado (Un día en la Empresa Autónoma)

Este es el proceso completo en bucle cerrado de cómo se comunican las plataformas:

1. **Generación (Agencia + Scrapling):** 
   - El *Cerebro Social* ejecuta un Cron de "búsqueda de leads B2B".
   - Pide a **Scrapling** que lea la cámara de comercio (sin ser bloqueado) y formatee los correos de los contadores.
   - Envía un mensaje en frío por WhatsApp usando las herramientas de `outreach`.
2. **Captación (Webhooks):**
   - El contador recibe el WhatsApp, hace clic en el Tracking Link (creado vía MCP) y entra a LiqExpert.
   - El `webhook_server` capta la conversión en milisegundos y marca al Lead como "Interested" en PostgreSQL.
3. **Conversión (LiqExpert):**
   - El *Cerebro Lógico* de LiqExpert entra en acción, ayudando directamente al contador a hacer la liquidación en el dashboard, manejando leyes de la DIAN sin cometer alucinaciones.
4. **Retención / Upsell (Heartbeat Inteligente):**
   - Tres días después, el `heartbeat.py` del *Cerebro Social* detecta que este contador tiene 10 NITs guardados en su `MEMORY.md`.
   - Vuelve a contactar al contador con una oferta hiper-personalizada (Ej: *"Veo que atiendes a la empresa XYZ, te ofrezco el plan Master de LiqExpert."*) formulando la propuesta mediante investigación adicional cortesía de Scrapling.

### D.4 Principio de Adopción de Microservicios para Agentes

El ecosistema debe evitar el "Monolito de Herramientas Agénticas". Cualquier nueva capacidad (ej: Scraping avanzado, generación de audio, análisis de PDF masivos) **no se añade al repositorio base**. Se implementa como un microservicio aislado bajo el mismo paradigma propuesto para Scrapling:
1. Docker aislado con su Runtime.
2. Expone una API REST o sub-servidor MCP.
3. La Agencia Agéntica (el orquestador) lo usa como una *Tool Call*. 

Este enfoque garantiza que si el sistema anti-bots de Scrapling falla un día, el negocio de LiqExpert no se cae; solo la prospección fría se detiene temporalmente mientras se emite una alerta.
