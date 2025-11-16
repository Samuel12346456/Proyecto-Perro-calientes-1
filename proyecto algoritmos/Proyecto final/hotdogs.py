from dataclasses import dataclass
from typing import List, Optional
from ingredientes import Ingrediente

@dataclass
class HotDog:
    id: str
    nombre: str
    pan: Ingrediente
    salchicha: Ingrediente
    toppings: List[Ingrediente]
    salsas: List[Ingrediente]
    acompanante: Optional[Ingrediente] = None
    precio_venta: float = 0.0
    
    @property
    def costo_ingredientes(self) -> float:
        """Calcula el costo total de los ingredientes del hot dog"""
        costo_total = self.pan.costo + self.salchicha.costo
        
        for topping in self.toppings:
            costo_total += topping.costo
        
        for salsa in self.salsas:
            costo_total += salsa.costo
        
        if self.acompanante:
            costo_total += self.acompanante.costo
        
        return costo_total
    
    @property
    def margen_ganancia(self) -> float:
        """Calcula el margen de ganancia del hot dog"""
        return self.precio_venta - self.costo_ingredientes
    
    def validar_longitud(self) -> bool:
        return len(self.pan.nombre) >= len(self.salchicha.nombre)
    
    def verificar_inventario(self, inventario) -> bool:
        if not inventario.hay_suficiente(self.pan, 1):
            return False
        if not inventario.hay_suficiente(self.salchicha, 1):
            return False
        for topping in self.toppings:
            if not inventario.hay_suficiente(topping, 1):
                return False
        for salsa in self.salsas:
            if not inventario.hay_suficiente(salsa, 1):
                return False
        if self.acompanante and not inventario.hay_suficiente(self.acompanante, 1):
            return False
        return True
    
    def consumir_del_inventario(self, inventario) -> bool:
        if not self.verificar_inventario(inventario):
            return False
        
        inventario.consumir_ingrediente(self.pan, 1)
        inventario.consumir_ingrediente(self.salchicha, 1)
        for topping in self.toppings:
            inventario.consumir_ingrediente(topping, 1)
        for salsa in self.salsas:
            inventario.consumir_ingrediente(salsa, 1)
        if self.acompanante:
            inventario.consumir_ingrediente(self.acompanante, 1)
        
        return True
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "pan": self.pan.to_dict(),
            "salchicha": self.salchicha.to_dict(),
            "toppings": [t.to_dict() for t in self.toppings],
            "salsas": [s.to_dict() for s in self.salsas],
            "acompanante": self.acompanante.to_dict() if self.acompanante else None,
            "precio_venta": self.precio_venta
        }
    
    @classmethod
    def from_dict(cls, data, gestor_ingredientes):
        pan = gestor_ingredientes.buscar_por_id(data["pan"]["id"])
        salchicha = gestor_ingredientes.buscar_por_id(data["salchicha"]["id"])
        toppings = [gestor_ingredientes.buscar_por_id(t["id"]) for t in data["toppings"]]
        salsas = [gestor_ingredientes.buscar_por_id(s["id"]) for s in data["salsas"]]
        acompanante = gestor_ingredientes.buscar_por_id(data["acompanante"]["id"]) if data["acompanante"] else None
        
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            pan=pan,
            salchicha=salchicha,
            toppings=toppings,
            salsas=salsas,
            acompanante=acompanante,
            precio_venta=data.get("precio_venta", 0.0)
        )