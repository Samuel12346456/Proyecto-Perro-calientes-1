from typing import Dict, List
from ingredientes import Ingrediente, CategoriaIngrediente

class Inventario:
    def __init__(self):
        self.existencias = {}
    
    def agregar_ingrediente(self, ingrediente: Ingrediente, cantidad: int):
        self.existencias[ingrediente.id] = cantidad
    
    def verificar_existencia(self, ingrediente: Ingrediente) -> int:
        return self.existencias.get(ingrediente.id, 0)
    
    def actualizar_existencia(self, ingrediente: Ingrediente, cantidad: int):
        self.existencias[ingrediente.id] = cantidad
    
    def hay_suficiente(self, ingrediente: Ingrediente, cantidad_necesaria: int) -> bool:
        return self.verificar_existencia(ingrediente) >= cantidad_necesaria
    
    def listar_por_categoria(self, ingredientes: List[Ingrediente], categoria: CategoriaIngrediente) -> Dict[str, int]:
        return {ing.nombre: self.verificar_existencia(ing) for ing in ingredientes if ing.categoria == categoria}
    
    def consumir_ingrediente(self, ingrediente: Ingrediente, cantidad: int) -> bool:
        if self.hay_suficiente(ingrediente, cantidad):
            self.existencias[ingrediente.id] -= cantidad
            return True
        return False