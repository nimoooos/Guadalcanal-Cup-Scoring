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
         "                    +   S P A R K   I N N O V A T I O N S   +                    \n"
         "                                                                                 \n")


def print_logo():
    for pixel in image:
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
            case default: print(Style.RESET_ALL+Back.BLACK, end="")
        print(pixel, end="")
    return None
