# Global imports
from pathlib import Path
from pyautogui import press
from typing import Union, List
from time import sleep


# Add source lib folder to path


# Relative imports
from ..logger import create_logger
from .auxiliaries import MenuImagesContainer, StepsCounter
from ..images_controller import ImagesActuator

# Logging config
if __name__ == "__main__": menu_s_logger = create_logger("", "menu_scroll_tracking.log")
else: menu_s_logger = create_logger(__name__)



# pattern for name images when they are in menu_images_folder: {kind_of_element}-{version_identifier}
class MenuScrolling:

    def __init__(self, menu_images_folder: Union[Path,str], duration_move_pointer: float = 0.25):
        """ ### MenuScrolling

        Args:
            `menu_images_folder` (Union[Path,str]): path to folder where we can find the images \n
            of menu scroll with names in the pattern. \n
            `duration_move_pointer` (float, optional): time to move mouse. Defaults to 0.25.
        """
        
        if isinstance(menu_images_folder, str): 
            self.menu_images_folder = Path(menu_images_folder)
        else: self.menu_images_folder = menu_images_folder

        self.image_container = MenuImagesContainer()
        
        self.img_actuator = ImagesActuator(duration_move_pointer)
        self.step_timeout = 2
        self.target_timeout = 2
        self.locate_timeout = 1
        self.clicks_on_target = 2
        self.clicks_to_focus = 1
        self.wait_before_clicking_on_target = 0
        self.stepcounter = StepsCounter()

    def load_images(self, target_image: Union[Path, str, List[Path]] = None):
        """ ### Load the images in the folder

        Identify each kind of image. \n
        Args:
            `target_image` (Union[Path, str, List[Path]], optional): Path to the target image. \n
            If not specified assume that target_image is in menu_images_folder.Defaults to None.
        """

        self._path_existence(self.menu_images_folder)
        
        self.set_target(target_image)
        menu_s_logger.debug(f"Carregando imagens do menu {self.menu_images_folder.name}")
        self._load_menu_elements()
     
    def set_target(self, target_image: Union[Path, str, List[Path]]):
        """ ### Change target image
        With this function you can modify the target_image even when the images have already been loaded. \n
        Args:
            `target_image` (Union[Path, str, List[Path]], optional): Path to the target image. \n
            If not specified assume that target_image is in menu_images_folder. Defaults to None.
        """

        if target_image is None: return 0

        if isinstance(target_image, str):
            target_image = Path(target_image)

        if isinstance(target_image, Path):
            
            self._path_existence(target_image)
            self.image_container.target = [target_image]
        
        if isinstance(target_image, list):

            for target_version in target_image:
                self._path_existence(target_version)
            
            self.image_container.target = target_image      
        
    def search_by_focus(self, step_direction: str, clicks_to_focus: int = 0, 
        wait_before_clicking_on_target: int = 0, steps: int = 3, kind_of_step: str = "mouse"):
        """### Focus in a specific part the menu and then search
        When the focus area is reached the function start the search in \n
        the chosen direction. If the target isn't found until reach one limit \n
        it goes back to the focus area and start the search in the other direction\n
        What is focus area: most probably area where the target is. \n
        Args:
            `step_direction` (str): `up` and `down` are the options \n
            `steps` (int, optional): number of clicks in the chosen directions. Defaults to 3. \n
            `clicks_to_focus` (int, optional): clicks to find the focus area in the chosen direction
        """

        menu_s_logger.info("Iniciando busca por foco")
        
        target_tracking, border_tracking = self._take_a_step(step_direction, clicks_to_focus, kind_of_step, False)
        self.stepcounter.refresh()
        
        sleep(wait_before_clicking_on_target)
        if (target_tracking != 0 and border_tracking != 0):

            menu_s_logger.info("Alvo não está no foco. Iniciando busca na direção escolhida")
            target_tracking, border_tracking = self.search(step_direction, steps, kind_of_step)
            
        if (target_tracking != 0 and border_tracking == 0):

            menu_s_logger.info("Nada encontrado. Voltando ao foco e inicial busca na direção contrária")
            self._take_a_step(self.flip_direction(step_direction), self.stepcounter.steps(step_direction), kind_of_step)

            target_tracking, border_tracking = self.search(self.flip_direction(step_direction), steps)
        
        if target_tracking != 0:
            menu_s_logger.info("All menu has been scrolled and target wasn't found")
        else:
            menu_s_logger.info("Alvo encontrado")
    
    
    def flip_direction(self, step_direction: str) -> str:
        """### invert direction
        Args:
            `step_direction` (str): `up` and `down` are the options \n
        Returns:
            `str`: the inverted direction
        """
        if step_direction == "up":
            return "down"
        if step_direction == "down":
            return "up"
        
    def search(self, step_direction: str, steps: int = 3, kind_of_step: str = "mouse") -> tuple:
        """ ### Search in a chosen direction

        Args:
            step_direction (str): `up` and `down` are the options
            steps (int, optional): number of clicks in the chosen directions. Defaults to 3.
            `kind_of_step` (str, optional): with `mouse` it'll click using the left trigger \n
             in the step image and with `keyboard` it'll press arrow of the direction. \n
             Defaults to "mouse". \n

        Returns:
            tuple: tuple that indicates if target and border have been reached
        """
        
        target_tracking = -1
        border_tracking = -1

        #primeira varificação
        target_tracking = self._click_on_target(self.image_container.target)
        if target_tracking == 0:
            return target_tracking, border_tracking
        
        # ~(AvB) == (~A)^(~B)
        while not (target_tracking == 0 or border_tracking == 0):
            target_tracking, border_tracking = self._take_a_step(step_direction, steps, kind_of_step)
        
        return target_tracking, border_tracking
         
    def _take_a_step(self, step_direction: str, steps: int = 3, kind_of_step: str = "mouse",
        verify_target: bool = True):
        """### Take steps in the chosen direction

        Args:
            `step_direction` (str): `up` and `down` are the options \n
            `steps` (int, optional): number of clicks in the chosen directions. Defaults to 3 \n
            `kind_of_step` (str, optional): with `mouse` it'll click using the left trigger \n
             in the step image and with `keyboard` it'll press arrow of the direction. \n
             Defaults to "mouse". \n
        """
        
        if step_direction == "up":
            
            if kind_of_step == "mouse":
                self._step_by_mouse(step_direction, self.image_container.upward_step, steps)
            if kind_of_step == "keyboard": 
                self._step_by_keyborad(step_direction, steps)

            self.stepcounter.count(step_direction, steps)

            if verify_target: target_tracking = self._click_on_target(self.image_container.target)
            else: target_tracking = -1

            border_tracking = self._border_to_reach("Upper limit", self.image_container.top_border)
            
            return (target_tracking, border_tracking)
            
        elif step_direction == "down":

            if kind_of_step == "mouse":
                self._step_by_mouse(step_direction, self.image_container.downward_step, steps)
            if kind_of_step == "keyboard": 
                self._step_by_keyborad(step_direction, steps)
            
            self.stepcounter.count(step_direction, steps)

            if verify_target: target_tracking = self._click_on_target(self.image_container.target)
            else: target_tracking = -1

            border_tracking = self._border_to_reach("Bottom limit", self.image_container.bottom_border)
            
            return (target_tracking, border_tracking)
        
        else:
            menu_s_logger.error(f"Valor informado: <<{step_direction}>> não é um direção válida")
            raise ValueError()
    
    def _step_by_mouse(self, step_direction: str, list_of_images: list, steps: int = 3):
        
        for try_counter, image in enumerate(list_of_images, 1):
            
            up_step_image_path = self._path_to_oparate(image)
            tracking = self.img_actuator.click_on_image(up_step_image_path.__str__(), 
                                                        timeout = self.step_timeout,
                                                        qtd_click = steps)
            
            if tracking < 0:
                if try_counter == len(list_of_images):
                    menu_s_logger.error(f"Todas as tentativas para encontrar as imagens do tipo |{step_direction}| foram esgotadas")
                    raise StepError(f"Erro no passo |{step_direction}|")
                else:
                    menu_s_logger.debug(f"Tentado outra versão do tipo |{step_direction}|")
            else:
                menu_s_logger.debug(f"|{step_direction}| foi encontrado")
                return tracking
    
    def _step_by_keyborad(self, step_direction: str, steps: int = 3):

        if step_direction == "up": press(step_direction, steps)
           
        if step_direction == "down": press(step_direction, steps)
        
        menu_s_logger.debug(f"{steps} passos pelo teclado")
            
    def _click_on_target(self, list_of_images: list):
        
        for try_counter, image in enumerate(list_of_images, 1):
            
            up_step_image_path = self._path_to_oparate(image)
            tracking = self.img_actuator.click_on_image(up_step_image_path.__str__(), 
                                                       timeout = self.target_timeout, 
                                                       qtd_click = self.clicks_on_target)
            
            if tracking < 0:
                if try_counter == len(list_of_images):
                    menu_s_logger.debug(f"Todas as tentativas para encontrar as imagens do tipo Target foram esgotadas")
                    return tracking
                else:
                    menu_s_logger.debug(f"Tentado outra versão do tipo Target")
            else:
                menu_s_logger.debug(f"Target foi encontrado")
                return tracking
    
    
    def _border_to_reach(self, step_direction: str, list_of_images: list):
        
        for try_counter, image in enumerate(list_of_images, 1):
            
            up_step_image_path = self._path_to_oparate(image)
            tracking = self.img_actuator.find_image(up_step_image_path.__str__(),
                                                          timeout=self.locate_timeout)
            
            if tracking < 0:
                if try_counter == len(list_of_images):
                    menu_s_logger.debug(f"Todas as tentativas para encontrar as imagens do tipo |{step_direction}| foram esgotadas")
                    return tracking
                else:
                    menu_s_logger.debug(f"Tentado outra versão do tipo |{step_direction}|")
            else:
                menu_s_logger.debug(f"|{step_direction}| foi encontrado")
                return tracking
        
    def _path_to_oparate(self, image: Union[str, Path]):

        if isinstance(image, str):
            return self.menu_images_folder / image
        if isinstance(image, Path):
            return image
        raise ValueError(f"Objeto {image} não corresponte a str ou Path")

    def _path_existence(self, path: Path):
        
        if not path.exists():
            menu_s_logger.error(f"Caminho para {path.__str__()} não existe")
            raise FileNotFoundError()
        
    def _load_menu_elements(self):

        for file in self.menu_images_folder.iterdir():

            if "top_b" in file.name: 
                self.image_container.top_border.append(file.name)
                
            if "bottom_b" in file.name:
                self.image_container.bottom_border.append(file.name)
            
            if ("target" in file.name) and (len(self.image_container.target) == 0):
                self.image_container.target.append(file.name)
            
            if "upward_step" in file.name:
                self.image_container.upward_step.append(file.name)
            
            if "downward_step" in file.name:
                self.image_container.downward_step.append(file.name)

        self._verify_img_container()

    def _verify_img_container(self):
            
            if len(self.image_container.top_border) == 0:
                menu_s_logger.error("Não foi encontrado nenhuma imagem para limite superior")
                raise FileNotFoundError()

            if len(self.image_container.bottom_border) == 0:
                menu_s_logger.error("Não foi encontrado imagens para o limte inferior")
                raise FileNotFoundError()
            
            if len(self.image_container.upward_step) == 0:
                menu_s_logger.error("Não foi encontrado imagens para o passo superior")
                raise FileNotFoundError()
            
            if len(self.image_container.upward_step) == 0:
                menu_s_logger.error("Não foi encontrado imagens para o passo superior")
                raise FileNotFoundError() 
            
            if len(self.image_container.target) == 0:
                menu_s_logger.warning("Não foi encontrado imagens para o alvo")
                menu_s_logger.warning("Você deve espeficiar uma imagem alvo")
        

class StepError(Exception):
    
    def __init__(self, message) -> None:
        super().__init__(message)
        self.message = message

if __name__ == "__main__":
    
  


    print("fim")

