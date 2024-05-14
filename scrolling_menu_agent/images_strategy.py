from dataclasses import dataclass, field
from typing import List
from pyscreeze import Box

from ..logger import create_logger

# Logging config
if __name__ == '__main__': 
    ele_strategy_logger = create_logger('')
    ele_strategy_logger.setLevel(20)
else: 
    ele_strategy_logger = create_logger(__name__, without_handler = True)

@dataclass
class MenuElementImageStratagy():
        """Indica qual será a stratégia usada para escolher dentre as imagens encontradas 

        Args:
            `reference_direction` (str, optional): Direção usada como referência para escolher a \n
            imagem. Pode assumir 2 valores: "vertical" e "horizontal". Defaults to None. \n

            `position_in_direction` (int, optional): Qual é a posição que a image ocupa dentro  \n
            da direção informada. Por exemplo, se o valor desse parâmetro for 2 isso quer \n
            dizer que a segunda imagem com maior coordenada naquela direção será escolhida. \n
            Defaults to None.

        Referencia da imagem:

        ------+------------------> X-axis (positive)\n
            1 |\n
            2 |\n
            3 |\n
              v\n
                Y-axis (positive)
        """

        reference_direction: str = field(default="vertical")
        position_in_direction: int = field(default=1)

@dataclass
class MenuElementsStratagy:
    """
    Referencia da imagem

-----+------------------> X-axis (positive)\n
     1 |\n
     2 |\n
     3 |\n
       v\n
        Y-axis (positive) \n
    
    `reference_direction` (str, optional): Direção usada como referência para escolher a \n
    imagem. Pode assumir 2 valores: "vertical" e "horizontal". Defaults to None. \n

    `position_in_direction` (int, optional): Qual é a posição que a image ocupa dentro  \n
    da direção informada. Por exemplo, se o valor desse parâmetro for 2 isso quer \n
    dizer que a segunda imagem com maior coordenada naquela direção será escolhida. \n
    Defaults to None.
    """
    number_menus: int
    upward_step: MenuElementImageStratagy = field(default_factory= MenuElementImageStratagy)
    downward_step: MenuElementImageStratagy = field(default_factory= MenuElementImageStratagy)


class Suntzu:
    def __init__(self, elements_strategy: MenuElementsStratagy) -> None:

        self.elements_strategy = elements_strategy
        

    def choose_step_image(self, direction: str, images: List[Box]):

        if self.elements_strategy.number_menus != len(images):
            ele_strategy_logger.warning(f"A quantidade de imagens de passos ({direction}) encontrados é "
                                        "diferente da quantidade de menus que estão na tela")
        
        
        if direction == "up":
            # Quanto maior o valor na coordenada y isso indica que a imagem está
            # mais abaixo na tela

            assert len(images) >= self.elements_strategy.downward_step.position_in_direction,\
            f"A quantidade de imagens de passos ({direction}) encontra é menor do que a posição "
            "da imagem que se procura \n" + f"Imagens: {images} \n Posição: {self.elements_strategy.downward_step.position_in_direction}"
            
            if self.elements_strategy.upward_step.reference_direction == "vertical":
                
                desc_sorted_boxes_in_direction = sorted(images, reverse=True, key=lambda box: box.top)

            elif self.elements_strategy.upward_step.reference_direction == "horizontal":

                desc_sorted_boxes_in_direction = sorted(images, reverse=True, key=lambda box: box.left)

            box = self.get_nth_highest_coordinate(desc_sorted_boxes_in_direction, self.elements_strategy.upward_step.position_in_direction)

            return box
        
        elif direction == "down":

            assert len(images) >= self.elements_strategy.downward_step.position_in_direction,\
            f"A quantidade de imagens de passos ({direction}) encontra é menor do que a posição \
            da imagem que se procura \n" + f"Imagens: {images} \n Posição: {self.elements_strategy.downward_step.position_in_direction}"

            
            if self.elements_strategy.downward_step.reference_direction == "vertical":

                desc_sorted_boxes_in_direction = sorted(images, reverse=True, key=lambda box: box.top)

            elif self.elements_strategy.downward_step.reference_direction == "horizontal":

                desc_sorted_boxes_in_direction = sorted(images, reverse=True, key=lambda box: box.left)

            box = self.get_nth_highest_coordinate(desc_sorted_boxes_in_direction, self.elements_strategy.downward_step.position_in_direction)

            return box
        


    def get_nth_highest_coordinate(self, desc_sorted_boxes_in_direction: List[Box], n):

        if 1 <= n <= len(desc_sorted_boxes_in_direction):
            return desc_sorted_boxes_in_direction[n - 1]
        else:
            return None