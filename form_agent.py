# Global imports
from pathlib import Path
from typing import Union
import pyautogui
import ctypes
import asyncio
import pyperclip

# Relative imports
from .logger import create_logger
from .images_controller import ImagesActuator
from .scrolling_menu_agent.menu_scroller import MenuScrolling

# Logging config
if __name__ == '__main__': 
    form_ma_logger = create_logger('')
    form_ma_logger.setLevel(20)
else: 
    form_ma_logger = create_logger(__name__, without_handler = True)


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
    
    def write_on_field_by_buffer(self, content: str):
        
        pyperclip.copy(content)
        pyautogui.hotkey("ctrl", "v")

    def write_on_field_by_keyboard(self, content: str,
        inter_bet_presses: float = 0
        ):
        """ ### Escreve a string caractere por caractere verificando a cada caractere
        se o capslock está ativado. Caso esteja ativado ele será desativado

        Args:
            `content` (str): Conteúdo que vai ser escrito \n
            `inter_bet_presses` (float): Intervalo entre os \n
            elementos da cadeia de caracteres
            
        """
        
        asyncio.run(write_avoiding_capslock(content, inter_bet_presses))
        

    def press_button_by_img(self, image_name: str, num_pushes: int = 1):
        """ Pressionar algum botão do formulário usando a imagem como
        referência

        Args:
            `image_name` (str): Nome da imagem \n
            `num_pushes` (int, optional): Quantidade de pressionamentos. \n 
            Defaults to 1.
        """
        self.click_on_image(self.folder_of_form_images / image_name, 
                            qtd_click = num_pushes)
    
    def press_button_by_keyborad(self, key_name: str, num_pushes: int = 1):
        """ Pressionar algum botão do formulário usando o teclado

        Args:
            key_name (str): Nome da tecla
            `num_pushes` (int, optional): Quantidade de pressionamentos. \n 
            Defaults to 1.
        """

        pyautogui.press(key_name, num_pushes)
    


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
            self.scroller = MenuScrolling(self.folder_of_form_images)
        else:
            self.scroller = MenuScrolling(scrolling_img_folder_path)
        

    def scroll_to_field(self, target_img: Union[str, Path], step_direction: str = "down", press_tab: bool = False, 
        steps:int = 30, clicks_on_target: int = 1, wait_before_searching_target: int = 0):
        """ ### Rolar até o campo

        Procura a imagem de ancora do campo, caso não encontre ele vai \n
        scrollar até encontrar essa imagem

        Args: \n
            `target_img` (str, Path): Para a entrada do tipo `str` você coloca o nome \n
             do arquivo da imagem que está pasta do menu de scrolling. Se for passado o `Path` 
             você colocar o caminho da imagem que você quer focar\n
            `step_direction` (str, optional): direção para percorrer no \n
            no menu scrolling. Defaults to `down`. \n
            `steps` (int, optional): quantidade de passos que ele deve dar. Defaults to 30. \n
            `clicks_on_target` (int, optional): Quantidade de click que deve \n
            dar na imagem ancora do campo quando encontrada. Defaults to 1.
        """

        if isinstance(target_img, str):
            target_path = self.folder_of_form_images / target_img
        elif isinstance(target_img, Path):
            target_path = target_img
        else:
            form_ma_logger.error("Tipo de dado da |target_img| não é válido")
            raise TypeError("|target_img| deve |str| ou |Path|")

        self.scroller.set_target(target_path)

        self.scroller.clicks_on_target = clicks_on_target
        self.scroller.search(step_direction, steps, 
                                   wait_before_searching_target= wait_before_searching_target)
        
        if press_tab:
            pyautogui.press("tab")


async def write_avoiding_capslock(text: str, interval: float = 0):
    """Escreve a string caractere por caractere
    verificando a cada caractere se o capslock está
    ativado. Caso esteja ativado ele será desativado

    Args:
        text (str): Texto para ser escrito
        interval (float, optional): Intervalo de tempo entre as letras
    """

    for letter in text:
        if is_capslock_on(): pyautogui.press('capslock')
        await asyncio.sleep(interval) 
        pyautogui.typewrite(letter)


def is_capslock_on()-> int:
    """### Indica qual é o estado atual

    Returns:
        int: 1 quer dizer que o caps lock está ativo
        int: 0 quer dizer que o caps lock está desativado
    """
    hllDll: ctypes.WinDLL = ctypes.WinDLL("User32.dll")
    VIRTUAL_KEY_FOR_CAPS_LOCK = 0x14
    return hllDll.GetKeyState(VIRTUAL_KEY_FOR_CAPS_LOCK)



if __name__ == "__main__":
    pass



        
