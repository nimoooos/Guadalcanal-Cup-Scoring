from colorama import Fore, Back, Style

image = ("                                                                                 \n"
         "                                        /*                                       \n"
         "                                        /**                                      \n"
         "             *******************************************************             \n"
         "             **###***########**#########****@@@@@**@@@@@@@@@**&@@@**             \n"
         "             **######**#######**########*****@@@@*@@@@@@@@**@@@@@@**             \n"
         "             **########*#######*########******@@*@@@@@@@@*@@@@@@@@**             \n"
         "             *****######################*******@@@@@@@@**@@@@@%*****             \n"
         "             **###^**######*********************(@@@@/*@@@@%**@@@@**             \n"
         "             **######^**####(*********************@@@@@@@*(@@@@@@@**             \n"
         "             **###############*********************@@@@@@@@@@@@@@@**             \n"
         "             *******###########**********@@@@@@@@@@@@@@@@@@/%*******             \n"
         "             **#####^%****######**********@@@@@@@@@@@@@**%/@@@@@@@**             \n"
         "             **##################**********@@@@@@@@@@@@@@@@@@@@@@@**             \n"
         "         */  **********###########**********@@@@@@@@@@@@@@%*********  **         \n"
         "        ** ****####################**********@@@@@@@@@@@@@@@@@@@@@**** **        \n"
         "     ****     **####################**********@@@@@@@@@@@@@@@@@@%**     ***      \n"
         " /***    ^      /***#################(*********@@@@@@@@@@@@@&**%       %   ***** \n"
         "    **             (******####******************@@@@@@@*****               **    \n"
         "      (**                 ^^^***********%%%%%%%%%%%%%%%                %**/      \n"
         "         (***                                                       ***          \n"
         "             (***         L I G H T N I N G    L A B S          ***%             \n"
         "                *****                                        ***                 \n"
         "                  ********************************************                   \n"
         "                   **##############(****@@@@@@@@@@@@@@@@@@@@*                    \n"
         "                     ****###########(***@@@@@@@@@@@@@@@@***%                     \n"
         "                         ^^***########**@@@@@@@@@@@****%                         \n"
         "                              ^^***####*@@@@@&%****                              \n"
         "                                   ^%*##*%***                                    \n"
         "                                       **                                        \n"
         "                                                                                 \n"
         "                     +   S P A R K   I N N O V A T I O N   +                     \n"
         "                                                                                 \n")


def print_logo(time: float = 0, mode: str = "COLOR"):
    """
    mode can be BASIC, COLOR, or MATRIX
    """
    from time import sleep
    IMAGE_LENGTH = 82*33
    SPEED = time/IMAGE_LENGTH

    if mode == "BASIC":
        for pixel in image:
            sleep(SPEED)
            print(pixel, end="")

    elif mode == "MATRIX":
        for pixel in image:
            sleep(SPEED)
            if pixel == "\n": print(Style.RESET_ALL)
            else: print(Back.BLACK + Fore.LIGHTGREEN_EX + pixel, end="")

    elif mode == "COLOR":
        for pixel in image:
            sleep(SPEED)
            match pixel:
                case "*": print(Style.RESET_ALL+Back.YELLOW+Fore.LIGHTYELLOW_EX, end="")
                case "(": print(Style.RESET_ALL+Back.YELLOW+Fore.LIGHTYELLOW_EX, end="")
                case "/": print(Style.RESET_ALL+Back.YELLOW+Fore.LIGHTYELLOW_EX, end="")
                case "&": print(Style.RESET_ALL+Back.YELLOW+Fore.LIGHTYELLOW_EX, end="")
                case "%": print(Style.RESET_ALL+Back.YELLOW+Fore.LIGHTYELLOW_EX, end="")
                case "^": print(Style.RESET_ALL+Back.YELLOW+Fore.LIGHTYELLOW_EX, end="")
                case "#": print(Style.RESET_ALL+Back.BLACK+Fore.RED+Style.BRIGHT, end="")
                case "+": print(Style.RESET_ALL+Back.BLACK+Fore.RED, end="")
                case "@": print(Style.RESET_ALL+Back.BLACK+Fore.LIGHTBLACK_EX, end="")
                case " ": print(Style.RESET_ALL+Back.BLACK, end="")
                case "\n": print(Style.RESET_ALL, end="")
            print(pixel, end="")
    return None


if __name__ == '__main__':
    print_logo()
