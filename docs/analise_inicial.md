# Analise inicial do sistema legado

O arquivo legado analisado e `legacy_system.py`. Ele concentra persistencia SQLite, regras de pedido, regras de pagamento e relatorios em uma unica classe (`LegacyOrderSystem`). Os trechos abaixo documentam violacoes observaveis antes da refatoracao, com pelo menos duas ocorrencias por principio SOLID.

## SRP - Single Responsibility Principle

### Violacao 1: classe com multiplas responsabilidades

```python
class LegacyOrderSystem:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self._create_tables()
```

Justificativa tecnica: a classe cria tabelas, calcula totais, aplica desconto, registra pagamento, altera status, cancela pedido e gera relatorio. Cada motivo de mudanca afeta o mesmo modulo.

Impacto pratico: uma mudanca pequena em pagamento ou relatorio pode quebrar criacao de pedido ou persistencia, aumentando risco de regressao.

### Violacao 2: metodo `create_order` mistura regra de negocio e SQL

```python
def create_order(self, customer_name, customer_type, items):
    ...
    cursor.execute(
        """
        INSERT INTO orders (
            customer_name, customer_type, subtotal, discount, total, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (customer_name, normalized_type, subtotal, discount, total, "CREATED", now),
    )
```

Justificativa tecnica: o mesmo metodo normaliza tipo de cliente, calcula subtotal/desconto/total e grava dados no banco.

Impacto pratico: nao e possivel testar regra de desconto sem tambem exercitar SQLite, tornando testes mais lentos e acoplados.

## OCP - Open/Closed Principle

### Violacao 1: novos tipos de cliente exigem alterar `if/elif`

```python
discount_rate = 0.0
if normalized_type == "VIP":
    discount_rate = 0.10
elif normalized_type == "CORPORATE":
    discount_rate = 0.15
```

Justificativa tecnica: a regra de desconto esta fechada dentro do metodo, sem extensao por estrategia ou politica externa.

Impacto pratico: adicionar um tipo `PARTNER` exige editar codigo existente e repetir testes de fluxos nao relacionados.

### Violacao 2: novos meios de pagamento exigem alterar o metodo central

```python
if normalized_method not in ("CARD", "PIX", "BOLETO"):
    raise ValueError("unsupported payment method")

reference_prefix = {"CARD": "CARD", "PIX": "PIX", "BOLETO": "BOL"}[normalized_method]
```

Justificativa tecnica: validacao e geracao de referencia dependem de listas e mapas fixos no metodo `pay_order`.

Impacto pratico: incluir outro pagamento, como transferencia, obriga alterar o legado e aumenta chance de quebrar cartao, PIX ou boleto.

## LSP - Liskov Substitution Principle

### Violacao 1: ausencia de contratos substituiveis para repositorio

```python
def _connect(self):
    return sqlite3.connect(self.db_name)
```

Justificativa tecnica: consumidores dependem diretamente da implementacao SQLite criada pela propria classe, sem contrato que permita substituir por outro repositorio.

Impacto pratico: trocar SQLite por outro armazenamento exige alterar a classe de negocio, nao apenas uma implementacao de persistencia.

### Violacao 2: ausencia de contratos substituiveis para pagamentos

```python
def pay_order(self, order_id, method):
    ...
    normalized_method = method.upper()
```

Justificativa tecnica: meios de pagamento sao strings interpretadas internamente, nao objetos com comportamento substituivel e contrato comum.

Impacto pratico: qualquer variacao real de gateway precisaria ser encaixada por condicionais, dificultando substituicao segura.

## ISP - Interface Segregation Principle

### Violacao 1: cliente que so cria pedido depende de operacoes de relatorio e pagamento

```python
class LegacyOrderSystem:
    ...
    def generate_report(self):
```

Justificativa tecnica: a unica interface publica da classe expoe criacao, consulta, pagamento, status, cancelamento e relatorio no mesmo objeto.

Impacto pratico: consumidores simples carregam dependencias e responsabilidades que nao usam, ampliando acoplamento.

### Violacao 2: cliente de relatorio depende de comandos de escrita

```python
def update_status(self, order_id, status):
    ...

def cancel_order(self, order_id):
    ...
```

Justificativa tecnica: nao ha segregacao entre interface de leitura/relatorio e interface de comandos mutaveis.

Impacto pratico: codigo que deveria apenas consultar relatorios recebe acesso acidental a mudancas de estado.

## DIP - Dependency Inversion Principle

### Violacao 1: regra de negocio depende de modulo concreto `sqlite3`

```python
import sqlite3
```

Justificativa tecnica: a camada de alto nivel depende diretamente de um detalhe tecnico de persistencia.

Impacto pratico: testes e evolucao de arquitetura ficam presos a SQLite e ao formato das tabelas.

### Violacao 2: classe instancia a propria dependencia de banco

```python
def _connect(self):
    return sqlite3.connect(self.db_name)
```

Justificativa tecnica: a dependencia e criada internamente, impedindo injecao de outra implementacao.

Impacto pratico: nao ha como usar um repositorio fake, memoria ou servico externo sem alterar a classe.
