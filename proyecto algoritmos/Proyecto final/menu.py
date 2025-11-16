from typing import List, Optional
from hotdogs import HotDog
from ingredientes import Ingrediente

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