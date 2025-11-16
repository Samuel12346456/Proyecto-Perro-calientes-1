import json
import requests
import os
from ingredientes import CategoriaIngrediente, Ingrediente
from inventario import Inventario
from menu import Menu
from hotdogs import HotDog
from gestor_ingredientes import GestorIngredientes
from gestor_inventario import GestorInventario
from gestor_menu import GestorMenu
from simulacion_ventas import SimulacionVentas

class SistemaHotDog:
    def __init__(self):
        self.gestor_ingredientes = GestorIngredientes()
        self.inventario = Inventario()
        self.menu = Menu()
        self.gestor_inventario = GestorInventario(self.inventario, self.gestor_ingredientes)
        self.gestor_menu = GestorMenu(self.menu, self.inventario, self.gestor_ingredientes)
        self.archivo_local = "datos_locales.json"
    
    def diagnosticar_estructura_datos(self):
        """Función temporal para diagnosticar la estructura real de los datos"""
        try:
            print("\n DIAGNÓSTICO DE ESTRUCTURA DE DATOS")
            print("="*50)
            
            urls = {
                "ingredientes": "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-1/main/ingredientes.json",
                "menu": "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-1/main/menu.json"
            }
            
            # Diagnosticar ingredientes
            print("\n ESTRUCTURA DE INGREDIENTES:")
            response = requests.get(urls["ingredientes"])
            if response.status_code == 200:
                datos = response.json()
                print(f"Total elementos: {len(datos)}")
                if datos:
                    print("Primeros 3 elementos completos:")
                    for i, elemento in enumerate(datos[:3]):
                        print(f"  {i+1}. {elemento}")
            else:
                print(f"Error al cargar ingredientes: {response.status_code}")
            
            # Diagnosticar menú
            print("\n ESTRUCTURA DEL MENÚ:")
            response = requests.get(urls["menu"])
            if response.status_code == 200:
                datos = response.json()
                print(f"Total elementos: {len(datos)}")
                if datos:
                    print("Primeros 3 elementos completos:")
                    for i, elemento in enumerate(datos[:3]):
                        print(f"  {i+1}. {elemento}")
            else:
                print(f"Error al cargar menú: {response.status_code}")
                
        except Exception as e:
            print(f"Error en diagnóstico: {e}")
    
    def cargar_datos_desde_api(self):
        try:
            print("Cargando datos desde la API de GitHub...")
            
            urls = {
                "ingredientes": "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-1/main/ingredientes.json",
                "menu": "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-1/main/menu.json"
            }
            
            # Cargar y convertir ingredientes
            print("\n Cargando ingredientes...")
            response = requests.get(urls["ingredientes"])
            if response.status_code == 200:
                datos_originales = response.json()
                print(f"   ✅ Datos crudos recibidos: {len(datos_originales)} categorías")
                
                # Convertir estructura anidada a lista plana de ingredientes
                ingredientes_convertidos = self._convertir_estructura_ingredientes(datos_originales)
                print(f"   🔄 Convertidos a {len(ingredientes_convertidos)} ingredientes individuales")
                
                self.gestor_ingredientes.cargar_desde_lista(ingredientes_convertidos)
                print(f"   ✅ Cargados {len(self.gestor_ingredientes.ingredientes)} ingredientes en el sistema")
                
                # Mostrar resumen por categoría
                print("    Resumen por categoría:")
                for categoria in CategoriaIngrediente:
                    ingredientes_cat = self.gestor_ingredientes.listar_por_categoria(categoria)
                    print(f"      {categoria.value}: {len(ingredientes_cat)}")
                    
            else:
                print(f"   ❌ Error HTTP {response.status_code} al cargar ingredientes")
                return False
            
            # Inicializar inventario con cantidades por defecto
            print("\n Inicializando inventario...")
            self._inicializar_inventario_por_defecto()
            print(f"   ✅ Inventario inicializado con {len(self.inventario.existencias)} items")
            
            # Cargar y convertir menú
            print("\n Cargando menú...")
            response = requests.get(urls["menu"])
            if response.status_code == 200:
                datos_originales = response.json()
                print(f"   ✅ Datos crudos recibidos: {len(datos_originales)} hot dogs")
                
                # Convertir estructura del menú
                menu_convertido = self._convertir_estructura_menu(datos_originales)
                print(f"    Hot dogs para procesar: {len(menu_convertido)}")
                
                hotdogs_cargados = 0
                for hd_data in menu_convertido:
                    try:
                        hotdog = self._crear_hotdog_desde_datos_convertidos(hd_data)
                        if hotdog:
                            self.menu.agregar_hotdog(hotdog)
                            hotdogs_cargados += 1
                            print(f"    Hot dog cargado: {hd_data['nombre']}")
                        else:
                            print(f"   ❌ No se pudo crear hot dog: {hd_data['nombre']}")
                    except Exception as e:
                        print(f"   ❌ Error al cargar hot dog {hd_data.get('nombre', 'desconocido')}: {e}")
                        continue
                
                print(f"   ✅ Cargado menú con {hotdogs_cargados} hot dogs")
            else:
                print(f"   ❌ Error HTTP {response.status_code} al cargar menú")
                return False
            
            print("\n DATOS CARGADOS EXITOSAMENTE DESDE LA API")
            return True
            
        except Exception as e:
            print(f"❌ ERROR GENERAL al cargar datos desde la API: {e}")
            print("🔄 Intentando cargar datos de respaldo...")
            return self._cargar_datos_respaldo()

    def _convertir_estructura_ingredientes(self, datos_originales):
        """Convierte la estructura anidada de ingredientes a lista plana"""
        ingredientes_convertidos = []
        
        for categoria_data in datos_originales:
            categoria_nombre = categoria_data.get("Categoria", "").lower()
            
            # Mapear nombres de categorías a nuestras categorías
            categoria_mapeada = self._mapear_categoria(categoria_nombre)
            
            opciones = categoria_data.get("Opciones", [])
            for opcion in opciones:
                ingrediente_convertido = {
                    "id": self._generar_id_ingrediente(opcion["nombre"], categoria_mapeada),
                    "nombre": opcion["nombre"],
                    "categoria": categoria_mapeada.value,
                    "tipo": opcion.get("tipo", opcion.get("base", "General")),
                    "costo": self._calcular_costo_por_defecto(categoria_mapeada)
                }
                ingredientes_convertidos.append(ingrediente_convertido)
        
        return ingredientes_convertidos

    def _mapear_categoria(self, categoria_nombre):
        """Mapea los nombres de categoría del repositorio a nuestras categorías"""
        mapeo = {
            "pan": CategoriaIngrediente.PAN,
            "salchicha": CategoriaIngrediente.SALCHICHA,
            "salsa": CategoriaIngrediente.SALSA,
            "toppings": CategoriaIngrediente.TOPPING,
            "acompañante": CategoriaIngrediente.ACOMPANANTE,
            "acompanante": CategoriaIngrediente.ACOMPANANTE
        }
        return mapeo.get(categoria_nombre.lower(), CategoriaIngrediente.TOPPING)

    def _generar_id_ingrediente(self, nombre, categoria):
        """Genera un ID único para el ingrediente"""
        nombre_sin_espacios = nombre.lower().replace(" ", "_").replace("'", "")
        return f"ing_{categoria.value.lower()}_{nombre_sin_espacios}"

    def _calcular_costo_por_defecto(self, categoria):
        """Calcula costos por defecto basados en la categoría"""
        costos_por_defecto = {
            CategoriaIngrediente.PAN: 0.8,
            CategoriaIngrediente.SALCHICHA: 1.5,
            CategoriaIngrediente.TOPPING: 0.4,
            CategoriaIngrediente.SALSA: 0.3,
            CategoriaIngrediente.ACOMPANANTE: 2.0
        }
        return costos_por_defecto.get(categoria, 0.5)

    def _inicializar_inventario_por_defecto(self):
        """Inicializa el inventario con cantidades por defecto para todos los ingredientes"""
        for ingrediente in self.gestor_ingredientes.ingredientes:
            # Cantidades por defecto basadas en categoría
            if ingrediente.categoria == CategoriaIngrediente.PAN:
                cantidad = 30
            elif ingrediente.categoria == CategoriaIngrediente.SALCHICHA:
                cantidad = 25
            elif ingrediente.categoria == CategoriaIngrediente.TOPPING:
                cantidad = 50
            elif ingrediente.categoria == CategoriaIngrediente.SALSA:
                cantidad = 100
            else:  # Acompañantes
                cantidad = 20
            
            self.inventario.agregar_ingrediente(ingrediente, cantidad)

    def _convertir_estructura_menu(self, datos_originales):
        """Convierte la estructura del menú a nuestro formato"""
        menu_convertido = []
        
        for hotdog_data in datos_originales:
            # Mapear claves (pueden variar entre mayúsculas/minúsculas)
            nombre = hotdog_data.get("nombre", "Hot Dog")
            pan = hotdog_data.get("Pan", hotdog_data.get("pan"))
            salchicha = hotdog_data.get("Salchicha", hotdog_data.get("salchicha"))
            
            # Manejar toppings (puede venir como "toppings" o "Toppings")
            toppings = hotdog_data.get("toppings", hotdog_data.get("Toppings", []))
            
            # Manejar salsas (puede venir como "salsas", "Salsas", o "salsa")
            salsas = hotdog_data.get("salsas", hotdog_data.get("Salsas", hotdog_data.get("salsa", [])))
            
            # Manejar acompañante
            acompanante = hotdog_data.get("Acompañante", hotdog_data.get("acompanante"))
            
            hotdog_convertido = {
                "id": f"hd_{nombre.lower().replace(' ', '_')}",
                "nombre": nombre,
                "pan": pan,
                "salchicha": salchicha,
                "toppings": toppings if isinstance(toppings, list) else [toppings] if toppings else [],
                "salsas": salsas if isinstance(salsas, list) else [salsas] if salsas else [],
                "acompanante": acompanante,
                "precio_venta": self._calcular_precio_por_defecto(len(toppings) if isinstance(toppings, list) else 0)
            }
            menu_convertido.append(hotdog_convertido)
        
        return menu_convertido

    def _calcular_precio_por_defecto(self, num_toppings):
        """Calcula precio por defecto basado en la complejidad del hot dog"""
        precio_base = 5.0
        precio_topping = 0.5
        return precio_base + (num_toppings * precio_topping)

    def _crear_hotdog_desde_datos_convertidos(self, datos_hotdog):
        """Crea un objeto HotDog a partir de datos ya convertidos"""
        try:
            nombre_hotdog = datos_hotdog["nombre"]
            
            # Buscar ingredientes con nombres exactos
            pan_nombre = datos_hotdog["pan"]
            salchicha_nombre = datos_hotdog["salchicha"]
            
            pan = self.gestor_ingredientes.buscar_por_nombre(pan_nombre)
            salchicha = self.gestor_ingredientes.buscar_por_nombre(salchicha_nombre)
            
            if not pan:
                print(f"   ⚠️  Pan no encontrado: '{pan_nombre}'")
                return None
            if not salchicha:
                print(f"   ⚠️  Salchicha no encontrada: '{salchicha_nombre}'")
                return None
            
            # Buscar toppings
            toppings = []
            for topping_nombre in datos_hotdog["toppings"]:
                topping = self.gestor_ingredientes.buscar_por_nombre(topping_nombre)
                if topping:
                    toppings.append(topping)
                else:
                    print(f"   ⚠️  Topping no encontrado: '{topping_nombre}'")
            
            # Buscar salsas
            salsas = []
            for salsa_nombre in datos_hotdog["salsas"]:
                salsa = self.gestor_ingredientes.buscar_por_nombre(salsa_nombre)
                if salsa:
                    salsas.append(salsa)
                else:
                    print(f"   ⚠️  Salsa no encontrada: '{salsa_nombre}'")
            
            # Buscar acompañante
            acompanante = None
            if datos_hotdog["acompanante"]:
                acompanante = self.gestor_ingredientes.buscar_por_nombre(datos_hotdog["acompanante"])
                if not acompanante:
                    print(f"   ⚠️  Acompañante no encontrado: '{datos_hotdog['acompanante']}'")
            
            # Crear hot dog
            hotdog = HotDog(
                id=datos_hotdog["id"],
                nombre=nombre_hotdog,
                pan=pan,
                salchicha=salchicha,
                toppings=toppings,
                salsas=salsas,
                acompanante=acompanante,
                precio_venta=datos_hotdog["precio_venta"]
            )
            
            return hotdog
            
        except Exception as e:
            print(f"   ❌ ERROR creando hot dog '{datos_hotdog.get('nombre', 'Sin nombre')}': {e}")
            return None

    def _cargar_datos_respaldo(self):
        """Carga datos de respaldo si la API falla"""
        try:
            archivo_respaldo = "datos_ejemplo.json"
            if os.path.exists(archivo_respaldo):
                with open(archivo_respaldo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                
                print("✅ Cargando datos de respaldo...")
                
                # Cargar ingredientes
                if 'ingredientes' in datos:
                    self.gestor_ingredientes.cargar_desde_lista(datos['ingredientes'])
                    print(f"✅ Cargados {len(datos['ingredientes'])} ingredientes de respaldo")
                
                # Inicializar inventario
                self._inicializar_inventario_por_defecto()
                print(f"✅ Inventario inicializado con {len(self.inventario.existencias)} items")
                
                # Cargar menú
                if 'menu' in datos:
                    for hd_data in datos['menu']:
                        try:
                            hotdog = self._crear_hotdog_desde_datos_convertidos(hd_data)
                            if hotdog:
                                self.menu.agregar_hotdog(hotdog)
                        except Exception as e:
                            print(f"Error al cargar hot dog de respaldo: {e}")
                            continue
                    print(f"✅ Cargado menú de respaldo con {len(datos['menu'])} hot dogs")
                
                print(" Datos de respaldo cargados exitosamente")
                return True
            else:
                print("❌ No se encontró archivo de respaldo")
                return False
                
        except Exception as e:
            print(f"❌ Error al cargar datos de respaldo: {e}")
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
                        if not self.gestor_ingredientes.buscar_por_id(ingrediente.id):
                            self.gestor_ingredientes.agregar_ingrediente(ingrediente)
                
                # Cargar inventario local
                if 'inventario' in datos:
                    for inv_data in datos['inventario']:
                        ingrediente = self.gestor_ingredientes.buscar_por_id(inv_data['ingrediente_id'])
                        if ingrediente:
                            self.inventario.actualizar_existencia(ingrediente, inv_data['cantidad'])
                
                # Cargar menú local
                if 'menu' in datos:
                    for hd_data in datos['menu']:
                        hotdog = HotDog.from_dict(hd_data, self.gestor_ingredientes)
                        if not self.menu.buscar_por_id(hotdog.id):
                            self.menu.agregar_hotdog(hotdog)
                
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
                'inventario': [],
                'menu': []
            }
            
            # Guardar ingredientes
            for ingrediente in self.gestor_ingredientes.ingredientes:
                datos['ingredientes'].append(ingrediente.to_dict())
            
            # Guardar inventario
            for ing_id, cantidad in self.inventario.existencias.items():
                datos['inventario'].append({
                    'ingrediente_id': ing_id,
                    'cantidad': cantidad
                })
            
            # Guardar menú
            for hotdog in self.menu.hotdogs:
                datos['menu'].append(hotdog.to_dict())
            
            with open(self.archivo_local, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            print("Datos locales guardados exitosamente")
            return True
            
        except Exception as e:
            print(f"Error al guardar datos locales: {e}")
            return False

    def mostrar_menu_principal(self):
        print("\n" + "="*50)
        print("        HOT DOG CCS  - SISTEMA PRINCIPAL")
        print("="*50)
        print("1. Gestión de Ingredientes")
        print("2. Gestión de Inventario")
        print("3. Gestión del Menú")
        print("4. Simular ventas")
        print("5. Guardar datos locales")
        print("6. Diagnóstico del sistema")
        print("7. Salir")
        print("="*50)

    def ejecutar_diagnostico(self):
        """Ejecuta un diagnóstico completo del sistema"""
        print("\n" + "="*60)
        print("           DIAGNÓSTICO DEL SISTEMA")
        print("="*60)
        
        print(f"\n ESTADO ACTUAL DEL SISTEMA:")
        print(f"   Ingredientes cargados: {len(self.gestor_ingredientes.ingredientes)}")
        print(f"   Hot dogs en menú: {len(self.menu.hotdogs)}")
        print(f"   Items en inventario: {len(self.inventario.existencias)}")
        
        print(f"\n🔍 INGREDIENTES POR CATEGORÍA:")
        for categoria in CategoriaIngrediente:
            ingredientes = self.gestor_ingredientes.listar_por_categoria(categoria)
            print(f"   {categoria.value}: {len(ingredientes)}")
            for ing in ingredientes[:3]:  # Mostrar primeros 3
                existencia = self.inventario.verificar_existencia(ing)
                print(f"      - {ing.nombre} (Existencia: {existencia})")
        
        print(f"\n HOT DOGS EN MENÚ:")
        for i, hotdog in enumerate(self.menu.hotdogs[:5]):  # Mostrar primeros 5
            disponible = "✅" if hotdog.verificar_inventario(self.inventario) else "❌"
            print(f"   {i+1}. {hotdog.nombre} - ${hotdog.precio_venta:.2f} {disponible}")
            print(f"      Pan: {hotdog.pan.nombre}")
            print(f"      Salchicha: {hotdog.salchicha.nombre}")
            print(f"      Toppings: {len(hotdog.toppings)}")
            print(f"      Salsas: {len(hotdog.salsas)}")
            if hotdog.acompanante:
                print(f"      Acompañante: {hotdog.acompanante.nombre}")
        
        if len(self.menu.hotdogs) > 5:
            print(f"   ... y {len(self.menu.hotdogs) - 5} más")
        
        print(f"\n INVENTARIO RESUMEN:")
        total_existencias = sum(self.inventario.existencias.values())
        print(f"   Total de unidades en inventario: {total_existencias}")
        
        print("\n" + "="*60)

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
                    print(f"\n--- INGREDIENTES EN {categoria.value.upper()} ---")
                    if ingredientes:
                        for ing in ingredientes:
                            existencia = self.inventario.verificar_existencia(ing)
                            print(f"  - {ing.nombre} (Tipo: {ing.tipo}, ID: {ing.id}, Costo: ${ing.costo:.2f}, Existencia: {existencia})")
                        print(f"\nTotal de {len(ingredientes)} ingredientes en {categoria.value}")
                    else:
                        print(f"No hay ingredientes en la categoría {categoria.value}")
                except (ValueError, IndexError):
                    print("Selección inválida.")
            
            elif opcion == '2':
                print("\nCategorías disponibles:")
                for i, cat in enumerate(CategoriaIngrediente, 1):
                    print(f"{i}. {cat.value}")
                try:
                    cat_idx = int(input("Seleccione categoría: ")) - 1
                    categoria = list(CategoriaIngrediente)[cat_idx]
                    
                    todos_ingredientes = self.gestor_ingredientes.listar_por_categoria(categoria)
                    if todos_ingredientes:
                        print(f"\nTodos los ingredientes en {categoria.value}:")
                        for ing in todos_ingredientes:
                            print(f"  - {ing.nombre} (Tipo: {ing.tipo})")
                    
                    tipo = input("\nIngrese el tipo a filtrar: ")
                    ingredientes = self.gestor_ingredientes.listar_por_categoria_y_tipo(categoria, tipo)
                    print(f"\nIngredientes en {categoria.value} - {tipo}:")
                    if ingredientes:
                        for ing in ingredientes:
                            existencia = self.inventario.verificar_existencia(ing)
                            print(f"  - {ing.nombre} (Costo: ${ing.costo:.2f}, Existencia: {existencia})")
                    else:
                        print(f"No hay ingredientes de tipo '{tipo}' en {categoria.value}")
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
                    
                    # Solicitar costo
                    while True:
                        try:
                            costo = float(input("Costo del ingrediente: $"))
                            if costo < 0:
                                print("El costo no puede ser negativo.")
                                continue
                            break
                        except ValueError:
                            print("Por favor ingrese un costo válido.")
                    
                    ingrediente_id = f"ing_{len(self.gestor_ingredientes.ingredientes) + 1:03d}"
                    nuevo_ingrediente = Ingrediente(
                        id=ingrediente_id,
                        nombre=nombre,
                        categoria=categoria,
                        tipo=tipo,
                        costo=costo
                    )
                    
                    self.gestor_ingredientes.agregar_ingrediente(nuevo_ingrediente)
                    
                    # Preguntar si desea agregar existencia en inventario
                    agregar_inventario = input("¿Desea agregar existencia en inventario? (s/n): ").lower()
                    if agregar_inventario == 's':
                        try:
                            cantidad = int(input("Cantidad inicial: "))
                            self.inventario.agregar_ingrediente(nuevo_ingrediente, cantidad)
                            print(f"Existencia de {cantidad} agregada para '{nombre}'")
                        except ValueError:
                            print("Cantidad inválida, no se agregó al inventario")
                    
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
                if existencia is None:
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
                        self.gestor_menu.mostrar_inventario_hotdog_detallado(hotdog)
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
        
        # === DIAGNÓSTICO TEMPORAL - EJECUTAR PRIMERO ===
        print("\n" + "="*60)
        print("          DIAGNÓSTICO TEMPORAL - ESTRUCTURA DE DATOS")
        print("="*60)
        self.diagnosticar_estructura_datos()
        print("="*60)
        input("Presiona Enter para continuar con la carga normal de datos...")
        # === FIN DIAGNÓSTICO TEMPORAL ===
        
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
                simulador.simular_dias()
            elif opcion == '5':
                self.guardar_datos_locales()
            elif opcion == '6':
                self.ejecutar_diagnostico()
            elif opcion == '7':
                print("¡Gracias por usar Hot Dog CCS! ")
                break
            else:
                print("Opción inválida. Por favor seleccione 1-7.")