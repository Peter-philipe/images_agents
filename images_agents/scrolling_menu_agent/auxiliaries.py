from typing import List


# Criar uma estrutura de dados com mais performace
# é uma alternativa tuple
class MenuImagesContainer:
    
    def __init__(self): 
    
        self.top_border: List[str] = []
        self.bottom_border: List[str] = []
        self.upward_step: List[str] = []
        self.downward_step: List[str] = []
        self.target: List[str] = []


class StepsCounter:

    def __init__(self) -> None:
        """ ### Count and store the steps made in each direction
        """
        self.upward_steps_made: int = 0
        self.downward_steps_made: int = 0
    
    def count(self, direction: str, steps: int):
        """ Count steps in the chosen direction

        Args:
            `direction` (str): `up` and `down` are the options \n
            `steps` (int): number of clicks in the chosen directions. Defaults to 3.
        """
        if direction == "up":
            self.upward_steps_made = self.upward_steps_made + steps

        elif direction == "down":
            self.downward_steps_made = self.downward_steps_made + steps
        else:
            print(f"direction isn't mapped: <<{direction}>>")
            raise ValueError()
    
    def steps(self, direction: str) -> int:
        """### Inform the steps made in one direction

        Args:
            `direction` (str): `up` and `down` are the options \n

        Returns:
            `int`: steps made
        """
        if direction == "up":
            return self.upward_steps_made 

        elif direction == "down":
            return self.downward_steps_made
        else:
            print(f"direction isn't mapped: <<{direction}>>")
            raise ValueError()

    def refresh(self):
        """### restart the counters
        """
        self.upward_steps_made = 0
        self.downward_steps_made = 0

if __name__ == "__name__":
    
    pass
    