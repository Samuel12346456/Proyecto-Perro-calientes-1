from typing import List
from menu import Menu
from inventario import Inventario
from hotdogs import HotDog
from ingredientes import Ingrediente, CategoriaIngrediente
from gestor_ingredientes import GestorIngredientes

class GestorMenu:
    def __init__(self, menu: Menu, inventario: Inventario, gestor_ingredientes: GestorIngredientes):
        self.menu = menu
        self.inventario = inventario
        self.gestor_ingredientes = gestor_ingredientes
    
    def ver_lista_hotdogs(self):
        print("\n=== MENÚ DE HOT DOGS ===")
        for i, hotdog in enumerate(self.menu.listar_hotdogs(), 1):
            disponible = "✓" if hotdog.verificar_inventario(self.inventario) else "✗"
            print(f"{i}. {hotdog.nombre} - ${hotdog.precio_venta:.2f} [{disponible}]")
    
    def verificar_inventario_para_hotdog(self, hotdog: HotDog) -> bool:
        return hotdog.verificar_inventario(self.inventario)
    
    def mostrar_inventario_hotdog_detallado(self, hotdog: HotDog):
        """Muestra el inventario detallado de cada ingrediente del hot dog"""
        print(f"\n INVENTARIO DETALLADO PARA: {hotdog.nombre}")
        print("=" * 60)
        print(f" Precio de venta: ${hotdog.precio_venta:.2f}")
        print(f" Costo de ingredientes: ${hotdog.costo_ingredientes:.2f}")
        print(f" Margen de ganancia: ${hotdog.margen_ganancia:.2f}")
        print("=" * 60)
        
        # Verificar pan
        existencia_pan = self.inventario.verificar_existencia(hotdog.pan)
        estado_pan = "✅ SUFICIENTE" if existencia_pan >= 1 else "❌ INSUFICIENTE"
        print(f" PAN: {hotdog.pan.nombre} ({hotdog.pan.tipo})")
        print(f"   Costo: ${hotdog.pan.costo:.2f}")
        print(f"   Cantidad necesaria: 1 unidad")
        print(f"   Existencia actual: {existencia_pan} unidades")
        print(f"   Estado: {estado_pan}")
        print()
        
        # Verificar salchicha
        existencia_salchicha = self.inventario.verificar_existencia(hotdog.salchicha)
        estado_salchicha = "✅ SUFICIENTE" if existencia_salchicha >= 1 else "❌ INSUFICIENTE"
        print(f" SALCHICHA: {hotdog.salchicha.nombre} ({hotdog.salchicha.tipo})")
        print(f"   Costo: ${hotdog.salchicha.costo:.2f}")
        print(f"   Cantidad necesaria: 1 unidad")
        print(f"   Existencia actual: {existencia_salchicha} unidades")
        print(f"   Estado: {estado_salchicha}")
        print()
        
        # Verificar toppings
        if hotdog.toppings:
            print(f" TOPPINGS ({len(hotdog.toppings)}):")
            for i, topping in enumerate(hotdog.toppings, 1):
                existencia_topping = self.inventario.verificar_existencia(topping)
                estado_topping = "✅ SUFICIENTE" if existencia_topping >= 1 else "❌ INSUFICIENTE"
                print(f"   {i}. {topping.nombre} ({topping.tipo})")
                print(f"      Costo: ${topping.costo:.2f}")
                print(f"      Cantidad necesaria: 1 unidad")
                print(f"      Existencia actual: {existencia_topping} unidades")
                print(f"      Estado: {estado_topping}")
        else:
            print(" TOPPINGS: No hay toppings seleccionados")
        print()
        
        # Verificar salsas
        if hotdog.salsas:
            print(f" SALSAS ({len(hotdog.salsas)}):")
            for i, salsa in enumerate(hotdog.salsas, 1):
                existencia_salsa = self.inventario.verificar_existencia(salsa)
                estado_salsa = "✅ SUFICIENTE" if existencia_salsa >= 1 else "❌ INSUFICIENTE"
                print(f"   {i}. {salsa.nombre} ({salsa.tipo})")
                print(f"      Costo: ${salsa.costo:.2f}")
                print(f"      Cantidad necesaria: 1 unidad")
                print(f"      Existencia actual: {existencia_salsa} unidades")
                print(f"      Estado: {estado_salsa}")
        else:
            print(" SALSAS: No hay salsas seleccionadas")
        print()
        
        # Verificar acompañante
        if hotdog.acompanante:
            existencia_acompanante = self.inventario.verificar_existencia(hotdog.acompanante)
            estado_acompanante = "✅ SUFICIENTE" if existencia_acompanante >= 1 else "❌ INSUFICIENTE"
            print(f" ACOMPAÑANTE: {hotdog.acompanante.nombre} ({hotdog.acompanante.tipo})")
            print(f"   Costo: ${hotdog.acompanante.costo:.2f}")
            print(f"   Cantidad necesaria: 1 unidad")
            print(f"   Existencia actual: {existencia_acompanante} unidades")
            print(f"   Estado: {estado_acompanante}")
        else:
            print(" ACOMPAÑANTE: No hay acompañante seleccionado")
        print()
        
        # Resumen general
        disponible = self.verificar_inventario_para_hotdog(hotdog)
        estado_general = "✅ DISPONIBLE" if disponible else "❌ NO DISPONIBLE"
        print("=" * 60)
        print(f"ESTADO GENERAL DEL HOT DOG: {estado_general}")
        
        if disponible:
            print(" Este hot dog puede ser preparado con el inventario actual")
        else:
            print("⚠️  Este hot dog NO puede ser preparado por falta de ingredientes")
        
        return disponible
    
    def agregar_nuevo_hotdog(self):
        print("\n=== AGREGAR NUEVO HOT DOG ===")
        
        nombre = input("Nombre del hot dog: ")
        
        # Seleccionar pan
        panes = self.gestor_ingredientes.listar_por_categoria(CategoriaIngrediente.PAN)
        print("\nPanes disponibles:")
        for i, pan in enumerate(panes, 1):
            existencia = self.inventario.verificar_existencia(pan)
            print(f"{i}. {pan.nombre} ({pan.tipo}) - Costo: ${pan.costo:.2f} - Existencia: {existencia}")
        pan_idx = int(input("Seleccione el pan: ")) - 1
        pan = panes[pan_idx]
        
        # Seleccionar salchicha
        salchichas = self.gestor_ingredientes.listar_por_categoria(CategoriaIngrediente.SALCHICHA)
        print("\nSalchichas disponibles:")
        for i, salchicha in enumerate(salchichas, 1):
            existencia = self.inventario.verificar_existencia(salchicha)
            print(f"{i}. {salchicha.nombre} ({salchicha.tipo}) - Costo: ${salchicha.costo:.2f} - Existencia: {existencia}")
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
                existencia = self.inventario.verificar_existencia(acomp)
                print(f"{i}. {acomp.nombre} ({acomp.tipo}) - Costo: ${acomp.costo:.2f} - Existencia: {existencia}")
            acomp_idx = int(input("Seleccione el acompañante: ")) - 1
            acompanante = acompanantes[acomp_idx]
        
        # Calcular costo total de ingredientes
        costo_total = pan.costo + salchicha.costo
        for topping in toppings:
            costo_total += topping.costo
        for salsa in salsas:
            costo_total += salsa.costo
        if acompanante:
            costo_total += acompanante.costo
        
        print(f"\n Costo total de ingredientes: ${costo_total:.2f}")
        
        # Solicitar precio de venta
        while True:
            try:
                precio_venta = float(input("Precio de venta del hot dog: $"))
                if precio_venta < costo_total:
                    confirmacion = input(f"¡Advertencia! El precio de venta (${precio_venta:.2f}) es menor que el costo (${costo_total:.2f}). ¿Desea continuar? (s/n): ")
                    if confirmacion.lower() != 's':
                        continue
                break
            except ValueError:
                print("Por favor ingrese un precio válido.")
        
        # Crear hot dog
        hotdog_id = f"hd_{len(self.menu.hotdogs) + 1:03d}"
        nuevo_hotdog = HotDog(
            id=hotdog_id,
            nombre=nombre,
            pan=pan,
            salchicha=salchicha,
            toppings=toppings,
            salsas=salsas,
            acompanante=acompanante,
            precio_venta=precio_venta
        )
        
        # Mostrar resumen financiero
        print(f"\n RESUMEN FINANCIERO:")
        print(f"   Costo de ingredientes: ${nuevo_hotdog.costo_ingredientes:.2f}")
        print(f"   Precio de venta: ${nuevo_hotdog.precio_venta:.2f}")
        print(f"   Margen de ganancia: ${nuevo_hotdog.margen_ganancia:.2f}")
        print(f"   Margen porcentual: {(nuevo_hotdog.margen_ganancia / nuevo_hotdog.precio_venta * 100):.1f}%")
        
        # Verificar inventario
        if not nuevo_hotdog.verificar_inventario(self.inventario):
            print("¡Advertencia! No hay suficiente inventario para este hot dog.")
            # Mostrar inventario detallado
            self.mostrar_inventario_hotdog_detallado(nuevo_hotdog)
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
            existencia = self.inventario.verificar_existencia(ing)
            print(f"{i}. {ing.nombre} ({ing.tipo}) - Costo: ${ing.costo:.2f} - Existencia: {existencia}")
        
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