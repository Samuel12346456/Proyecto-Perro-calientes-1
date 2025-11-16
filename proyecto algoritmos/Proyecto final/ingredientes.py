from enum import Enum
from dataclasses import dataclass

class CategoriaIngrediente(Enum):
    PAN = "Pan"
    SALCHICHA = "Salchicha"
    TOPPING = "Topping"
    SALSA = "Salsa"
    ACOMPANANTE = "Acompañante"
    
    @classmethod
    def from_string(cls, value: str):
        """Convierte un string a CategoriaIngrediente con manejo robusto"""
        if not value:
            return cls.TOPPING
            
        value_lower = value.lower().strip()
        mapping = {
            'pan': cls.PAN,
            'salchicha': cls.SALCHICHA,
            'topping': cls.TOPPING,
            'toppings': cls.TOPPING,
            'salsa': cls.SALSA,
            'acompañante': cls.ACOMPANANTE,
            'acompanante': cls.ACOMPANANTE
        }
        return mapping.get(value_lower, cls.TOPPING)

@dataclass
class Ingrediente:
    id: str
    nombre: str
    categoria: CategoriaIngrediente
    tipo: str
    costo: float = 0.0
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria.value,
            "tipo": self.tipo,
            "costo": self.costo
        }
    
    @classmethod
    def from_dict(cls, data):
        # Manejar diferentes formatos de entrada
        nombre = data.get("nombre", "Sin nombre")
        
        # Generar ID si no existe
        ingrediente_id = data.get("id")
        if not ingrediente_id:
            nombre_sin_espacios = nombre.lower().replace(" ", "_")
            categoria_str = data.get("categoria", "topping")
            ingrediente_id = f"ing_{categoria_str.lower()}_{nombre_sin_espacios}"
        
        # Manejar categoría
        categoria_str = data.get("categoria", "topping")
        categoria = CategoriaIngrediente.from_string(categoria_str)
        
        # Manejar tipo
        tipo = data.get("tipo", "General")
        
        # Costo
        costo = data.get("costo", 0.5)
        
        return cls(
            id=ingrediente_id,
            nombre=nombre,
            categoria=categoria,
            tipo=tipo,
            costo=costo
        )