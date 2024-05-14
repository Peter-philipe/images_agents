from pathlib import Path
import sys
import logging
import subprocess

num_dir_to_src = 2
src_folder = Path(__file__)
for i in range(num_dir_to_src): src_folder = src_folder.parent

if src_folder not in sys.path: sys.path.append(str(src_folder))
if Path.cwd() not in sys.path: sys.path.append(Path.cwd().__str__())

from logger import create_logger
from controlador_imagem import ImagesActuator

log_file = Path(__file__).parent / "ted_controller_logs.log"
if __name__ == "__main__": ted_controller_logger = create_logger("", log_file)
else: ted_controller_logger = create_logger(__name__)

class TedActuator(ImagesActuator):
    
    def __init__(self, duration_move_pointer: float = 0.25, raise_approach: bool = False) -> None:
        self.ted_pid: subprocess.Popen
        super().__init__(duration_move_pointer, raise_approach)

    

    def open_app(self):
        ted_controller_logger.info("Abrindo Ted")
        ted_exe_path = Path(r"C:\SefaNet\ted.exe")
        self.ted_pid = subprocess.Popen(ted_exe_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
    def go_to_testar_tab(self):
        ted_controller_logger.info("Indo para aba de |testar|")
        
        img_tab_to_activate = (Path(__file__).parent / "testar_tab-to_activate.png")
        tab_to_activate_track = self.click_on_image(img_tab_to_activate, timeout = 15)

        if tab_to_activate_track == 0:
            ted_controller_logger.info("Tab |testar| está disponível") 
            return 0
        
        ted_controller_logger.info("Tab para opção de |testar| não está disponível")
        ted_controller_logger.info("Verificando se já está na Tab de |testar|")

        img_tab_activated = (Path(__file__).parent / "testar_tab-activated.png")
        tab_activated_track = self.find_image(img_tab_activated, timeout = 15)

        if tab_activated_track == 0: 
            ted_controller_logger.info("Já está na Tab de |testar|")
            return 1
        else:
            ted_controller_logger.info("Não da para saber está no Tab |testar|")
            return -1
        
    def open_scroll_menu(self):

        img_scroll_opener = (Path(__file__).parent / "scroll_menu_opener.png")
        scroll_opene_track = self.click_on_image(img_scroll_opener, timeout = 15)

        if scroll_opene_track == 0:
            ted_controller_logger.info("Menu de scrolling aberto") 
            return 0
        else:
            ted_controller_logger.error("Não foi possível abrir o menu scrolling") 
            return -1

    def close_ted(self):
        ted_controller_logger.info("Fechando janela")
        self.ted_pid.terminate()
    
        
if __name__ == "__main__":

    ted_controller_logger.setLevel(logging.DEBUG)
    
    ted_app = TedActuator()
    ted_app.open_app()
    ted_app.go_to_testar_tab()
    ted_app.open_scroll_menu()
    #será mesmo que eu preciso de um novo teclado()(((())))
    ted_app.close_ted()

    

    print("fim")