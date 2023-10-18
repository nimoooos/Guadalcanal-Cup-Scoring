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


def print_logo(time: float= 0, matrix_mode: bool = False):
    from time import sleep
    IMAGE_LENGTH = 1207  # not counting blank space
    SPEED = time/IMAGE_LENGTH

    for pixel in image:
        speed = SPEED
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
            case " ":
                print(Style.RESET_ALL+Back.BLACK, end="")
                speed = 0
            case "\n": print(Style.RESET_ALL, end="")
            case default: print(Style.RESET_ALL+Back.BLACK, end="")
        if matrix_mode and pixel != "\n": print(Back.BLACK + Fore.LIGHTGREEN_EX, end="")
        print(pixel, end="")
        sleep(speed)
    return None


if __name__ == '__main__':
    print_logo()
    print_logo(time=10, matrix_mode=True)
