# SDD - acadeMIND vNext

## 1. Visão Geral

### Nome do Projeto

**acadeMIND**

### Objetivo

Aplicação desktop-first com interface web local para organização, ingestão, processamento e consolidação de materiais acadêmicos de graduação.

### Público-alvo

Graduandos que desejam centralizar:

* PDFs
* Slides
* Apostilas
* Gravações de aula
* Áudios
* Conteúdo web exportado

### Premissas Técnicas

* Execução local em Windows 11
* Sem dependência cloud obrigatória
* Uso intensivo da RTX 4080 para transcrição
* Interface web responsiva
* Persistência local em disco
* Arquitetura simples e regenerável
* MVP incremental

---

# 2. Objetivos Funcionais

O sistema deve permitir:

1. Criar cursos
2. Criar disciplinas dentro dos cursos
3. Upload de múltiplos tipos de arquivo
4. Organização lógica dos arquivos
5. Processamento batch dos materiais
6. Transcrição GPU accelerated
7. Consolidação documental
8. Download dos artefatos gerados
9. Reprocessamento controlado
10. Operação 100% local

---

# 3. Arquitetura Recomendada

## Stack

### Backend

* Python 3.10+
* FastAPI
* Uvicorn
* SQLModel ou SQLite puro
* Pydantic

### Frontend

* HTML + Tailwind
* HTMX
* Alpine.js
* Design system baseado em `projekt-design-system.html`

### Processamento

* FFmpeg
* faster-whisper
* CUDA
* PyTorch CUDA
* pypdf

### Banco

* SQLite local

### Empacotamento futuro

* Docker opcional
* PyInstaller opcional

---

# 4. Arquitetura de Pastas

```text
academind/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── services/
│   ├── processors/
│   ├── models/
│   ├── repositories/
│   ├── templates/
│   ├── static/
│   └── main.py
│
├── storage/
│   ├── cursos/
│   │
│   └── temp/
│
├── database/
│   └── academind.db
│
├── logs/
│
├── ffmpeg/
│
├── requirements.txt
│
└── README.md
```

---

# 5. Estrutura de Dados

## Curso

```json
{
  "id": "uuid",
  "nome": "Engenharia de Software",
  "created_at": "datetime"
}
```

---

## Disciplina

```json
{
  "id": "uuid",
  "curso_id": "uuid",
  "nome": "Arquitetura de Software",
  "created_at": "datetime"
}
```

---

## Arquivo

```json
{
  "id": "uuid",
  "disciplina_id": "uuid",
  "nome_original": "aula01.mp4",
  "tipo": "mp4",
  "categoria": "video",
  "path_original": "",
  "path_processado": "",
  "status": "pending",
  "created_at": "datetime"
}
```

---

# 6. Estrutura Física dos Arquivos

## Exemplo

```text
storage/
└── cursos/
    └── engenharia-software/
        └── arquitetura-software/
            ├── originais/
            │   ├── documentos/
            │   ├── videos/
            │   ├── audios/
            │   └── web/
            │
            ├── processados/
            │   ├── transcricoes/
            │   ├── pdfs/
            │   └── exports/
            │
            └── metadata/
```

---

# 7. Tipos de Arquivos Aceitos

| Tipo  | Categoria |
| ----- | --------- |
| PDF   | Documento |
| TXT   | Documento |
| DOCX  | Documento |
| HTML  | Web       |
| MHTML | Web       |
| MP4   | Vídeo     |
| MP3   | Áudio     |
| WAV   | Áudio     |
| M4A   | Áudio     |

---

# 8. Fluxo do Usuário

## Fluxo Principal

```text
Usuário acessa app
    ↓
Cria curso
    ↓
Cria disciplina
    ↓
Faz upload dos arquivos
    ↓
Arquivos são catalogados
    ↓
Usuário inicia processamento
    ↓
Sistema:
    - transcreve vídeos
    - transcreve áudios
    - concatena PDFs
    ↓
Arquivos gerados aparecem na aba "Processados"
    ↓
Usuário baixa ZIP final
```

---

# 9. Processamento de Vídeo e Áudio

## Motor de Transcrição

### Recomendação

Utilizar:

```text
faster-whisper
```

### Motivos

* Excelente qualidade
* Usa CUDA
* Muito rápido na RTX 4080
* Melhor custo/performance local

---

## Modelo Recomendado

### Padrão MVP

```text
large-v3
```

---

## Configuração GPU

```python
device="cuda"
compute_type="float16"
```

---

## Pipeline

```text
MP4/MP3
    ↓
FFmpeg extrai áudio
    ↓
Whisper transcreve
    ↓
TXT salvo em:
processados/transcricoes/
```

---

# 10. Concatenação de PDFs

## Biblioteca

```text
pypdf
```

## Resultado

```text
concatenado.pdf
```

## Ordem

* Ordem alfabética
* Futuramente:

  * drag-and-drop ordering

---

# 11. Interface Web

## Requisitos

### Dashboard inicial

* Lista de cursos
* Criar curso

### Página da disciplina

Separada em abas:

#### Aba 1 - Originais

* Lista arquivos enviados
* Download
* Abrir pasta
* Excluir

#### Aba 2 - Processados

* TXT transcritos
* concatenado.pdf
* ZIP final

#### Aba 3 - Processamento

* Status
* Fila
* Progresso
* Logs

---

# 12. Design System

## Regra Crítica

O arquivo:

```text
projekt-design-system.html
```

serve apenas como:

* referência visual
* tokens de UI
* spacing
* tipografia
* componentes

O branding do app deve permanecer:

```text
acadeMIND
```

Nunca utilizar:

* logos projekt
* nomes projekt
* textos projekt
* identidade projekt

---

# 13. Backend API

## Endpoints MVP

### Cursos

```http
GET    /api/cursos
POST   /api/cursos
DELETE /api/cursos/{id}
```

---

### Disciplinas

```http
GET    /api/disciplinas/{id}
POST   /api/disciplinas
DELETE /api/disciplinas/{id}
```

---

### Upload

```http
POST /api/upload
```

---

### Processamento

```http
POST /api/processar/{disciplina_id}
```

---

### Downloads

```http
GET /api/download/{arquivo_id}
GET /api/download/zip/{disciplina_id}
```

---

# 14. ZIP Final

## Conteúdo

```text
exports/
└── disciplina-export.zip
    ├── originais/
    ├── transcricoes/
    ├── concatenado.pdf
    └── metadata.json
```

---

# 15. Logs

## Necessário

```text
logs/
```

### Tipos

* upload.log
* processamento.log
* ffmpeg.log
* whisper.log
* api.log

---

# 16. Requisitos Não Funcionais

## Performance

* Processamento paralelo controlado
* Não travar UI

## Segurança

* Sanitização de nomes
* Bloqueio path traversal
* Limite de extensões

## Robustez

* Resume de processamento
* Retry simples
* Tolerância a arquivos inválidos

## UX

* Drag-and-drop upload
* Barra de progresso
* Toasts simples

---

# 17. Recursos Imprescindíveis Não Citados Originalmente

## 17.1 Fingerprint de Arquivos

Necessário evitar duplicidade.

### Estratégia

SHA256 no upload.

---

## 17.2 Banco de Jobs

Necessário para:

* fila
* status
* reprocessamento
* recuperação após crash

---

## 17.3 Status de Processamento

```text
pending
processing
completed
failed
```

---

## 17.4 Lock de Processamento

Evitar:

* dois processos simultâneos
* corrupção de arquivos

---

## 17.5 Sistema de Configuração

Arquivo:

```text
config.yaml
```

Com:

* paths
* modelo whisper
* threads
* idioma padrão
* tamanho máximo upload

---

## 17.6 Healthcheck

Endpoint:

```http
GET /health
```

---

## 17.7 Conversão Universal

Nem todos formatos serão compatíveis diretamente.

### Necessário

Padronizar com FFmpeg:

* sample rate
* canais
* codec

---

## 17.8 Watchdog de Processos

Detectar:

* travamentos
* subprocessos mortos
* timeout

---

# 18. Decisões Técnicas

## NÃO utilizar

* Electron
* Node backend pesado
* Banco remoto
* Cloud obrigatória
* Microservices

## UTILIZAR

* Monólito modular
* FastAPI
* SQLite
* Processamento local

---

# 19. Roadmap MVP

## Fase 1

* CRUD cursos
* CRUD disciplinas
* Upload
* Organização física

## Fase 2

* Transcrição áudio
* Transcrição vídeo

## Fase 3

* Concatenação PDF

## Fase 4

* ZIP export

## Fase 5

* UI refinada

---

# 20. Requisitos de Hardware

## Recomendado

* RTX 4080
* 32GB RAM mínimo
* SSD NVMe
* CUDA Toolkit 12+

---

# 21. Dependências

## Python

```text
fastapi
uvicorn
jinja2
python-multipart
sqlmodel
pydantic
faster-whisper
torch
torchaudio
ffmpeg-python
pypdf
aiofiles
python-slugify
watchdog
```

---

# 22. Estratégia de Execução

## Desenvolvimento

```powershell
uvicorn app.main:app --reload
```

---

## Produção Local

```powershell
nohup python mn.py &
```

ou:

```powershell
python mn.py
```

---

# 23. Requisitos de UX

## Interface

* limpa
* rápida
* foco em produtividade
* zero poluição visual

## Navegação

```text
Curso
  → Disciplina
      → Originais
      → Processados
      → Logs
```

---

# 24. Melhorias Futuras

## Backlog

* OCR
* Busca semântica
* IA de resumo
* Flashcards
* Chat contextual
* Vetorização
* RAG local
* Multiusuário
* Docker deploy
* Sincronização remota
* Integração Obsidian
* Export markdown

---

# 25. Estrutura Final Recomendada

```text
acadeMIND
├── backend/
├── frontend/
├── storage/
├── database/
├── logs/
├── ffmpeg/
├── config/
└── scripts/
```

---

# 26. Conclusão Técnica

A melhor abordagem para o acadeMIND é:

* FastAPI monolítico modular
* Frontend HTMX/Tailwind
* SQLite local
* faster-whisper com CUDA
* Estrutura filesystem-first
* Processamento assíncrono controlado
* MVP incremental
* Sem dependência cloud

Essa arquitetura é:

* simples
* rápida
* regenerável
* compatível com Cursor + GSD
* adequada para sua RTX 4080
* adequada para Windows 11 local
