import json
import requests
import random
from typing import List, Dict, Optional
from enum import Enum
import os
from dataclasses import dataclass, asdict

class CategoriaIngrediente(Enum):
    PAN = "Pan"
    SALCHICHA = "Salchicha"
    TOPPING = "Topping"
    SALSA = "Salsa"
    ACOMPANANTE = "Acompañante"

@dataclass
class Ingrediente:
    id: str
    nombre: str
    categoria: CategoriaIngrediente
    tipo: str
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria.value,
            "tipo": self.tipo
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            categoria=CategoriaIngrediente(data["categoria"]),
            tipo=data["tipo"]
        )

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
    
    def listar_por_categoria(self, ingredientes: List[Ingrediente], categoria: CategoriaIngrediente) -> Dict[Ingrediente, int]:
        return {ing: self.verificar_existencia(ing) for ing in ingredientes if ing.categoria == categoria}
    
    def consumir_ingrediente(self, ingrediente: Ingrediente, cantidad: int) -> bool:
        if self.hay_suficiente(ingrediente, cantidad):
            self.existencias[ingrediente.id] -= cantidad
            return True
        return False

@dataclass
class HotDog:
    id: str
    nombre: str
    pan: Ingrediente
    salchicha: Ingrediente
    toppings: List[Ingrediente]
    salsas: List[Ingrediente]
    acompanante: Optional[Ingrediente] = None
    
    def validar_longitud(self) -> bool:
        # Validación básica de longitud (puede expandirse según reglas específicas)
        return len(self.pan.nombre) >= len(self.salchicha.nombre)
    
    def verificar_inventario(self, inventario: Inventario) -> bool:
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
    
    def consumir_del_inventario(self, inventario: Inventario) -> bool:
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
            "acompanante": self.acompanante.to_dict() if self.acompanante else None
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
            acompanante=acompanante
        )

class Menu:
    def __init__(self):
        self.hotdogs = []
    
    def agregar_hotdog(self, hotdog: HotDog):
        self.hotdogs.append(hotdog)
    
    def eliminar_hotdog(self, hotdog: HotDog):
        self.hotdogs.remove(hotdog)
    
    def listar_hotdogs(self) -> List[HotDog]:
        return self.hotdogs
    
    def buscar_por_id(self, hotdog_id: str) -> Optional[HotDog]:
        for hotdog in self.hotdogs:
            if hotdog.id == hotdog_id:
                return hotdog
        return None
    
    def hotdogs_con_ingrediente(self, ingrediente: Ingrediente) -> List[HotDog]:
        return [hd for hd in self.hotdogs if self._hotdog_usa_ingrediente(hd, ingrediente)]
    
    def _hotdog_usa_ingrediente(self, hotdog: HotDog, ingrediente: Ingrediente) -> bool:
        if hotdog.pan.id == ingrediente.id or hotdog.salchicha.id == ingrediente.id:
            return True
        if any(t.id == ingrediente.id for t in hotdog.toppings):
            return True
        if any(s.id == ingrediente.id for s in hotdog.salsas):
            return True
        if hotdog.acompanante and hotdog.acompanante.id == ingrediente.id:
            return True
        return False

class GestorIngredientes:
    def __init__(self):
        self.ingredientes = []
    
    def cargar_desde_lista(self, datos: List[dict]):
        for dato in datos:
            ingrediente = Ingrediente.from_dict(dato)
            self.ingredientes.append(ingrediente)
    
    def listar_por_categoria(self, categoria: CategoriaIngrediente) -> List[Ingrediente]:
        return [ing for ing in self.ingredientes if ing.categoria == categoria]
    
    def listar_por_categoria_y_tipo(self, categoria: CategoriaIngrediente, tipo: str) -> List[Ingrediente]:
        return [ing for ing in self.ingredientes if ing.categoria == categoria and ing.tipo == tipo]
    
    def agregar_ingrediente(self, ingrediente: Ingrediente):
        self.ingredientes.append(ingrediente)
    
    def eliminar_ingrediente(self, ingrediente: Ingrediente, menu: Menu) -> bool:
        # Verificar si el ingrediente está siendo usado
        hotdogs_afectados = menu.hotdogs_con_ingrediente(ingrediente)
        
        if hotdogs_afectados:
            print(f"¡Advertencia! El ingrediente '{ingrediente.nombre}' está siendo usado en {len(hotdogs_afectados)} hot dog(s) del menú:")
            for hd in hotdogs_afectados:
                print(f"  - {hd.nombre}")
            
            confirmacion = input("¿Desea eliminar el ingrediente y todos los hot dogs afectados? (s/n): ").lower()
            if confirmacion != 's':
                print("Eliminación cancelada.")
                return False
            
            # Eliminar hot dogs afectados
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
        for ing in self.ingredientes:
            if ing.nombre.lower() == nombre.lower():
                return ing
        return None

class GestorInventario:
    def __init__(self, inventario: Inventario, gestor_ingredientes: GestorIngredientes):
        self.inventario = inventario
        self.gestor_ingredientes = gestor_ingredientes
    
    def visualizar_todo(self):
        print("\n=== INVENTARIO COMPLETO ===")
        for categoria in CategoriaIngrediente:
            self.listar_existencias_por_categoria(categoria)
    
    def buscar_existencia(self, nombre_ingrediente: str) -> Optional[int]:
        ingrediente = self.gestor_ingredientes.buscar_por_nombre(nombre_ingrediente)
        if ingrediente:
            return self.inventario.verificar_existencia(ingrediente)
        return None
    
    def listar_existencias_por_categoria(self, categoria: CategoriaIngrediente):
        ingredientes_categoria = self.gestor_ingredientes.listar_por_categoria(categoria)
        existencias = self.inventario.listar_por_categoria(ingredientes_categoria, categoria)
        
        print(f"\n--- {categoria.value.upper()} ---")
        for ingrediente, cantidad in existencias.items():
            print(f"  {ingrediente.nombre} ({ingrediente.tipo}): {cantidad}")
    
    def actualizar_existencia(self, nombre_ingrediente: str, nueva_cantidad: int) -> bool:
        ingrediente = self.gestor_ingredientes.buscar_por_nombre(nombre_ingrediente)
        if ingrediente:
            self.inventario.actualizar_existencia(ingrediente, nueva_cantidad)
            print(f"Existencia de '{ingrediente.nombre}' actualizada a {nueva_cantidad}")
            return True
        else:
            print(f"Ingrediente '{nombre_ingrediente}' no encontrado.")
            return False

class GestorMenu:
    def __init__(self, menu: Menu, inventario: Inventario, gestor_ingredientes: GestorIngredientes):
        self.menu = menu
        self.inventario = inventario
        self.gestor_ingredientes = gestor_ingredientes
    
    def ver_lista_hotdogs(self):
        print("\n=== MENÚ DE HOT DOGS ===")
        for i, hotdog in enumerate(self.menu.listar_hotdogs(), 1):
            disponible = "✓" if hotdog.verificar_inventario(self.inventario) else "✗"
            print(f"{i}. {hotdog.nombre} [{disponible}]")
    
    def verificar_inventario_para_hotdog(self, hotdog: HotDog) -> bool:
        return hotdog.verificar_inventario(self.inventario)
    
    def agregar_nuevo_hotdog(self):
        print("\n=== AGREGAR NUEVO HOT DOG ===")
        
        nombre = input("Nombre del hot dog: ")
        
        # Seleccionar pan
        panes = self.gestor_ingredientes.listar_por_categoria(CategoriaIngrediente.PAN)
        print("\nPanes disponibles:")
        for i, pan in enumerate(panes, 1):
            print(f"{i}. {pan.nombre} ({pan.tipo})")
        pan_idx = int(input("Seleccione el pan: ")) - 1
        pan = panes[pan_idx]
        
        # Seleccionar salchicha
        salchichas = self.gestor_ingredientes.listar_por_categoria(CategoriaIngrediente.SALCHICHA)
        print("\nSalchichas disponibles:")
        for i, salchicha in enumerate(salchichas, 1):
            print(f"{i}. {salchicha.nombre} ({salchicha.tipo})")
        salchicha_idx = int(input("Seleccione la salchicha: ")) - 1
        salchicha = salchichas[salchicha_idx]
        
        # Validar longitud
        if not self._validar_longitud_pan_salchicha(pan, salchicha):
            confirmacion = input("¡Advertencia! La longitud del pan y la salchicha no coinciden. ¿Desea continuar? (s/n): ")
            if confirmacion.lower() != 's':
                print("Registro cancelado.")
                return False
        
        # Seleccionar toppings
        toppings = self._seleccionar_ingredientes_multiples(CategoriaIngrediente.TOPPING, "toppings")
        
        # Seleccionar salsas
        salsas = self._seleccionar_ingredientes_multiples(CategoriaIngrediente.SALSA, "salsas")
        
        # Seleccionar acompañante (opcional)
        acompanante = None
        incluir_acompanante = input("\n¿Incluir acompañante? (s/n): ").lower()
        if incluir_acompanante == 's':
            acompanantes = self.gestor_ingredientes.listar_por_categoria(CategoriaIngrediente.ACOMPANANTE)
            print("\nAcompañantes disponibles:")
            for i, acomp in enumerate(acompanantes, 1):
                print(f"{i}. {acomp.nombre} ({acomp.tipo})")
            acomp_idx = int(input("Seleccione el acompañante: ")) - 1
            acompanante = acompanantes[acomp_idx]
        
        # Crear hot dog
        hotdog_id = f"hd_{len(self.menu.hotdogs) + 1:03d}"
        nuevo_hotdog = HotDog(
            id=hotdog_id,
            nombre=nombre,
            pan=pan,
            salchicha=salchicha,
            toppings=toppings,
            salsas=salsas,
            acompanante=acompanante
        )
        
        # Verificar inventario
        if not nuevo_hotdog.verificar_inventario(self.inventario):
            print("¡Advertencia! No hay suficiente inventario para este hot dog.")
            confirmacion = input("¿Desea agregarlo de todas formas? (s/n): ")
            if confirmacion.lower() != 's':
                print("Registro cancelado.")
                return False
        
        self.menu.agregar_hotdog(nuevo_hotdog)
        print(f"Hot dog '{nombre}' agregado exitosamente al menú!")
        return True
    
    def _seleccionar_ingredientes_multiples(self, categoria: CategoriaIngrediente, nombre_plural: str) -> List[Ingrediente]:
        ingredientes_disponibles = self.gestor_ingredientes.listar_por_categoria(categoria)
        seleccionados = []
        
        print(f"\n{nombre_plural.capitalize()} disponibles:")
        for i, ing in enumerate(ingredientes_disponibles, 1):
            print(f"{i}. {ing.nombre} ({ing.tipo})")
        
        while True:
            seleccion = input(f"Seleccione un {nombre_plural[:-1]} (0 para terminar): ")
            if seleccion == '0':
                break
            try:
                idx = int(seleccion) - 1
                if 0 <= idx < len(ingredientes_disponibles):
                    seleccionados.append(ingredientes_disponibles[idx])
                    print(f"{ingredientes_disponibles[idx].nombre} agregado.")
                else:
                    print("Selección inválida.")
            except ValueError:
                print("Por favor ingrese un número válido.")
        
        return seleccionados
    
    def _validar_longitud_pan_salchicha(self, pan: Ingrediente, salchicha: Ingrediente) -> bool:
        # Implementación básica - puede expandirse según reglas específicas
        return len(pan.nombre) >= len(salchicha.nombre)
    
    def eliminar_hotdog(self):
        self.ver_lista_hotdogs()
        if not self.menu.hotdogs:
            return
        
        try:
            seleccion = int(input("\nSeleccione el hot dog a eliminar: ")) - 1
            hotdog = self.menu.hotdogs[seleccion]
            
            # Verificar inventario
            if hotdog.verificar_inventario(self.inventario):
                confirmacion = input("¡Advertencia! Aún hay inventario para este hot dog. ¿Está seguro de eliminarlo? (s/n): ")
                if confirmacion.lower() != 's':
                    print("Eliminación cancelada.")
                    return False
            
            self.menu.eliminar_hotdog(hotdog)
            print(f"Hot dog '{hotdog.nombre}' eliminado exitosamente.")
            return True
        except (ValueError, IndexError):
            print("Selección inválida.")
            return False

class SimulacionVentas:
    def __init__(self, menu: Menu, inventario: Inventario):
        self.menu = menu
        self.inventario = inventario
        self.ventas_exitosas = 0
        self.clientes_cambiaron_opinion = 0
        self.clientes_no_pudieron_comprar = 0
        self.total_hotdogs_vendidos = 0
        self.acompanantes_vendidos = 0
        self.hotdogs_vendidos = {}
        self.hotdogs_fallidos = {}
        self.ingredientes_faltantes = {}
    
    def simular_dia(self):
        print("\n=== SIMULANDO DÍA DE VENTAS ===")
        
        num_clientes = random.randint(0, 200)
        print(f"Clientes del día: {num_clientes}")
        
        for cliente_id in range(num_clientes):
            self._procesar_cliente(cliente_id)
        
        self._generar_reporte()
    
    def _procesar_cliente(self, cliente_id: int):
        num_hotdogs = random.randint(0, 5)
        
        if num_hotdogs == 0:
            print(f"El cliente {cliente_id} cambió de opinión")
            self.clientes_cambiaron_opinion += 1
            return
        
        hotdogs_comprados = []
        hotdogs_fallidos = []
        
        for _ in range(num_hotdogs):
            # Seleccionar hot dog aleatorio
            if not self.menu.hotdogs:
                print("No hay hot dogs en el menú!")
                break
            
            hotdog = random.choice(self.menu.hotdogs)
            
            # Verificar si se puede vender
            if hotdog.verificar_inventario(self.inventario):
                hotdogs_comprados.append(hotdog)
                # Registrar venta
                self.hotdogs_vendidos[hotdog.id] = self.hotdogs_vendidos.get(hotdog.id, 0) + 1
                
                # Consumir del inventario
                hotdog.consumir_del_inventario(self.inventario)
                self.total_hotdogs_vendidos += 1
                
                # Acompañante adicional
                if random.choice([True, False]):
                    self.acompanantes_vendidos += 1
            else:
                hotdogs_fallidos.append(hotdog)
                # Registrar fallo
                self.hotdogs_fallidos[hotdog.id] = self.hotdogs_fallidos.get(hotdog.id, 0) + 1
                
                # Identificar ingrediente faltante
                ingrediente_faltante = self._identificar_ingrediente_faltante(hotdog)
                if ingrediente_faltante:
                    self.ingredientes_faltantes[ingrediente_faltante.id] = self.ingredientes_faltantes.get(ingrediente_faltante.id, 0) + 1
        
        if hotdogs_comprados:
            print(f"Cliente {cliente_id} compró: {[hd.nombre for hd in hotdogs_comprados]}")
            self.ventas_exitosas += 1
        elif hotdogs_fallidos:
            print(f"Cliente {cliente_id} no pudo comprar: {[hd.nombre for hd in hotdogs_fallidos]}")
            self.clientes_no_pudieron_comprar += 1
    
    def _identificar_ingrediente_faltante(self, hotdog: HotDog) -> Optional[Ingrediente]:
        if not self.inventario.hay_suficiente(hotdog.pan, 1):
            return hotdog.pan
        if not self.inventario.hay_suficiente(hotdog.salchicha, 1):
            return hotdog.salchicha
        for topping in hotdog.toppings:
            if not self.inventario.hay_suficiente(topping, 1):
                return topping
        for salsa in hotdog.salsas:
            if not self.inventario.hay_suficiente(salsa, 1):
                return salsa
        if hotdog.acompanante and not self.inventario.hay_suficiente(hotdog.acompanante, 1):
            return hotdog.acompanante
        return None
    
    def _generar_reporte(self):
        print("\n=== REPORTE DEL DÍA ===")
        print(f"Total de clientes: {self.ventas_exitosas + self.clientes_cambiaron_opinion + self.clientes_no_pudieron_comprar}")
        print(f"Clientes que cambiaron de opinión: {self.clientes_cambiaron_opinion}")
        print(f"Clientes que no pudieron comprar: {self.clientes_no_pudieron_comprar}")
        print(f"Clientes que compraron exitosamente: {self.ventas_exitosas}")
        
        if self.ventas_exitosas > 0:
            promedio = self.total_hotdogs_vendidos / self.ventas_exitosas
            print(f"Promedio de hot dogs por cliente: {promedio:.2f}")
        
        # Hot dog más vendido
        if self.hotdogs_vendidos:
            mas_vendido_id = max(self.hotdogs_vendidos, key=self.hotdogs_vendidos.get)
            mas_vendido = next((hd for hd in self.menu.hotdogs if hd.id == mas_vendido_id), None)
            if mas_vendido:
                print(f"Hot dog más vendido: {mas_vendido.nombre} ({self.hotdogs_vendidos[mas_vendido_id]} ventas)")
        
        # Hot dogs que causaron problemas
        if self.hotdogs_fallidos:
            print("\nHot dogs que causaron que clientes se marcharan:")
            for hd_id, count in self.hotdogs_fallidos.items():
                hotdog = next((hd for hd in self.menu.hotdogs if hd.id == hd_id), None)
                if hotdog:
                    print(f"  - {hotdog.nombre}: {count} veces")
        
        # Ingredientes faltantes
        if self.ingredientes_faltantes:
            print("\nIngredientes que causaron problemas:")
            for ing_id, count in self.ingredientes_faltantes.items():
                # Buscar ingrediente por ID (necesitaríamos acceso al gestor de ingredientes)
                print(f"  - Ingrediente ID {ing_id}: {count} veces")
        
        print(f"Total de acompañantes vendidos: {self.acompanantes_vendidos}")

class SistemaHotDog:
    def __init__(self):
        self.gestor_ingredientes = GestorIngredientes()
        self.inventario = Inventario()
        self.menu = Menu()
        self.gestor_inventario = GestorInventario(self.inventario, self.gestor_ingredientes)
        self.gestor_menu = GestorMenu(self.menu, self.inventario, self.gestor_ingredientes)
        self.archivo_local = "datos_locales.json"
    
    def cargar_datos_desde_api(self):
        try:
            print("Cargando datos desde la API de GitHub...")
            
            # URLs de los archivos JSON en el repositorio
            urls = {
                "ingredientes": "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-1/main/ingredientes.json",
                "inventario": "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-1/main/inventario.json",
                "menu": "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-1/main/menu.json"
            }
            
            # Cargar ingredientes
            response = requests.get(urls["ingredientes"])
            if response.status_code == 200:
                datos_ingredientes = response.json()
                self.gestor_ingredientes.cargar_desde_lista(datos_ingredientes)
                print(f"Cargados {len(datos_ingredientes)} ingredientes")
            else:
                print("Error al cargar ingredientes desde la API")
                return False
            
            # Cargar inventario
            response = requests.get(urls["inventario"])
            if response.status_code == 200:
                datos_inventario = response.json()
                for item in datos_inventario:
                    ingrediente = self.gestor_ingredientes.buscar_por_id(item["ingrediente_id"])
                    if ingrediente:
                        self.inventario.agregar_ingrediente(ingrediente, item["cantidad"])
                print(f"Cargado inventario con {len(datos_inventario)} items")
            else:
                print("Error al cargar inventario desde la API")
                return False
            
            # Cargar menú (esto sería más complejo en una implementación real)
            # Por simplicidad, asumimos que el menú viene en un formato específico
            
            print("Datos cargados exitosamente desde la API")
            return True
            
        except Exception as e:
            print(f"Error al cargar datos desde la API: {e}")
            return False
    
    def cargar_datos_locales(self):
        try:
            if os.path.exists(self.archivo_local):
                with open(self.archivo_local, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                
                # Cargar ingredientes locales
                if 'ingredientes' in datos:
                    for ing_data in datos['ingredientes']:
                        ingrediente = Ingrediente.from_dict(ing_data)
                        # Solo agregar si no existe
                        if not self.gestor_ingredientes.buscar_por_id(ingrediente.id):
                            self.gestor_ingredientes.agregar_ingrediente(ingrediente)
                
                # Cargar inventario local
                if 'inventario' in datos:
                    for inv_data in datos['inventario']:
                        ingrediente = self.gestor_ingredientes.buscar_por_id(inv_data['ingrediente_id'])
                        if ingrediente:
                            self.inventario.actualizar_existencia(ingrediente, inv_data['cantidad'])
                
                print("Datos locales cargados exitosamente")
                return True
            else:
                print("No hay archivo local de datos")
                return False
                
        except Exception as e:
            print(f"Error al cargar datos locales: {e}")
            return False
    
    def guardar_datos_locales(self):
        try:
            datos = {
                'ingredientes': [],
                'inventario': []
            }
            
            # Guardar ingredientes (solo los locales - en una implementación real
            # necesitaríamos identificar cuáles son locales vs de la API)
            for ingrediente in self.gestor_ingredientes.ingredientes:
                datos['ingredientes'].append(ingrediente.to_dict())
            
            # Guardar inventario
            for ing_id, cantidad in self.inventario.existencias.items():
                datos['inventario'].append({
                    'ingrediente_id': ing_id,
                    'cantidad': cantidad
                })
            
            with open(self.archivo_local, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            print("Datos locales guardados exitosamente")
            return True
            
        except Exception as e:
            print(f"Error al guardar datos locales: {e}")
            return False
    
    def mostrar_menu_principal(self):
        print("\n" + "="*50)
        print("        HOT DOG CCS 🌭 - SISTEMA PRINCIPAL")
        print("="*50)
        print("1. Gestión de Ingredientes")
        print("2. Gestión de Inventario")
        print("3. Gestión del Menú")
        print("4. Simular un día de ventas")
        print("5. Guardar datos locales")
        print("6. Salir")
        print("="*50)
    
    def ejecutar_gestion_ingredientes(self):
        while True:
            print("\n--- GESTIÓN DE INGREDIENTES ---")
            print("1. Listar productos por categoría")
            print("2. Listar productos por categoría y tipo")
            print("3. Agregar ingrediente")
            print("4. Eliminar ingrediente")
            print("5. Volver al menú principal")
            
            opcion = input("Seleccione una opción: ")
            
            if opcion == '1':
                print("\nCategorías disponibles:")
                for i, cat in enumerate(CategoriaIngrediente, 1):
                    print(f"{i}. {cat.value}")
                try:
                    cat_idx = int(input("Seleccione categoría: ")) - 1
                    categoria = list(CategoriaIngrediente)[cat_idx]
                    ingredientes = self.gestor_ingredientes.listar_por_categoria(categoria)
                    print(f"\nIngredientes en {categoria.value}:")
                    for ing in ingredientes:
                        print(f"  - {ing.nombre} ({ing.tipo})")
                except (ValueError, IndexError):
                    print("Selección inválida.")
            
            elif opcion == '2':
                print("\nCategorías disponibles:")
                for i, cat in enumerate(CategoriaIngrediente, 1):
                    print(f"{i}. {cat.value}")
                try:
                    cat_idx = int(input("Seleccione categoría: ")) - 1
                    categoria = list(CategoriaIngrediente)[cat_idx]
                    tipo = input("Ingrese el tipo: ")
                    ingredientes = self.gestor_ingredientes.listar_por_categoria_y_tipo(categoria, tipo)
                    print(f"\nIngredientes en {categoria.value} - {tipo}:")
                    for ing in ingredientes:
                        print(f"  - {ing.nombre}")
                except (ValueError, IndexError):
                    print("Selección inválida.")
            
            elif opcion == '3':
                print("\nAgregar nuevo ingrediente:")
                nombre = input("Nombre: ")
                print("Categorías:")
                for i, cat in enumerate(CategoriaIngrediente, 1):
                    print(f"{i}. {cat.value}")
                try:
                    cat_idx = int(input("Seleccione categoría: ")) - 1
                    categoria = list(CategoriaIngrediente)[cat_idx]
                    tipo = input("Tipo: ")
                    
                    ingrediente_id = f"ing_{len(self.gestor_ingredientes.ingredientes) + 1:03d}"
                    nuevo_ingrediente = Ingrediente(
                        id=ingrediente_id,
                        nombre=nombre,
                        categoria=categoria,
                        tipo=tipo
                    )
                    
                    self.gestor_ingredientes.agregar_ingrediente(nuevo_ingrediente)
                    print(f"Ingrediente '{nombre}' agregado exitosamente!")
                    
                except (ValueError, IndexError):
                    print("Selección inválida.")
            
            elif opcion == '4':
                nombre = input("Nombre del ingrediente a eliminar: ")
                ingrediente = self.gestor_ingredientes.buscar_por_nombre(nombre)
                if ingrediente:
                    self.gestor_ingredientes.eliminar_ingrediente(ingrediente, self.menu)
                else:
                    print("Ingrediente no encontrado.")
            
            elif opcion == '5':
                break
            else:
                print("Opción inválida.")
    
    def ejecutar_gestion_inventario(self):
        while True:
            print("\n--- GESTIÓN DE INVENTARIO ---")
            print("1. Visualizar todo el inventario")
            print("2. Buscar existencia de ingrediente")
            print("3. Listar existencias por categoría")
            print("4. Actualizar existencia de producto")
            print("5. Volver al menú principal")
            
            opcion = input("Seleccione una opción: ")
            
            if opcion == '1':
                self.gestor_inventario.visualizar_todo()
            
            elif opcion == '2':
                nombre = input("Nombre del ingrediente: ")
                existencia = self.gestor_inventario.buscar_existencia(nombre)
                if existencia is not None:
                    print(f"Existencia: {existencia}")
                else:
                    print("Ingrediente no encontrado.")
            
            elif opcion == '3':
                print("\nCategorías disponibles:")
                for i, cat in enumerate(CategoriaIngrediente, 1):
                    print(f"{i}. {cat.value}")
                try:
                    cat_idx = int(input("Seleccione categoría: ")) - 1
                    categoria = list(CategoriaIngrediente)[cat_idx]
                    self.gestor_inventario.listar_existencias_por_categoria(categoria)
                except (ValueError, IndexError):
                    print("Selección inválida.")
            
            elif opcion == '4':
                nombre = input("Nombre del ingrediente: ")
                try:
                    nueva_cantidad = int(input("Nueva cantidad: "))
                    self.gestor_inventario.actualizar_existencia(nombre, nueva_cantidad)
                except ValueError:
                    print("Cantidad inválida.")
            
            elif opcion == '5':
                break
            else:
                print("Opción inválida.")
    
    def ejecutar_gestion_menu(self):
        while True:
            print("\n--- GESTIÓN DEL MENÚ ---")
            print("1. Ver lista de hot dogs")
            print("2. Ver inventario para hot dog específico")
            print("3. Agregar nuevo hot dog")
            print("4. Eliminar hot dog")
            print("5. Volver al menú principal")
            
            opcion = input("Seleccione una opción: ")
            
            if opcion == '1':
                self.gestor_menu.ver_lista_hotdogs()
            
            elif opcion == '2':
                self.gestor_menu.ver_lista_hotdogs()
                if self.menu.hotdogs:
                    try:
                        seleccion = int(input("Seleccione el hot dog: ")) - 1
                        hotdog = self.menu.hotdogs[seleccion]
                        disponible = self.gestor_menu.verificar_inventario_para_hotdog(hotdog)
                        estado = "DISPONIBLE" if disponible else "SIN INVENTARIO"
                        print(f"Estado: {estado}")
                    except (ValueError, IndexError):
                        print("Selección inválida.")
            
            elif opcion == '3':
                self.gestor_menu.agregar_nuevo_hotdog()
            
            elif opcion == '4':
                self.gestor_menu.eliminar_hotdog()
            
            elif opcion == '5':
                break
            else:
                print("Opción inválida.")
    
    def ejecutar(self):
        print("Iniciando sistema Hot Dog CCS...")
        
        # Cargar datos
        if not self.cargar_datos_desde_api():
            print("Usando datos de respaldo...")
        
        self.cargar_datos_locales()
        
        # Menú principal
        while True:
            self.mostrar_menu_principal()
            opcion = input("Seleccione una opción: ")
            
            if opcion == '1':
                self.ejecutar_gestion_ingredientes()
            elif opcion == '2':
                self.ejecutar_gestion_inventario()
            elif opcion == '3':
                self.ejecutar_gestion_menu()
            elif opcion == '4':
                simulador = SimulacionVentas(self.menu, self.inventario)
                simulador.simular_dia()
            elif opcion == '5':
                self.guardar_datos_locales()
            elif opcion == '6':
                print("¡Gracias por usar Hot Dog CCS! 🌭")
                break
            else:
                print("Opción inválida. Por favor seleccione 1-6.")

# Ejecutar el sistema
if __name__ == "__main__":
    sistema = SistemaHotDog()
    sistema.ejecutar()