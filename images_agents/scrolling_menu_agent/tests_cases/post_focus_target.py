from pathlib import Path
import sys
import logging

num_dir_to_src = 2
src_folder = Path(__file__)
for i in range(num_dir_to_src): src_folder = src_folder.parent

if src_folder not in sys.path: sys.path.append(str(src_folder))
if Path.cwd() not in sys.path: sys.path.append(Path.cwd().__str__())

from menu_scroller import MenuScrolling, menu_s_logger
from logger import create_logger, make_filehandler
from controlador_imagem import img_aux_logger
from tests_cases.ted_manager.ted_controller import TedActuator, ted_controller_logger


log_file = Path(__file__).parent / "post_focus_target_logs.log"
if __name__ == "__main__": post_f_target_logger = create_logger("", log_file)
else: post_f_target_logger = create_logger(__name__, log_file)


if __name__ == "__main__":

    post_f_target_logger.setLevel(logging.INFO)
    menu_s_logger.addHandler(make_filehandler(log_file))
    img_aux_logger.addHandler(make_filehandler(log_file))
    ted_controller_logger.addHandler(make_filehandler(log_file))

    menu_folder_image = src_folder / r"general_images\ted_sefaz"
    post_focus_target_menu_folder = menu_folder_image / "post_focus_target"
    post_focus_targets_path: list[Path] = [img_path for img_path in post_focus_target_menu_folder.iterdir()]

    ted_app = TedActuator()
    ted_app.open_app()
    ted_app.go_to_testar_tab()
    ted_app.open_scroll_menu()

    find_in_scrolling_menus = MenuScrolling(menu_folder_image)
    find_in_scrolling_menus.load_images(post_focus_targets_path)
    find_in_scrolling_menus.search_by_focus("down", 12)
    
    ted_app.close_ted()
