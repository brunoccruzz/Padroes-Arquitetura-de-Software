# Factory e LSP para pedidos

## Decisao adotada

`OrderService` nao cria mais `Order` diretamente. Ele recebe uma `PedidoFactoryInterface`
e delega a criacao para `PedidoFactory`, que seleciona uma factory especifica para
`NORMAL`, `VIP` ou `CORPORATE`.

As classes `NormalOrderFactory`, `VipOrderFactory` e `CorporateOrderFactory` compartilham
o contrato `OrderFactoryInterface`: todas recebem `customer_name` e `items`, e todas
retornam um `Order` valido no estado `CREATED`. Nenhuma delas altera pre-condicoes,
pos-condicoes ou excecoes esperadas pelo cliente. Assim, qualquer factory concreta pode
substituir outra no ponto em que o contrato `OrderFactoryInterface` e exigido.

## Hierarquia PedEspecial

A hierarquia `PedEspecial -> Sis` do enunciado foi eliminada no desenho refatorado. A
base atual usa o modelo unico `Order` e varia regras por estrategias e factories. Essa
decisao evita o problema original de LSP em que uma subclasse mudava o fluxo de estados
e o calculo de totais de forma incompativel com o comportamento da classe base.

## Avaliacao de Abstract Factory

`Abstract Factory` foi avaliado, mas nao e necessario para a mudanca atual porque a
familia criada ainda tem apenas um produto principal: `Order`. O padrao ficaria melhor
justificado quando cada tipo de cliente precisar criar uma familia completa e coerente,
por exemplo:

- factory de pedido;
- politica de notificacao;
- politica de pontos/fidelidade;
- perfil de pagamento ou aprovacao.

Nesse cenario futuro, uma `CustomerExperienceFactory` poderia expor metodos como
`create_order_factory()`, `create_notification_policy()` e `create_loyalty_policy()`,
garantindo que todos os objetos da familia `VIP` ou `CORPORATE` sejam combinados sem
condicionais espalhadas.
