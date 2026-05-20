# EFC 1 - Padroes e Arquitetura de Software

Projeto de refatoracao orientada por Golden Master Tests.

## Arquitetura

- `legacy_system.py`: fachada de compatibilidade com a API original capturada pelos testes.
- `src/models`: entidades e enums de dominio (`Order`, `OrderItem`, status, tipos de cliente e pagamento).
- `src/repositories`: `OrderRepository`, unico ponto com acesso direto a SQLite.
- `src/services`: regras de pedido, pagamento e relatorio.
- `src/interfaces`: abstracoes com `ABC` para repositorios e servicos externos.
- `tests/golden_master`: testes que congelam o comportamento original.

## Comandos

```bash
pytest -v
pytest --cov=. --cov-report=term-missing --cov-report=html
ruff check .
```

Tambem ha atalhos:

```bash
make test
make coverage
make lint
```

## Sprints

### Sprint 0

- Criada suite `pytest`.
- Criados Golden Master Tests para pedido normal, VIP, corporativo, pagamentos, status, cancelamento e relatorios.
- Cada teste usa banco isolado com `tmp_path` e `monkeypatch.chdir(tmp_path)`.
- Criado `docs/analise_inicial.md` com violacoes SOLID.
- Tag Git: `sprint-0`.

### Sprint 1

- Extraidas camadas `models`, `repositories`, `services` e `interfaces`.
- Isolado acesso SQLite em `OrderRepository`.
- Mantida compatibilidade por meio da fachada `LegacyOrderSystem`.
- Preparado para Strategy, Observer, Factory e DIP no Sprint 2.
