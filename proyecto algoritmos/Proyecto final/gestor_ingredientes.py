from typing import List, Optional
from ingredientes import Ingrediente, CategoriaIngrediente
from menu import Menu

class GestorIngredientes:
    def __init__(self):
        self.ingredientes = []
    
    def cargar_desde_lista(self, datos: List[dict]):
        for dato in datos:
            try:
                ingrediente = Ingrediente.from_dict(dato)
                # Verificar si ya existe un ingrediente con el mismo ID
                if not any(ing.id == ingrediente.id for ing in self.ingredientes):
                    self.ingredientes.append(ingrediente)
            except Exception as e:
                print(f"Error al cargar ingrediente {dato.get('nombre', 'desconocido')}: {e}")
                continue
    
    def listar_por_categoria(self, categoria: CategoriaIngrediente) -> List[Ingrediente]:
        return [ing for ing in self.ingredientes if ing.categoria == categoria]
    
    def listar_por_categoria_y_tipo(self, categoria: CategoriaIngrediente, tipo: str) -> List[Ingrediente]:
        return [ing for ing in self.ingredientes if ing.categoria == categoria and ing.tipo == tipo]
    
    def agregar_ingrediente(self, ingrediente: Ingrediente):
        self.ingredientes.append(ingrediente)
    
    def eliminar_ingrediente(self, ingrediente: Ingrediente, menu: Menu) -> bool:
        hotdogs_afectados = menu.hotdogs_con_ingrediente(ingrediente)
        
        if hotdogs_afectados:
            print(f"¡Advertencia! El ingrediente '{ingrediente.nombre}' está siendo usado en {len(hotdogs_afectados)} hot dog(s) del menú:")
            for hd in hotdogs_afectados:
                print(f"  - {hd.nombre}")
            
            confirmacion = input("¿Desea eliminar el ingrediente y todos los hot dogs afectados? (s/n): ").lower()
            if confirmacion != 's':
                print("Eliminación cancelada.")
                return False
            
            for hd in hotdogs_afectados:
                menu.eliminar_hotdog(hd)
                print(f"Hot dog '{hd.nombre}' eliminado del menú.")
        
        self.ingredientes.remove(ingrediente)
        print(f"Ingrediente '{ingrediente.nombre}' eliminado exitosamente.")
        return True
    
    def buscar_por_id(self, ingrediente_id: str) -> Optional[Ingrediente]:
        for ing in self.ingredientes:
            if ing.id == ingrediente_id:
                return ing
        return None
    
    def buscar_por_nombre(self, nombre: str) -> Optional[Ingrediente]:
        nombre_lower = nombre.lower().strip()
        for ing in self.ingredientes:
            if ing.nombre.lower() == nombre_lower:
                return ing
        
        # Búsqueda flexible para manejar variaciones
        for ing in self.ingredientes:
            if nombre_lower in ing.nombre.lower() or ing.nombre.lower() in nombre_lower:
                return ing
        
        return None
    
    def obtener_ingredientes_por_nombres(self, nombres: List[str]) -> List[Ingrediente]:
        """Obtiene una lista de ingredientes por sus nombres"""
        ingredientes = []
        for nombre in nombres:
            ingrediente = self.buscar_por_nombre(nombre)
            if ingrediente:
                ingredientes.append(ingrediente)
        return ingredientes