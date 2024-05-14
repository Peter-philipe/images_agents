
# Global imports
import time
import pyautogui
from pathlib import Path
from typing import Union,Generator, Tuple, Iterable, List
import logging
import cv2
import numpy as np
import asyncio
from concurrent.futures import Future, ProcessPoolExecutor
from pyscreeze import Box
from cv2.typing import MatLike

# Relative imports
from .logger import create_logger

# Logging config
if __name__ == '__main__': 
    img_aux_logger = create_logger('')
    img_aux_logger.setLevel(20)
else: 
    img_aux_logger = create_logger(__name__, without_handler = True)

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
        button: str = "left", qtd_click: str = 1, timeout: Union[int, float] = 15,
        confidence: float = 0.9):
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
        
        asyncio.run(self._avoid_mouse_interference())

        timer = Timer(timeout)
        while not timer.is_expired():

            try:
                img_data = pyautogui.locateOnScreen(self._decode_image_path(img_path), confidence= confidence)
            except Exception as error:
                if "screen grab failed" in error.args[0]:
                    img_aux_logger.error("Erro de screen grab. Fazendo uma segunda tentativa")
                    return self.click_on_image(img_path, offset_pos_x, offset_pos_y, button, qtd_click, timeout, confidence)

                img_aux_logger.info(f"Erro ao procurar a imagem")
                if self.raise_approach:
                    raise error
                else:
                    img_aux_logger.debug(f"Informações sobre o erro: {error}")
                    return -2
            

            if img_data != None:

                img_pos_x, img_pos_y = pyautogui.center(img_data)

                self.click_in_coordenates(left=img_pos_x,
                                          hight=img_pos_y,
                                          offset_pos_x=offset_pos_x,
                                          offset_pos_y=offset_pos_y,
                                          button=button,
                                          qtd_click=qtd_click)
                
                img_aux_logger.debug("Clique com sucesso")
                return 0
            
        if self.raise_approach:
            raise TimeoutError(f"O tempo para encontrar a imagem espirou: {img_path.name}")
        else:
            img_aux_logger.debug(f"O tempo para encontrar a imagem espirou: {img_path.name}")
            return -1
        

    def find_image(self, img_path: Union[str, Path], 
        timeout: Union[int, float] = 20, is_async_execution: bool = False, 
        return_box: bool = False):
        """ ### Encontrar imagem

        #### Args:
            `image_path`: string do caminho da imagem \n
            `timeout`: tempo para esperar encontrar a imagem \n
        """

        if isinstance(img_path, str): img_path = Path(img_path)
        
        if not is_async_execution:
            asyncio.run(self._avoid_mouse_interference())
        
        img_aux_logger.debug(f"Procurando pela imagem: {img_path.name}")
        
        timer = Timer(timeout)
        while not timer.is_expired():
            try:
                
                img_data = pyautogui.locateOnScreen(self._decode_image_path(img_path), grayscale=True, confidence=0.95)
                
            except Exception as error:
                img_aux_logger.error(f"Erro ao procurar a imagem")
                if self.raise_approach:
                    raise error
                else:
                    img_aux_logger.debug(f"Informações sobre o erro: {error}")
                    return -2
            
            if (img_data is not None) and (not return_box): 
                img_aux_logger.debug(f"Imagem encontrada: {img_path.name}")
                return 0
            
            if (img_data is not None) and (return_box): 
                img_aux_logger.debug(f"Imagem encontrada: {img_path.name}")
                return img_data
                        
        if self.raise_approach:
            raise TimeoutError(f"O tempo para encontrar a imagem espirou: {img_path.name}")
        else:
            img_aux_logger.debug(f"O tempo para encontrar a imagem espirou: {img_path.name}")
            return -1
    
    def find_all_image_instances(self, img_path: Union[str, Path], 
        timeout: Union[int, float] = 20)-> Union[Tuple[Box], int]:
        """ ### Procurar por vários exemplares de uma mesma imagem

        #### Args:
            `image_path`: string do caminho da imagem \n
            `timeout`: tempo para esperar encontrar a imagem \n
        """

        if isinstance(img_path, str): img_path = Path(img_path)
        
        asyncio.run(self._avoid_mouse_interference())
        
        img_aux_logger.debug(f"Procurando pela imagem: {img_path.name}")
        
        timer = Timer(timeout)
        while not timer.is_expired():

            try:
                
                images_gen: Union[Generator, None] = pyautogui.locateAllOnScreen(self._decode_image_path(img_path), grayscale=True, confidence=0.95)
                
            except Exception as error:
                img_aux_logger.error(f"Erro ao procurar a imagem")
                if self.raise_approach:
                    raise error
                else:
                    img_aux_logger.debug(f"Informações sobre o erro: {error}")
                    return -2
                
            images: Tuple[Box] = tuple(images_gen)

            if (images_gen is not None) and (len(images) > 0): 
                img_aux_logger.debug("Imagens encontradas")

                return images
            
            if ((images_gen is not None) and (len(images) == 0) or images_gen is None): 
                img_aux_logger.debug("Nenhuma imagem foi encontrada")
                return -1
            
            
        if self.raise_approach:
            raise TimeoutError(f"O tempo para encontrar a imagem espirou: {img_path.name}")
        else:
            img_aux_logger.debug(f"O tempo para encontrar a imagem espirou: {img_path.name}")
            return -1
    
    def find_multi_imagens(self, images_path: Iterable[Union[Path, str]], 
        timeout: Union[int, float] = 20)-> List[Box]:

        if isinstance(images_path[0], str): 
            images_path = tuple(map(lambda img_path: Path(img_path), images_path))

        result = asyncio.run(self._find_multi_images_async(images_path, timeout))

        return result
    
    async def _find_multi_images_async(self, images_path: Iterable[Union[Path, str]], 
        timeout: Union[int, float] = 20):

        await self._avoid_mouse_interference()
        
        temp_results: List[Future] = []
        
        with ProcessPoolExecutor() as pool:
            event_loop = asyncio.get_event_loop()
            for img_path in images_path:

                survey_result = event_loop.run_in_executor(pool, 
                                                           self.find_image, 
                                                           img_path, 
                                                           timeout, 
                                                           True,
                                                           True)
                temp_results.append(survey_result)

        results = []
        for survey in temp_results:
            res = await asyncio.wrap_future(survey)
            results.append(res)

        return results

    def _decode_image_path(self, image_path: Path) -> MatLike:
        """
        If there is any special character in the path it need to be decoded.
        so this function do it \n
        Args:
            image_path (Path): path with some special character
        
        Discussion about it:
        https://stackoverflow.com/questions/43185605/how-do-i-read-an-image-from-a-path-with-unicode-characters
        """
        
        try:
            stream = image_path.open(mode = "rb")
        except Exception as error:
            img_aux_logger.error("Erro ao ler arquivo da imagem")
            img_aux_logger.error(f"Detalhes do erro: {error}")
            
            return error
        bytes = bytearray(stream.read())
        stream.close()
        numpyarray = np.asarray(bytes, dtype=np.uint8)
        
        image = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
        if image.ndim > 2:
            # Tirar o canal alpha e deixar só RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
 
        
        return image

    def click_on_box(self, box: Box, button: str = "left", 
        qtd_click: int = 1, offset_pos_x: int = 0, offset_pos_y: int = 0):

        self.click_in_coordenates(left=box.left,
                                  hight=box.top,
                                   button=button,
                                   qtd_click=qtd_click,
                                   offset_pos_x=offset_pos_x,
                                   offset_pos_y=offset_pos_y)

    def click_in_coordenates(self, left: int, hight: int, button: str = "left", 
        qtd_click: int = 1, offset_pos_x: int = 0, offset_pos_y: int = 0):
        """ Vai até as coordenadas indicadas e clica nessa posição a qunatidade de vezes que foi requerido

        Args:
            left (int): _description_
            hight (int): _description_
            button (str, optional): _description_. Defaults to "left".
            qtd_click (int, optional): _description_. Defaults to 1.
            offset_pos_x (int, optional): _description_. Defaults to 0.
            offset_pos_y (int, optional): _description_. Defaults to 0.
        """

        
        pyautogui.moveTo(left + offset_pos_x, 
                         hight + offset_pos_y, 
                         self.duration_move_pointer
                         )
        
        pyautogui.click(button=button, clicks=qtd_click)

        pass

    async def _avoid_mouse_interference(self):
        """Para evitar que o mouse fique em cima de alguma imagem.\n
           Move o ponteiro para parte inferior direita da tela
        """
        await asyncio.sleep(1)
        
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
        """Temporizador

        Args:
            duration (float, optional): Tempo para ser cronometrado. Defaults to 10.0.
        """
        self.duration = duration
        self.start = time.perf_counter()

    def reset(self):
        """Reiniciar a contagem de tempo
        """
        self.start = time.perf_counter()
        

    def explode(self):
        """Força que o tempo expire
        """
        self.duration = 0


    def increment(self, increment:float = 0):

        """Aumenta a quantidade de tempo do temporizador
        Args:
            increment (int, optional): Valor em segundos para adicionar no
            temporizador. Defaults to 0.
        """

        if not isinstance(increment, float):
            raise TypeError("O valor de incremento deve ser um número flutuando (float)")

        self.duration += increment
        

    def is_expired(self):
        """Verifica se o tempo para ser cronometrado
        já expirou

        Returns:
            bool: Caso verdadeiro o tempo expirou
        """
        if self.duration == -1:
            return True

        return (self.at() > self.duration)
    
    def at(self):
        """Quanto tempo já se passou desde de o
        início da cronometragem

        Returns:
            float: tempo decorrido
        """
        return time.perf_counter() - self.start


if __name__ == '__main__':
    
    img_aux_logger.setLevel(logging.DEBUG)
    clicador = ImagesActuator()

    clicador.find_image(r"E:\RPA\Homologation\finder_by_guided_scrolling\elements\custom_processments\top_b-1.png")