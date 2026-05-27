# Diagrama de Classes

Diagrama UML dividido por camada para facilitar leitura e exportação.

---

## 1. Modelos

```mermaid
classDiagram
    direction LR

    class CustomerType {
        <<enumeration>>
        NORMAL
        VIP
        CORPORATE
    }

    class OrderStatus {
        <<enumeration>>
        CREATED
        PAID
        CANCELLED
        SHIPPED
    }

    class PaymentMethod {
        <<enumeration>>
        CARD
        PIX
        BOLETO
        CRYPTO
    }

    class OrderItem {
        <<dataclass>>
        +str sku
        +str name
        +int quantity
        +float unit_price
        +float line_total
    }

    class PaymentRecord {
        <<dataclass>>
        +PaymentMethod method
        +float amount
        +str status
        +str reference
        +str paid_at
    }

    class Order {
        <<dataclass>>
        +int id
        +str customer_name
        +CustomerType customer_type
        +float subtotal
        +float discount
        +float total
        +OrderStatus status
        +str created_at
        +list~OrderItem~ items
        +list~PaymentRecord~ payments
    }

    Order "1" *-- "many" OrderItem : contém
    Order "1" *-- "many" PaymentRecord : contém
    Order --> CustomerType
    Order --> OrderStatus
    PaymentRecord --> PaymentMethod
```

---

## 2. Interfaces

```mermaid
classDiagram
    direction TB

    class OrderRepositoryInterface {
        <<interface>>
        +save(order Order) Order
        +get_by_id(order_id int) Order
        +add_payment(order_id int, payment PaymentRecord) None
        +update_status(order_id int, status OrderStatus) bool
        +report_summary() tuple
    }

    class NotificationObserverInterface {
        <<interface>>
        +update(order Order) None
    }

    class PaymentReferenceProviderInterface {
        <<interface>>
        +reference_for(method PaymentMethod, order_id int) str
    }

    class DiscountStrategyInterface {
        <<interface>>
        +calculate(subtotal float) float
    }

    class DiscountStrategyResolverInterface {
        <<interface>>
        +resolve(customer_type CustomerType) DiscountStrategyInterface
    }

    class PaymentStrategyInterface {
        <<interface>>
        +execute(order_id int, amount float) PaymentRecord
    }

    class PaymentStrategyResolverInterface {
        <<interface>>
        +resolve(method PaymentMethod) PaymentStrategyInterface
    }

    class OrderFactoryInterface {
        <<interface>>
        +create(customer_name str, items list) Order
    }

    class PedidoFactoryInterface {
        <<interface>>
        +create_order(customer_name str, customer_type str, items list) Order
    }

    DiscountStrategyResolverInterface --> DiscountStrategyInterface : retorna
    PaymentStrategyResolverInterface --> PaymentStrategyInterface : retorna
```

---

## 3. Repositório

```mermaid
classDiagram
    direction LR

    class OrderRepositoryInterface {
        <<interface>>
        +save(order Order) Order
        +get_by_id(order_id int) Order
        +add_payment(order_id int, payment PaymentRecord) None
        +update_status(order_id int, status OrderStatus) bool
        +report_summary() tuple
    }

    class OrderRepository {
        -str db_name
        +save(order Order) Order
        +get_by_id(order_id int) Order
        +add_payment(order_id int, payment PaymentRecord) None
        +update_status(order_id int, status OrderStatus) bool
        +report_summary() tuple
        -_connect() Connection
        -_create_tables() None
    }

    OrderRepository ..|> OrderRepositoryInterface : implementa
```

---

## 4. Serviços

```mermaid
classDiagram
    direction TB

    class OrderService {
        -OrderRepositoryInterface repository
        -PedidoFactoryInterface order_factory
        -list~NotificationObserverInterface~ _observers
        +attach_observer(observer NotificationObserverInterface) None
        +create_order(customer_name str, customer_type str, items list) Order
        +get_order(order_id int) Order
        +update_status(order_id int, status str) Order
        +cancel_order(order_id int) Order
        -_notify_observers(order Order) None
    }

    class PaymentService {
        -OrderRepositoryInterface repository
        -PaymentStrategyResolverInterface payment_resolver
        +pay_order(order_id int, method str) dict
    }

    class ReportService {
        -OrderRepositoryInterface repository
        +generate_report() str
    }

    class OrderRepositoryInterface {
        <<interface>>
    }

    class PedidoFactoryInterface {
        <<interface>>
    }

    class NotificationObserverInterface {
        <<interface>>
    }

    class PaymentStrategyResolverInterface {
        <<interface>>
    }

    OrderService --> OrderRepositoryInterface : depende
    OrderService --> PedidoFactoryInterface : depende
    OrderService "1" o-- "many" NotificationObserverInterface : observa
    PaymentService --> OrderRepositoryInterface : depende
    PaymentService --> PaymentStrategyResolverInterface : depende
    ReportService --> OrderRepositoryInterface : depende
```

---

## 5. Estratégias de Desconto

```mermaid
classDiagram
    direction TB

    class DiscountStrategyInterface {
        <<interface>>
        +calculate(subtotal float) float
    }

    class DiscountStrategyResolverInterface {
        <<interface>>
        +resolve(customer_type CustomerType) DiscountStrategyInterface
    }

    class NoDiscountStrategy {
        +calculate(subtotal float) float
    }

    class VipDiscountStrategy {
        -float _RATE = 0.10
        +calculate(subtotal float) float
    }

    class CorporateDiscountStrategy {
        -float _RATE = 0.15
        +calculate(subtotal float) float
    }

    class FixedDiscountStrategy {
        -float _amount
        +calculate(subtotal float) float
    }

    class VolumeDiscountStrategy {
        -tuple _TIERS
        +calculate(subtotal float) float
    }

    class DefaultDiscountStrategyResolver {
        -dict _registry
        -DiscountStrategyInterface _fallback
        +resolve(customer_type CustomerType) DiscountStrategyInterface
    }

    NoDiscountStrategy ..|> DiscountStrategyInterface : implementa
    VipDiscountStrategy ..|> DiscountStrategyInterface : implementa
    CorporateDiscountStrategy ..|> DiscountStrategyInterface : implementa
    FixedDiscountStrategy ..|> DiscountStrategyInterface : implementa
    VolumeDiscountStrategy ..|> DiscountStrategyInterface : implementa
    DefaultDiscountStrategyResolver ..|> DiscountStrategyResolverInterface : implementa
    DefaultDiscountStrategyResolver "1" o-- "many" DiscountStrategyInterface : registra
```

---

## 6. Estratégias de Pagamento

```mermaid
classDiagram
    direction TB

    class PaymentStrategyInterface {
        <<interface>>
        +execute(order_id int, amount float) PaymentRecord
    }

    class PaymentStrategyResolverInterface {
        <<interface>>
        +resolve(method PaymentMethod) PaymentStrategyInterface
    }

    class CardPaymentStrategy {
        +execute(order_id int, amount float) PaymentRecord
    }

    class PixPaymentStrategy {
        +execute(order_id int, amount float) PaymentRecord
    }

    class BoletoPaymentStrategy {
        +execute(order_id int, amount float) PaymentRecord
    }

    class CryptoPaymentStrategy {
        -float _FEE_RATE = 0.02
        +execute(order_id int, amount float) PaymentRecord
    }

    class DefaultPaymentStrategyResolver {
        -dict _registry
        +resolve(method PaymentMethod) PaymentStrategyInterface
    }

    CardPaymentStrategy ..|> PaymentStrategyInterface : implementa
    PixPaymentStrategy ..|> PaymentStrategyInterface : implementa
    BoletoPaymentStrategy ..|> PaymentStrategyInterface : implementa
    CryptoPaymentStrategy ..|> PaymentStrategyInterface : implementa
    DefaultPaymentStrategyResolver ..|> PaymentStrategyResolverInterface : implementa
    DefaultPaymentStrategyResolver "1" o-- "many" PaymentStrategyInterface : registra
```

---

## 7. Observadores

```mermaid
classDiagram
    direction LR

    class NotificationObserverInterface {
        <<interface>>
        +update(order Order) None
    }

    class EmailNotificationObserver {
        +update(order Order) None
    }

    class SmsNotificationObserver {
        +update(order Order) None
    }

    class ManagerNotificationObserver {
        +update(order Order) None
    }

    class WhatsAppNotificationObserver {
        +update(order Order) None
    }

    EmailNotificationObserver ..|> NotificationObserverInterface : implementa
    SmsNotificationObserver ..|> NotificationObserverInterface : implementa
    ManagerNotificationObserver ..|> NotificationObserverInterface : implementa
    WhatsAppNotificationObserver ..|> NotificationObserverInterface : implementa
```

---

## 8. Fábricas

```mermaid
classDiagram
    direction TB

    class OrderFactoryInterface {
        <<interface>>
        +create(customer_name str, items list) Order
    }

    class PedidoFactoryInterface {
        <<interface>>
        +create_order(customer_name str, customer_type str, items list) Order
    }

    class CustomerOrderFactory {
        -CustomerType _customer_type
        -DiscountStrategyResolverInterface _discount_resolver
        +create(customer_name str, items list) Order
        -_build_items(items list) list~OrderItem~
    }

    class NormalOrderFactory {
        +__init__(discount_resolver DiscountStrategyResolverInterface)
    }

    class VipOrderFactory {
        +__init__(discount_resolver DiscountStrategyResolverInterface)
    }

    class CorporateOrderFactory {
        +__init__(discount_resolver DiscountStrategyResolverInterface)
    }

    class PedidoFactory {
        -dict~CustomerType, OrderFactoryInterface~ _factories
        +from_discount_resolver(discount_resolver)$ PedidoFactory
        +create_order(customer_name str, customer_type str, items list) Order
    }

    class VolumeDiscountPedidoFactory {
        -int _THRESHOLD = 3
        -float _RATE = 0.15
        -PedidoFactoryInterface _inner
        +create_order(customer_name str, customer_type str, items list) Order
        -_apply_volume_discount(items list) list
    }

    class DiscountStrategyResolverInterface {
        <<interface>>
    }

    NormalOrderFactory --|> CustomerOrderFactory : herda
    VipOrderFactory --|> CustomerOrderFactory : herda
    CorporateOrderFactory --|> CustomerOrderFactory : herda
    CustomerOrderFactory ..|> OrderFactoryInterface : implementa
    CustomerOrderFactory --> DiscountStrategyResolverInterface : depende
    PedidoFactory ..|> PedidoFactoryInterface : implementa
    PedidoFactory "1" o-- "many" OrderFactoryInterface : registra
    VolumeDiscountPedidoFactory ..|> PedidoFactoryInterface : implementa
    VolumeDiscountPedidoFactory --> PedidoFactoryInterface : decora
```

---

## Legenda

| Seta | Significado |
|------|-------------|
| `──▷` (sólida, triângulo vazio) | **Herança** — subclasse estende superclasse |
| `╌╌▷` (tracejada, triângulo vazio) | **Implementação** — classe implementa interface |
| `───>` (sólida, seta aberta) | **Dependência** — classe depende de abstração |
| `◆───` (losango preenchido) | **Composição** — dono controla ciclo de vida |
| `◇───` (losango vazio) | **Agregação** — referência sem controle de ciclo de vida |

## Padrões de Projeto

| Padrão | Classes envolvidas |
|--------|--------------------|
| **Strategy** | `DiscountStrategyInterface` + 5 implementações; `PaymentStrategyInterface` + 4 implementações |
| **Strategy Resolver** | `DefaultDiscountStrategyResolver`, `DefaultPaymentStrategyResolver` |
| **Factory Method** | `CustomerOrderFactory` → `NormalOrderFactory`, `VipOrderFactory`, `CorporateOrderFactory` |
| **Abstract Factory** | `PedidoFactory` coordena factories por `CustomerType` |
| **Decorator** | `VolumeDiscountPedidoFactory` envolve `PedidoFactoryInterface` |
| **Observer** | `OrderService` notifica `NotificationObserverInterface` + 4 observers |
| **Repository** | `OrderRepositoryInterface` + `OrderRepository` (SQLite) |
| **Dependency Injection** | Todos os services recebem dependências via construtor |
