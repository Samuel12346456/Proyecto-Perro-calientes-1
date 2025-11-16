import random
from typing import Optional, Dict
from menu import Menu
from inventario import Inventario
from hotdogs import HotDog
from ingredientes import Ingrediente

class SimulacionVentas:
    def __init__(self, menu: Menu, inventario: Inventario):
        self.menu = menu
        self.inventario = inventario
        self.ventas_exitosas = 0
        self.clientes_no_pudieron_comprar = 0
        self.total_hotdogs_vendidos = 0
        self.acompanantes_vendidos = 0
        self.hotdogs_vendidos = {}
        self.hotdogs_fallidos = {}
        self.ingredientes_faltantes = {}
        self.ingresos_totales = 0.0
        self.costos_totales = 0.0
    
    def simular_dias(self):
        print("\n=== SIMULACIÓN DE VENTAS ===")
        
        while True:
            print("\n¿Cuántos días desea simular?")
            print("1. 1 día")
            print("2. 2 días")
            print("3. Volver al menú principal")
            
            opcion = input("Seleccione una opción: ")
            
            if opcion == '1':
                self._simular_un_dia()
                break
            elif opcion == '2':
                self._simular_dos_dias()
                break
            elif opcion == '3':
                return
            else:
                print("Opción inválida. Por favor seleccione 1, 2 o 3.")
    
    def _simular_un_dia(self):
        print("\n=== SIMULANDO 1 DÍA DE VENTAS ===")
        
        num_clientes = random.randint(50, 150)
        print(f"Clientes del día: {num_clientes}")
        
        # Reiniciar contadores para la simulación
        self._reiniciar_contadores()
        
        for cliente_id in range(num_clientes):
            self._procesar_cliente(cliente_id)
        
        self._generar_reporte("DÍA 1")
    
    def _simular_dos_dias(self):
        print("\n=== SIMULANDO 2 DÍAS DE VENTAS ===")
        
        # Reiniciar contadores para la simulación completa
        self._reiniciar_contadores()
        
        # Simular día 1
        num_clientes_dia1 = random.randint(50, 150)
        print(f"\n--- DÍA 1 ---")
        print(f"Clientes del día 1: {num_clientes_dia1}")
        
        for cliente_id in range(num_clientes_dia1):
            self._procesar_cliente(cliente_id)
        
        # Guardar resultados del día 1
        resultados_dia1 = self._obtener_resultados_parciales()
        
        # Simular día 2
        num_clientes_dia2 = random.randint(50, 150)
        print(f"\n--- DÍA 2 ---")
        print(f"Clientes del día 2: {num_clientes_dia2}")
        
        for cliente_id in range(num_clientes_dia1, num_clientes_dia1 + num_clientes_dia2):
            self._procesar_cliente(cliente_id)
        
        # Generar reporte comparativo
        self._generar_reporte_comparativo(resultados_dia1, num_clientes_dia1, num_clientes_dia2)
    
    def _reiniciar_contadores(self):
        """Reinicia todos los contadores para una nueva simulación"""
        self.ventas_exitosas = 0
        self.clientes_no_pudieron_comprar = 0
        self.total_hotdogs_vendidos = 0
        self.acompanantes_vendidos = 0
        self.hotdogs_vendidos = {}
        self.hotdogs_fallidos = {}
        self.ingredientes_faltantes = {}
        self.ingresos_totales = 0.0
        self.costos_totales = 0.0
    
    def _obtener_resultados_parciales(self):
        """Obtiene los resultados actuales para comparación"""
        return {
            'ventas_exitosas': self.ventas_exitosas,
            'clientes_no_pudieron_comprar': self.clientes_no_pudieron_comprar,
            'total_hotdogs_vendidos': self.total_hotdogs_vendidos,
            'acompanantes_vendidos': self.acompanantes_vendidos,
            'ingresos_totales': self.ingresos_totales,
            'costos_totales': self.costos_totales,
            'hotdogs_vendidos': self.hotdogs_vendidos.copy(),
            'hotdogs_fallidos': self.hotdogs_fallidos.copy()
        }

    def _procesar_cliente(self, cliente_id: int):
        # Determinar si el cliente cambia de opinión ANTES de decidir comprar
        cambia_opinion = random.random() < 0.1  # 10% de probabilidad de cambiar de opinión
        
        if cambia_opinion:
            print(f"El cliente {cliente_id} cambió de opinión y no compró nada")
            # Ahora contamos esto como "no pudo comprar"
            self.clientes_no_pudieron_comprar += 1
            return
        
        # Si no cambió de opinión, decide cuántos hot dogs comprar
        num_hotdogs = random.randint(1, 3)  # Entre 1 y 3 hot dogs por cliente
        
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
                
                # Registrar ingresos y costos
                self.ingresos_totales += hotdog.precio_venta
                self.costos_totales += hotdog.costo_ingredientes
                
                # Acompañante adicional (50% de probabilidad)
                if random.choice([True, False]):
                    self.acompanantes_vendidos += 1
                    # Asumimos que el acompañante cuesta $1 y se vende a $2
                    self.ingresos_totales += 2.0
                    self.costos_totales += 1.0
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

    def _generar_reporte(self, titulo: str):
        print(f"\n=== REPORTE {titulo} ===")
        total_clientes = self.ventas_exitosas + self.clientes_no_pudieron_comprar
        
        print(f"Total de clientes: {total_clientes}")
        print(f"Clientes que compraron exitosamente: {self.ventas_exitosas}")
        print(f"Clientes que no pudieron comprar: {self.clientes_no_pudieron_comprar}")
        
        if total_clientes > 0:
            porcentaje_exitos = (self.ventas_exitosas / total_clientes) * 100
            porcentaje_fallos = (self.clientes_no_pudieron_comprar / total_clientes) * 100
            print(f"Tasa de éxito: {porcentaje_exitos:.1f}%")
            print(f"Tasa de fallos: {porcentaje_fallos:.1f}%")
        
        if self.ventas_exitosas > 0:
            promedio = self.total_hotdogs_vendidos / self.ventas_exitosas
            print(f"Promedio de hot dogs por cliente exitoso: {promedio:.2f}")
        
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
                # Buscar en todos los ingredientes disponibles
                ingrediente_encontrado = None
                for hotdog in self.menu.hotdogs:
                    if hotdog.pan.id == ing_id:
                        ingrediente_encontrado = hotdog.pan
                        break
                    if hotdog.salchicha.id == ing_id:
                        ingrediente_encontrado = hotdog.salchicha
                        break
                    for topping in hotdog.toppings:
                        if topping.id == ing_id:
                            ingrediente_encontrado = topping
                            break
                    for salsa in hotdog.salsas:
                        if salsa.id == ing_id:
                            ingrediente_encontrado = salsa
                            break
                    if hotdog.acompanante and hotdog.acompanante.id == ing_id:
                      ingrediente_encontrado = hotdog.acompanante
                    break
                
                if ingrediente_encontrado:
                    print(f"  - {ingrediente_encontrado.nombre}: {count} veces")
                else:
                    print(f"  - Ingrediente ID {ing_id}: {count} veces")
        
        print(f"\nTotal de hot dogs vendidos: {self.total_hotdogs_vendidos}")
        print(f"Total de acompañantes vendidos: {self.acompanantes_vendidos}")
        
        # Información financiera
        ganancia_neta = self.ingresos_totales - self.costos_totales
        margen_ganancia = (ganancia_neta / self.ingresos_totales * 100) if self.ingresos_totales > 0 else 0
        
        print(f"\n INFORMACIÓN FINANCIERA:")
        print(f"   Ingresos totales: ${self.ingresos_totales:.2f}")
        print(f"   Costos totales: ${self.costos_totales:.2f}")
        print(f"   Ganancia neta: ${ganancia_neta:.2f}")
        print(f"   Margen de ganancia: {margen_ganancia:.1f}%")

    def _generar_reporte_comparativo(self, resultados_dia1, num_clientes_dia1, num_clientes_dia2):
        """Genera un reporte comparativo entre los dos días"""
        total_clientes = num_clientes_dia1 + num_clientes_dia2
        
        print("\n" + "="*60)
        print("           REPORTE COMPARATIVO - 2 DÍAS")
        print("="*60)
        
        print(f"\n RESUMEN GENERAL:")
        print(f"Total de clientes en 2 días: {total_clientes}")
        print(f"  - Día 1: {num_clientes_dia1} clientes")
        print(f"  - Día 2: {num_clientes_dia2} clientes")
        print(f"Total de hot dogs vendidos: {self.total_hotdogs_vendidos}")
        print(f"Total de acompañantes vendidos: {self.acompanantes_vendidos}")
        
        print(f"\n COMPARATIVO POR DÍA:")
        print(f"{'MÉTRICA':<25} {'DÍA 1':<10} {'DÍA 2':<10} {'TOTAL':<10}")
        print("-" * 55)
        print(f"{'Clientes exitosos':<25} {resultados_dia1['ventas_exitosas']:<10} {self.ventas_exitosas - resultados_dia1['ventas_exitosas']:<10} {self.ventas_exitosas:<10}")
        print(f"{'Clientes fallidos':<25} {resultados_dia1['clientes_no_pudieron_comprar']:<10} {self.clientes_no_pudieron_comprar - resultados_dia1['clientes_no_pudieron_comprar']:<10} {self.clientes_no_pudieron_comprar:<10}")
        print(f"{'Hot dogs vendidos':<25} {resultados_dia1['total_hotdogs_vendidos']:<10} {self.total_hotdogs_vendidos - resultados_dia1['total_hotdogs_vendidos']:<10} {self.total_hotdogs_vendidos:<10}")
        print(f"{'Acompañantes vendidos':<25} {resultados_dia1['acompanantes_vendidos']:<10} {self.acompanantes_vendidos - resultados_dia1['acompanantes_vendidos']:<10} {self.acompanantes_vendidos:<10}")
        
        # Tasas de éxito por día
        tasa_dia1 = (resultados_dia1['ventas_exitosas'] / num_clientes_dia1 * 100) if num_clientes_dia1 > 0 else 0
        tasa_dia2 = ((self.ventas_exitosas - resultados_dia1['ventas_exitosas']) / num_clientes_dia2 * 100) if num_clientes_dia2 > 0 else 0
        tasa_total = (self.ventas_exitosas / total_clientes * 100) if total_clientes > 0 else 0
        
        print(f"\n TASAS DE ÉXITO:")
        print(f"  Día 1: {tasa_dia1:.1f}%")
        print(f"  Día 2: {tasa_dia2:.1f}%")
        print(f"  Total: {tasa_total:.1f}%")
        
        # Hot dog más vendido en general
        if self.hotdogs_vendidos:
            mas_vendido_id = max(self.hotdogs_vendidos, key=self.hotdogs_vendidos.get)
            mas_vendido = next((hd for hd in self.menu.hotdogs if hd.id == mas_vendido_id), None)
            if mas_vendido:
                print(f"\n HOT DOG MÁS VENDIDO (2 días):")
                print(f"  {mas_vendido.nombre} - {self.hotdogs_vendidos[mas_vendido_id]} ventas")
        
        # Información financiera comparativa
        ingresos_dia1 = resultados_dia1['ingresos_totales']
        ingresos_dia2 = self.ingresos_totales - resultados_dia1['ingresos_totales']
        costos_dia1 = resultados_dia1['costos_totales']
        costos_dia2 = self.costos_totales - resultados_dia1['costos_totales']
        ganancia_dia1 = ingresos_dia1 - costos_dia1
        ganancia_dia2 = ingresos_dia2 - costos_dia2
        ganancia_total = self.ingresos_totales - self.costos_totales
        
        print(f"\n INFORMACIÓN FINANCIERA COMPARATIVA:")
        print(f"{'CONCEPTO':<15} {'DÍA 1':<12} {'DÍA 2':<12} {'TOTAL':<12}")
        print("-" * 51)
        print(f"{'Ingresos':<15} ${ingresos_dia1:<11.2f} ${ingresos_dia2:<11.2f} ${self.ingresos_totales:<11.2f}")
        print(f"{'Costos':<15} ${costos_dia1:<11.2f} ${costos_dia2:<11.2f} ${self.costos_totales:<11.2f}")
        print(f"{'Ganancia':<15} ${ganancia_dia1:<11.2f} ${ganancia_dia2:<11.2f} ${ganancia_total:<11.2f}")
        
        print("="*60)