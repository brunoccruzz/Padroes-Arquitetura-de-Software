from abc import ABC, abstractmethod

from src.models import PaymentMethod


class PaymentReferenceProviderInterface(ABC):
    @abstractmethod
    def reference_for(self, method: PaymentMethod, order_id: int) -> str:
        raise NotImplementedError
