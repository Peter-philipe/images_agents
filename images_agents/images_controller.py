
# Global imports
import time
import pyautogui
from pathlib import Path
from typing import Union
import logging
import cv2
import numpy as np
from cv2.typing import MatLike

# Relative imports
from .logger import create_logger

# Logging config
if __name__ == "__main__": img_aux_logger = create_logger("")
else: img_aux_logger = create_logger(__name__)

# teste
class ImagesActuator:
    """
    Classe que procura auxiliar a busca por elementos renderizados na tela
    
    """
    def __init__(self, duration_move_pointer: float = 0.25, raise_approach: bool = False) -> None:
        """ ### Controlador de ações com as imagens

        Args:
            `duration_move_pointer` (float, optional): tempo do mouse ir para posição de \n
            descanço. Defaults to 0.25. \n
            `raise_approach` (bool, optional): Decide se quando tiver erro ele \n
            retorna um código numérico ou uma Excpetion. Defaults to False. \n
        """
        self.duration_move_pointer = duration_move_pointer
        self.raise_approach = raise_approach
       

    def click_on_image(self, 
        img_path: Union[str, Path], offset_pos_x: int = 0, offset_pos_y: int = 0, 
        button: str = "left", qtd_click: str = 1, timeout: Union[int, float] = 15):
        '''
        ### Clicar na imagem
        O clique ocorre no centro da imagem, mas pode ser \n
        alterado para alterado usando os parâmetros: \n
        `offset_pos_x` e `offset_pos_y`

        #### Parâmetros
        `image_path`: string do caminho da imagem \n
        `offset_pos_x`: adicionar distancia horizontalmente ao clicar na imagem \n
        `offset_pos_y`: adicionar distancia verticalmente ao clicar na imagem \n
        `qtd_click`: quantidades de cliques \n
        `timeout`: tempo para esperar encontrar a imagem \n
        '''
        
        if isinstance(img_path, str): img_path = Path(img_path)
            
        img_aux_logger.debug(f"Clicando na imagem: {img_path.name}")
        
        self._avoid_mouse_interference()

        timer = Timer(timeout)
        while timer.not_expired:

            try:
                img_data = pyautogui.locateOnScreen(self._decode_image_path(img_path), confidence=0.9)
            except Exception as error:
                img_aux_logger.info(f"Erro ao procurar a imagem")
                if self.raise_approach:
                    raise error
                else:
                    img_aux_logger.debug(f"Informações sobre o erro: {error}")
                    return -2
            

            if img_data != None:

                img_pos_x, img_pos_y = pyautogui.center(img_data)
                pyautogui.moveTo(img_pos_x + offset_pos_x, 
                                 img_pos_y + offset_pos_y, 
                                 self.duration_move_pointer
                                 )
                time.sleep(1)
                pyautogui.click(button=button, clicks=qtd_click)
                
                img_aux_logger.debug("Clique com sucesso")
                return 0
            
        if self.raise_approach:
            raise TimeoutError(f"O tempo para encontrar a imagem espirou: {img_path.name}")
        else:
            img_aux_logger.debug(f"O tempo para encontrar a imagem espirou: {img_path.name}")
            return -1


    def find_image(self, img_path: Union[str, Path], 
        timeout: Union[int, float] = 20):
        """ ### Encontrar imagem

        #### Args:
            `image_path`: string do caminho da imagem \n
            `timeout`: tempo para esperar encontrar a imagem \n
        """

        if isinstance(img_path, str): img_path = Path(img_path)
        
        self._avoid_mouse_interference()
        
        img_aux_logger.debug(f"Procurando pela imagem: {img_path.name}")
        
        timer = Timer(timeout)
        while timer.not_expired:
            try:
                
                img_data = pyautogui.locateOnScreen(self._decode_image_path(img_path), grayscale=True, confidence=0.95)
                
            except Exception as error:
                img_aux_logger.error(f"Erro ao procurar a imagem")
                if self.raise_approach:
                    raise error
                else:
                    img_aux_logger.debug(f"Informações sobre o erro: {error}")
                    return -2
            
            if img_data is not None: 
                img_aux_logger.debug("Imagem encontrada")
                return 0
                        
            
        if self.raise_approach:
            raise TimeoutError(f"O tempo para encontrar a imagem espirou: {img_path.name}")
        else:
            img_aux_logger.debug(f"O tempo para encontrar a imagem espirou: {img_path.name}")
            return -1
    
    def find_all_images_instances(self, img_path: Union[str, Path], 
        timeout: Union[int, float] = 20):
        """ ### Procurar por vários exemplares de uma imagem

        #### Args:
            `image_path`: string do caminho da imagem \n
            `timeout`: tempo para esperar encontrar a imagem \n
        """

        if isinstance(img_path, str): img_path = Path(img_path)
        
        self._avoid_mouse_interference()
        
        img_aux_logger.debug(f"Procurando pela imagem: {img_path.name}")
        
        timer = Timer(timeout)
        while timer.not_expired:
            try:
                
                img_data = pyautogui.locateAllOnScreen(self._decode_image_path(img_path), grayscale=True, confidence=0.95)
                
            except Exception as error:
                img_aux_logger.error(f"Erro ao procurar a imagem")
                if self.raise_approach:
                    raise error
                else:
                    img_aux_logger.debug(f"Informações sobre o erro: {error}")
                    return -2
            
            if img_data is not None: 
                img_aux_logger.debug("Imagem encontrada")
                return img_data
             
            
        if self.raise_approach:
            raise TimeoutError(f"O tempo para encontrar a imagem espirou: {img_path.name}")
        else:
            img_aux_logger.debug(f"O tempo para encontrar a imagem espirou: {img_path.name}")
            return -1


    def _decode_image_path(self, image_path: Path) -> MatLike:
        """
        If there is any special character in the path it need to be decoded.
        so this function do it \n
        Args:
            image_path (Path): path with some special character
        
        Discussion about it:
        https://stackoverflow.com/questions/43185605/how-do-i-read-an-image-from-a-path-with-unicode-characters
        """
        
        stream = image_path.open(mode = "rb")
        bytes = bytearray(stream.read())
        stream.close()
        numpyarray = np.asarray(bytes, dtype=np.uint8)
        
        image = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
        if image.ndim > 2:
            # Tirar o canal alpha e deixar só RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
 
        
        return image


    def _avoid_mouse_interference(self):
        """Para evitar que o mouse fique em cima de alguma imagem.\n
           Move o ponteiro para parte inferior direita da tela
        """
        time.sleep(1)
        
        screen_size_x, screen_size_y = pyautogui.size()
        
        #O valor 80 é para que o mouse fique no canto da janela e não suma na tela
        standby_x_pos = screen_size_x - 80
        standby_y_pos = screen_size_y - 80
        
        #Função que move o mouse
        pyautogui.moveTo(standby_x_pos, 
                         standby_y_pos, 
                         self.duration_move_pointer)


class Timer:
    def __init__(self, duration: float = 10.0):
        self.duration = duration
        self.start = time.perf_counter()

    def reset(self):
        self.start = time.perf_counter()
        # print("The timer has been reset. Self.start: " + str(self.start))

    def explode(self):
        self.duration = 0
        # print("The timer has been force-expired.")

    def increment(self, increment=0):
        self.duration += increment
        # print("The timer has been incremented by " + str(increment) + " seconds")

    @property
    def not_expired(self):
        # duration == -1 means dev wants a infinite loop/Timer
        if self.duration == -1:
            return True
        return False if time.perf_counter() - self.start > self.duration else True

    @property
    def expired(self):
        return not self.not_expired

    @property
    def at(self):
        # print("The timer is running. Self.at: " + str(time.perf_counter() - self.start))
        return time.perf_counter() - self.start


if __name__ == '__main__':
    
    img_aux_logger.setLevel(logging.DEBUG)
    clicador = ImagesActuator()

    clicador.find_image(r"E:\RPA\Homologation\finder_by_guided_scrolling\elements\custom_processments\top_b-1.png")