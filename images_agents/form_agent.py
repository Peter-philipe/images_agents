# Global imports
from pathlib import Path
import sys
from typing import Union
import pyautogui

# Relative imports
from .logger import create_logger
from .images_controller import ImagesActuator
from .scrolling_menu_agent.menu_scroller import MenuScrolling

# Logging config
if __name__ == "__main__": form_ma_logger = create_logger('')
else: form_ma_logger = create_logger(__name__)


class FormManager(ImagesActuator):

    def __init__(self, form_img_folder_path: Union[str, Path]) -> None:
        """ Classe para fazer o preenchimento de formulário

        Args:
            `form_img_folder_path` (str): Nome da pasta onde estão as imagens dos campos \n
            Defaults to "prod". \n
        """

        if isinstance(form_img_folder_path, str): self.folder_of_form_images = Path(form_img_folder_path)
        else: self.folder_of_form_images = form_img_folder_path
        
        super().__init__(raise_approach = True)
    
    def focus_on_field(self, name_of_image:str, press_tab: bool = False, 
        x_pos: int = 0, y_pos: int = 0):
        """ ### Focar no campo
        Clica na imagem usada como ancora para deixar no ponto de usar o campo.\n
        Caso precise o TAB pode ser colocado no fluxo \n
        Args:
            `name_of_image` (str): Nome da imagem com a extensão
            `press_tab` (bool): Pressionar TAB caso precise 
        """

        empresa_field = self.folder_of_form_images / name_of_image
        self.click_on_image(empresa_field, offset_pos_x = x_pos, offset_pos_y = y_pos)

        if press_tab:
            pyautogui.press("tab")
    
    def write_on_field(self, content: str, 
        inter_bet_presses: float = 0):
        """ ### Escrever no campo do formulário

        Args:
            `content` (str): Conteúdo que vai ser escrito \n
            `inter_bet_presses` (float): Intervalo entre os \n
            elementos da cadeia de caracteres
        """
        pyautogui.write(content, interval = inter_bet_presses)

    def press_button(self, image_name: str, num_pushes: int = 1):
        """ Pressionar algum botão do formulário

        Args:
            `image_name` (str): Nome da imagem \n
            `num_pushes` (int, optional): Quantidade de pressionamentos. \n 
            Defaults to 1.
        """
        self.click_on_image(self.folder_of_form_images / image_name, 
                            qtd_click = num_pushes)


class FormScroller(FormManager): 

    def __init__(self, form_img_folder_path: Union[str, Path], 
                 scrolling_img_folder_path: Union[str, Path] = None) -> None:
        """ Classe para fazer o preenchimento de formulário

        Args:
            `form_img_folder_path` (str): Nome da pasta onde estão as imagens dos campos \n
            `scrolling_img_folder_path`(str, optional): nome da pasta onde estão as imagens dos elementos \n
            do menu de scrolling que o formulário faz parte. Defaults to None
        """
        super().__init__(form_img_folder_path)

        if scrolling_img_folder_path is None:
            self.form_scrolling = MenuScrolling(self.folder_of_form_images)
        else:
            self.form_scrolling = MenuScrolling(scrolling_img_folder_path)
        
        self.form_scrolling.load_images()

    def scroll_to_field(self, target_img_name: str, step_direction: str = "down", 
        steps:int = 30, clicks_on_target: int = 1):
        """ ### Scroll_to_field

        Procura a imagem de ancora do campo, caso não encontre ele vai \n
        scrollar até encontrar essa imagem

        Args: \n
            `target_img_name` (str): nome do arquivo da imagem \n
            `step_direction` (str, optional): direção para percorrer no \n
            no menu scrolling. Defaults to `down`. \n
            `steps` (int, optional): quantidade de passos que ele deve dar. Defaults to 30. \n
            `clicks_on_target` (int, optional): Quantidade de click que deve \n
            dar na imagem ancora do campo quando encontrada. Defaults to 1.
        """

        target_path = self.folder_of_form_images / target_img_name
        self.form_scrolling.set_target(target_path)

        self.form_scrolling.clicks_on_target = clicks_on_target
        self.form_scrolling.search(step_direction, steps)
        pyautogui.press("tab")

    




if __name__ == "__main__":
    pass



        
