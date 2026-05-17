# acadeMIND

Aplicação **acadeMIND**: concha inicial com hierarquia cursos/disciplinas, API REST e painel HTML (HTMX + Jinja2).

## Requisitos

- Python 3.10+
- FFmpeg instalado no `PATH` (opcional nesta fase; sem ele, `/health` reporta estado `degraded`)

## Arranque (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item config.example.yaml config.yaml
uvicorn app.main:app --reload
```

Opcionalmente edite `config.yaml` sobre `config.defaults.yaml` — chaves válidas ficam nos exemplos incluídos. Se `logging_dir` estiver definido, os logs são gravados em formato rotativo nessa pasta relativa ao repositório.

## Verificações rápidas

- Interface: http://127.0.0.1:8000/
- Estado do processo/SQLite/ffmpeg/torch CUDA (sem downloads de modelo): http://127.0.0.1:8000/health  

```powershell
curl http://127.0.0.1:8000/health
```

## Testes

```powershell
pytest -q
```
