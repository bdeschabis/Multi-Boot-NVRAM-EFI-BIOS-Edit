# This # -*-coding:Latin-1 -*
# 09/06/2021
# -- reminder: sudo blkid gives the list of partitions sda1, sda2,... with their partition UUID, like this:
# /dev/sda2: UUID="ec29c189-4443-477d-a5b2-cc27ee4f2f5f" TYPE="ext4" PARTUUID="53fdb494-8960-43d9-9046-05d9a9535af2"
# /dev/sdb1: LABEL_FATBOOT="EFI" LABEL="EFI" UUID="70D6-1701" TYPE="vfat" PARTLABEL="EFI System Partition" PARTUUID="44114127-5172-48c4-8013-a08d6ae5998d"
# /dev/sdb2: UUID="595f05fc-254f-404d-85aa-e3738190a1b3" TYPE="apfs" PARTLABEL="macOS" PARTUUID="aea857a6-cd93-485e-8bbd-38479205d2c8"
# /dev/sda1: UUID="56B9-798D" TYPE="vfat" PARTLABEL="Efi Sda1" PARTUUID="c3312c62-42d0-4cd3-8c26-875eb96dd1b0"
# /dev/sda3: UUID="4dd750d9-d6e7-46dd-af8e-dce0ef7215b7" TYPE="swap" PARTUUID="e45e375c-3841-4d4f-82ef-2fc522663841"
# /dev/sda4: UUID="b1917d60-2061-4f87-b5c4-8450dc43bbd8" TYPE="ext4" PARTUUID="982182cb-d81a-4eb8-8a83-7b4a4b158cd4"
# /dev/sda5: LABEL="Exfat" UUID="1075-3F3C" TYPE="exfat" PTTYPE="dos" PARTUUID="c113352b-2888-7648-a50e-a8450cb27dd9"

# --          sudo efibootmgr -v lists NVFAT lines and boot order
# BootOrder: 0003,0004,0005,0006,0001
# Boot0001* Refind AppleSdb	HD(1,GPT,44114127-5172-48c4-8013-a08d6ae5998d,0x28,0x64000)/File(\EFI\refind\refind_x64.efi)
# Boot0003* Refind Sda1	HD(1,GPT,c3312c62-42d0-4cd3-8c26-875eb96dd1b0,0x800,0x100000)/File(\EFI\refind\refind_x64.efi)
# Boot0004* Mint Sda1	HD(1,GPT,c3312c62-42d0-4cd3-8c26-875eb96dd1b0,0x800,0x100000)/File(\EFI\debian\shimx64.efi)
# Boot0005* Refind Sdc	HD(1,GPT,483d0a05-f775-45f0-8904-07eedefc4935,0x800,0x79800)/File(\EFI\refind\refind_x64.efi)
# Boot0006* Kubuntu Sdc	HD(1,GPT,483d0a05-f775-45f0-8904-07eedefc4935,0x800,0x79800)/File(\EFI\debian\shimx64.efi)
# BootFFFF* 	PciRoot(0x0)/Pci(0x1f,0x2)/Sata(0,0,0)/HD(1,GPT,c3312c62-42d0-4cd3-8c26-875eb96dd1b0,0x800,0x100000)/File(\EFI\BOOT\BOOTX64.efi)


#================================================================
# pour lancer le script, ne pas utiliser exec mais sudo dans un terminal

import os  # fonctions propres à l'OS linux, window, ...dont on peut tirer le séparateur système et change dir
import sys
import time
import subprocess
import tkinter as tk
from tkinter import Checkbutton
#import socket

#jump to the directory containing the program
dir=format(os.getcwd())
os.chdir(dir)


#===========================declaration of variables that will be global in the procedures
table_blkid_brute = []
table_blkid_nette = []
table_efibootmgr_net = []
table_EFIsdx = []
table_commentaire = []
table_intermed = []
table_lignes_affichees = []
messages_ano_bootorder = []
iblkid = 0
ilignes_EFI = 0
BootOrder = ""
global_bootorder=""
global_booCurrent="xxxx"
EFI_MBR="EFI"
global bit_bouton
bit_bouton = 0


non_monté = "non"    # flag reporting valid EFI lines but whose partUUID is not in blkid
blancs="                                                                                 "
dir_travail = os.path.abspath(os.path.dirname(__file__))  # determines the directory of the program
os.chdir(dir_travail)  # Change Directory where is "efibootmgr_Us.py"
#================================ efibootmgr program must be run as a root user
if os.getuid() != 0:
    print("this program must be run as a root user")
    print("Press the enter key")
    sys.exit()
#--------check if blkid and efibootmgr on this machine, necessary for this program-----------------------
#=============   result of "which efibootmgr" is "/bin/efibootmgr" or nothing if efibootmgr not installed.
try:
    subprocess.check_call("which efibootmgr > " + '"' + dir_travail + "/efibootmgr_blkid.txt" + '"', shell=True)
except:
    print("efibootmgr missing")
try:
    subprocess.check_call("which blkid >> " + '"' + dir_travail + "/efibootmgr_blkid.txt" + '"', shell=True)
except:
    print("blkid missing")
try:
    subprocess.check_call("which lsblk >> " + '"' + dir_travail + "/efibootmgr_blkid.txt" + '"', shell=True)
except:
    print("lsblk missing")

efibootmgr_etat = open(dir_travail + "/efibootmgr_blkid.txt", 'r')
efibootmgr_status = efibootmgr_etat.read()
efibootmgr_etat.close()
os.remove(dir_travail + "/efibootmgr_blkid.txt")  # efface fichier résidu d'un précédent passage éventuellement

if "/efibootmgr" in efibootmgr_status:
    pass
else:
    sys.exit("efibootmgr not found on this machine. Install efibootmgr")
if "/blkid" in efibootmgr_status:
    pass
else:
    sys.exit("blkid not found on this machine. Install blkid")
if "/lsblk" in efibootmgr_status:
    pass
else:
    sys.exit("lsblk not found on this machine. Install lsblk")

# ------------------------------- fin de vérification de la présence de blkid , efibootmgr et lsblk-----------


# ============================= procedure for displaying the message if help requested (param "h" at the end of the command line)=============================
def aidez_moi():
    print("program displaying the EFI launchers of this system. It uses the sudo efibootmgr and blkid commands")
    print("as well as python3 libraries os, sys, tkinter, signal, ")
    print("It can receive parameters ""h"" (help me), ""t"" (display in terminal) and ""v"" (with comment)")
    print("It must be launched as a super user (root)")
    print("by example : sudo python3 /home/path to.../efibootmgr_sdy.py 'h'")
    if os.getuid() != 0:  # ---check that it is running as root
        print("Since it's not, you'll be fired in 10 seconds.")
        time.sleep(10)
        quit()

# =================================fin de procédure aidez_moi ===================================================

# ------------------acquiring parameters from the command line----------------------


printer = "non"
verbeux = "0"
for param in sys.argv:
    if len(param) == 1:
        if (param == "h") or (param == "H"):
            aidez_moi()
            break
        else:
            if (param == "t") or (param == "T"):
                printer = "oui"
            else:
                if (param == "v") or (param == "V"):
                    verbeux = "1"
# -------------------------------fin acquisition paramètres --------------------------------


# -------------------- deleting old files if necessary-----------------------------
if os.path.exists(dir_travail + "/blkid.txt"):  # supprime le fichier résidu éventuel
    os.remove(dir_travail + "/blkid.txt")

if os.path.exists(dir_travail + "/efiboot.txt"):  # supprime le fichier résidu éventuel
    os.remove(dir_travail + "/efiboot.txt")


# ======== initial values for windows
#__________________________________________________________ici
global largeur_fenetre
global hauteur_fenetre
global LargeurScreen
global HauteurScreen
global coin_x
global coin_y


window = tk.Tk()
LargeurScreen = window.winfo_screenwidth()
HauteurScreen = window.winfo_screenheight()
largeur_fenetre = 930
hauteur_fenetre = 420
coin_x=(LargeurScreen - largeur_fenetre) / 2
coin_y=(HauteurScreen - hauteur_fenetre) / 2



bit_triEFI = 1   #----used for displaying EFI lines in natural order or according to BootOrder NVRAM table
verbeux="0"

#===================================  composition of an explanatory spiel =============================
#-----------------the "table_commentaire" table contains the spiel lines displayed at the bottom of the window
table_commentaire.append("   ")
table_commentaire.append("Glossary: NVRAM is non-volatile memory stored on the motherboard. It contains, among other things, a list")
table_commentaire.append("of the executable modules launching the different OS (Operating System: windows, linux, ...), with their location")
table_commentaire.append("on the different units hosting these OS. It also contains a priority table indicating in which order must be read")
table_commentaire.append("the list of these modules when starting the computer (BootOrder table above)")
table_commentaire.append("When installing a new operating system, its installer program adds to the NVRAM a line locating its own boot module")
table_commentaire.append("and it places the index of this new item at the top of the BootOrder table")
table_commentaire.append("The 'BootOrder' line of this screen presents the order in which the various modules are taken into account (priorities),")
table_commentaire.append("and the following lines, which we call 'EFI lines', present the different modules with their location")
table_commentaire.append("     ")
table_commentaire.append("<Warning!!!> These EFI lines are NVRAM lines and all of them may not be valid at this time .")
table_commentaire.append("there are in fact all the launchers of the EFI folders of the ESP partitions with which the computer has already booted.")
table_commentaire.append("Use Refind to see all usable launchers at boot time, and efibootmgr or efibootmgrgui.py to reorder them.")
table_commentaire.append("The 'sudo efibootmgr -v' command shows boot entries with the UUIDs of the EFI partitions containing them, but")
table_commentaire.append("using the UUID is inconvenient. The purpose of efibootmgr_Us.py is to additionally provide for each partition UUID")
table_commentaire.append("its common linux name: sda1, sdb1, sdc1.... relying on the result of the 'blkid' command")
table_commentaire.append("In order to never be blocked at boot, it is in your interest, for each system, to place the Refind software launcher at")
table_commentaire.append("the top (entry '\EFI\\refind\\refind_x64.efi') because it detects at boot time all bootable entries.")
table_commentaire.append("The Refind installer installs its own launcher in /boot/efi/EFI/refind/refind_x64.efi.")
table_commentaire.append("(if ESP partition is /dev/sdc1 and root is /dev/sdc2, then /dev/sdc1/EFI/ is mounted in /dev/sdc2/boot/efi)")
table_commentaire.append("the program efibootmgrgui.py (python GUI) also allows to change the boot order of the launchers")
table_commentaire.append("or register new ones")
table_commentaire.append("Similarly, the grub installer adds its own launchers /boot/efi/EFI/ubuntu/shimx64.efi and grubx64.efi")
table_commentaire.append("On a system whose EFIbios only accepts digitally signed launchers, you cannot start using grubx64.efi,")
table_commentaire.append("which is not signed. Shimx64.efi on the other hand is signed, and is therefore accepted")
table_commentaire.append("The only role of shimx64.efi is then to chain to grubx64.efi and that's it.")
table_commentaire.append("                                    efibootmgr : useful commands ")
table_commentaire.append('List of NVRAM : <" sudo efibootmgr -v " >          ')
table_commentaire.append("Replacing the BootOrder record  : " + ' <"sudo efibootmgr -o 0002,0001,0000,00003,00007"> ')
table_commentaire.append('Removal of the bootloader 000x item : <"sudo efibootmgr -b 000x -B">')
table_commentaire.append('< Attention, in what follows, the usual \ of Linux paths must imperatively be replaced by />')
table_commentaire.append("Adding an item '"'/EFI/refind/refind_x64.efi'"' for the ESP partition sdc1 for example: <>")
table_commentaire.append('< sudo efibootmgr --create --disk /dev/sdc --part 1 --label "Refind " --loader /EFI/refind/refind_x64.efi>')
table_commentaire.append("Adding an item  '"'/EFI/ubuntu/shimx64.efi'"' for the ESP partition sdb1 for example: <>")
table_commentaire.append('< sudo efibootmgr --create --disk /dev/sdb --part 1 --label "Ubuntu " --loader /EFI/ubuntu/shimx64.efi>')
table_commentaire.append("(this loader, signed, launches grubx64.efi, unsigned, which is in the same directory). <> ")
table_commentaire.append("")
table_commentaire.append("=================================================================================================")
table_commentaire.append("Here are a few explanations about the starting up  of  the computers known as UEFI or EFI BIOS.")
table_commentaire.append("On any mother board there is a memory which is not erased  even after the computer shuts down.")
table_commentaire.append("This non volatile memory is often called NVRAM : acronym for Non Volatile Random Access Memory. ")
table_commentaire.append("Among other things, that memory contains : ")
table_commentaire.append("A table of which every row can indicate the name of a program that is launched immediately")
table_commentaire.append("before the activation of any OS (windows, Linux...) and also the physical unit in which the")
table_commentaire.append("program is (UUID of its partition) and also, in that  unit, the path which leads to it and its")
table_commentaire.append("file name (for instance /EFI/ubuntu/shimx64.efi)")
table_commentaire.append("It also contains a table which indicates in what order the rows of the previous table must be")
table_commentaire.append("browsed so as to  decide which sytem must be launched first, then secondly in case the first")
table_commentaire.append("one fails, then  thirdly and so on.")
table_commentaire.append("Quite logically, that second table is called BootOrder and each of its rows contains the rank")
table_commentaire.append("of an item of the first table, in the form of a four digit number in hexadecimal notation")
table_commentaire.append("(0000,0001,...000A....)")
table_commentaire.append("A small program, which is also present in non volatile memory (called BIOS) is run as soon as")
table_commentaire.append("the computer is powered up. Through the reading of the BootOrder table, its detects which row")
table_commentaire.append("of the first table it has to operate and therefore which program it has to load from the disk")
table_commentaire.append("for immediate running. As it is not very intelligent, it understands nothing else than the file")
table_commentaire.append("system FAT32. The partitions whose UUID are contained in the first table must therefore be in")
table_commentaire.append("the FAT 32 format so that the small program can  find, load and run the launching of the OS.")
table_commentaire.append("Moreover, they also have to be flagged as ESP or EFI and Bootable .  Otherwise they are ignored")
table_commentaire.append("in the process.")
table_commentaire.append("On quality mother boards, the BIOS is intelligent enough to offer, in graphical display,  the")
table_commentaire.append("tools enabling to create or modify rows of the first table and reorder BootOrder. But on basic")
table_commentaire.append("or ancient systems , that tool is either rudimentary or missing. In that case, the tables can")
table_commentaire.append("only be modified by a program loaded from a CD or a bootable USB key.")
table_commentaire.append("Finally, during the installation of an OS (UBUNTU for instance) the installation program (GRUB-INSTALL ")
table_commentaire.append("or UBUNTU) enriches the NVRAM by inscribing a row which locates the start up module")
table_commentaire.append("(shimx64.efi for UBUNTU) and adds the rank of that new row at the top of the Boot Order table.")
table_commentaire.append("At the next start up, in that example, it is shimx64.efi which will be run and will launch UBUNTU.")
table_commentaire.append("NB : An authentication mechanism has been imagined to protect the computer from the installation")
table_commentaire.append("of non authentical starting programs. That mechanism is included in the BIOS which verifies the")
table_commentaire.append("signature of every program before launching it. However, this checking can be avoided by activating")
table_commentaire.append("the CSM option of the BIOS (CSM: Compatibility Support Module) in order to start an OS that is on")
table_commentaire.append("a non-UEFI disk")
table_commentaire.append("Yet, under Linux, there exists different non-signed  launchers whose launching would be refused")
table_commentaire.append("in a protected computer except by asking Microsoft to authenticate them.")
table_commentaire.append("That is why one has to use the shim program, which is signed and whose role is to launch the")
table_commentaire.append("grub program (Linux boot loader) corresponding to each Linux version.")
table_commentaire.append("")
table_commentaire.append("==============================Aim of  the present program :==================================")
table_commentaire.append("As the bios program can only read the FAT partitions whose flag is ESP or EFI, the program")
table_commentaire.append("presents only those units in the 'sda1, sdb1, sdc2...' form, according to the Linux convention.")
table_commentaire.append("It enables one to create, modify, suppress rows from the table which contains the OS starting")
table_commentaire.append("up programs and also to modify the classification on the Bootorder table.")
table_commentaire.append("In fact, according to the indications it receives and to the NVRAM content, it composes and")
table_commentaire.append("launches the commands which could have been laboriously created manually in a terminal to reach")
table_commentaire.append("the same result.")
table_commentaire.append("The used commands are displayed at the bottom of each window before being executed.")

#===================================== fin composition baratin =============================================


#================ proc d'extraction des infos de blkid pour faire une table pour chaque info ================
def extrac_dev_partUUID_de_blkid():
    global iblkid
    global table_blkid_brute
    global table_blkid_nette
    global dir_travail
    global BootOrder
    global blancs

    #================================= extraction des infos de la commande blkid ======================================
    # ----------- mise en mémoire de la table résultant de la commande "sudo blkid" . Exemples de lignes :-------------
    # --- /dev/sda2: UUID="ec29c189-4443-477d-a5b2-cc27ee4f2f5f" TYPE="ext4" PARTUUID="53fdb494-8960-43d9-9046-05d9a..."
    # --- /dev/sdb1: UUID="DD33-62A7" TYPE="vfat" PARTLABEL="Efi Sdb1" PARTUUID="483d0a05-f775-45f0-8904-07eedefc4935"

    #------------------le fichier blkid.txt a été créé dans la procédure faire_ou_refaire_le_boulot--------------------
    fich_blkid = open("blkid.txt", 'r')  # defines the object fich-blkid as readable file blkid.txt
    table_blkid_brute = fich_blkid.readlines()  # done, table_blkid_brute is done
    fich_blkid.close()  # close fich_blkid
    os.remove(dir_travail + "/blkid.txt")  #-------------------on n'en aura plus besoin
    # -------------------------- fin de mise en mémoire de la table  "table_blkid_brute"-------------------------------------------
    type_part = "-------------------------------"
    iblkid = 0
    for blkid in table_blkid_brute:
        dev_sd = blkid[0:11]  # extrait /dev/sdxy:
        dev_sd = dev_sd .replace(chr(47), chr(92))   #  replace slash with backslash

        idx1 = str.find(blkid, ' PARTUUID=')
        if idx1 != -1:
            droite = blkid[(idx1+11):]
            idx2 = str.find(droite ,'"')
            if idx2 != -1:
                partuuid = droite[:idx2]
                partuuid = partuuid + blancs
                partuuid = partuuid[:36]
            else:
                partuuid = blancs
        else:
            partuuid = blancs

        #--  In the end, to find the device associated with each efibootmgr item, just keep device + partUUID in table_blkid_nette
        ligne = "!" + dev_sd + "!" + partuuid + "!"  # sous cette forme  !/dev/sda2: !53fdb49...d9a9535af2!  with dev from 2 to 10 and PartUUID from 13 to 49
        table_blkid_nette.append(ligne)
        iblkid = iblkid+1
#============== fin extrac_dev_partUUID_de_blkid


#======================procédure d'extraction des infos de "efibootmgr -v" ===================================
def extract_efibootmgr():
    #======================= mémorisation des résultats de la commande "efibootmgr -v" comme ceci ==========
    #    order    |  efibootmgr_libel |       table_efibootmgr_EFIpart        |     table_efibootmgr_partfile
    #  Boot0000*  | Refind Sda1...... |  c3312c62-42d0-4cd3-8c26-875eb96dd1b0 |  \EFI\refind\refind_x64.efi....
    #  Boot0001*  | Elementary Sdc1.. |  4611294d-5452-4f5c-a21c-3a6ebecdd797 |  \EFI\ubuntu\shimx64.efi.......
    # ------------------le fichier efiboot.txt a été créé dans la procédure faire_ou_refaire_le_boulot---------------


    fich_efiboot = open("efiboot.txt", 'r', errors='ignore')  # calque l'objet fich-efiboot comme fichier en lecture sur efiboot.txt
    table_efiboot = fich_efiboot.readlines()
    fich_efiboot.close()  # ferme le fichier fich_efiboot
    os.remove(dir_travail + "/efiboot.txt")  # -------------------on n'en aura plus besoin
    global table_efibootmgr_net
    global ilignes_EFI
    global BootOrder
    global global_bootorder
    global EFI_MBR
    global global_booCurrent
    BootOrder = "no Boot0rder, EFIbios will act by default or do ""sudo efibootmgr -o 0000,0001,0002 par exemple"""   # init bootorder

    # la commande sudo efibootmgrgui liste les postes EFI, et permet de les reclasser (choix du boot) d'en créer ou supprimer.
    # la ligne  de efibootmgrgui est pour le poste 0003 par exemple "0003   ubuntu   \EFI\refind\refind_x64.efi"
    #           il y manque donc le volume /dev/sdx, car il peut y avoir plus d'un dossier \EFI\refind\refind_x64.efi (un par disque bootable)
    #
    # la ligne de la commande blkid est "/dev/sda1: UUID="56B9-798D" TYPE="vfat" PARTLABEL="Efi Sda1" PARTUUID="c3312c62-42d0-4cd3-8c26-875eb96dd1b0"
    #                                ce qui établit le lien entre volume (/dev/sdx) et partUUID
    # la ligne de efibootmgr -v est "Boot0003* ubuntu 	HD(1,GPT,c3312c62-42d0-4cd3-8c26-875eb96dd1b0,0x800,0x100000)/File(\EFI\refind\refind_x64.efi)
    #           cette dernière nous donne tout, sauf le volume en clair (/dev/sda1)
    #
    # aussi, par EFI, nous allons afficher "Boot0003 | ubuntu ....| /dev/sda1 | \EFI\refind\refind_x64.efi....| c3312c62-42d0-4cd3-8c26-875eb96dd1b0"
    #                           ce qui nous dira quel est le volume ^^^^^^^^^  associé à la ligne  "Boot0003" de efibootmgrgr.

    ilignes_EFI = 0
    partfile = " non défini                          "
    BootOrder=""

    for efiboot in table_efiboot:  # pour chaque ligne de sudo efibootmgr -v-

        if efiboot[0:9] == "BootOrder":
            BootOrder = efiboot
            global_bootorder=BootOrder
        else:
            if efiboot[0:13] == "BootCurrent: ":
                global_booCurrent=efiboot[13:17]
             #==================================début lignes non Bootorder=========================================
            else:
                if efiboot[0:6] == "Boot00":   #élimine les lignes Timeout, BootOrder, ...mais garde Boot00xx
                    EFI_MBR ="EFI"
                    deb_UUID = 0
                    efiboot = efiboot + blancs
                    order = efiboot[0:8]  # extrait Boot0001*
                    idx1 = 10

                    #idx2 = str.find(efiboot, chr(9))  # attention   entre quotes, caractère ascii 09 (tabulation horizontale)

                    efiboot = efiboot.replace(chr(9),"")


                    idx2=str.find(efiboot, "HD(")
                    if idx2 != -1:
                        libel = efiboot[idx1:idx2]
                        deb_UUID = idx2 + 9
                        libel = libel+blancs
                    else:
                        idx2 = str.find(efiboot, "BBS(")
                        if idx2 != -1:
                            libel = efiboot[idx1:idx2]
                            deb_UUID = 0
                        else:
                            idx2 = str.find(efiboot, "Connection")
                            if idx2 != -1:
                                libel = efiboot[idx1:idx2]
                                deb_UUID = 0
                            else:
                                libel = blancs
                    libel=libel+blancs
                    libel = libel[0:21]

                    if deb_UUID != 0:
                        idx1=deb_UUID
                        idx2=efiboot.find(",", idx1)
                        #idx2=len(efiboot) -44
                        if idx2 != -1:
                            partUUID=efiboot[idx1:idx2] + blancs
                        else:
                            partUUID = "     na     " + blancs
                    else:
                        partUUID =  "     na     " + blancs

                    partUUID = partUUID[0:36]

                    idx1 = str.find(efiboot,'/File(') + 6
                    idx2=efiboot.find(')',idx1 )            #============parentèse fermante après /File(
                    if idx1 != -1:
                        partfile = efiboot[idx1:idx2] + blancs
                    idx3=str.find(partfile.casefold(), ".efi")

                    if idx3 != -1:
                        idx3=idx3+4
                        partfile=partfile[0:idx3]
                    else:
                        EFI_MBR="---"
                        partfile = blancs


                    partfile = partfile + blancs

                    partfile = partfile[0:35]

                    #if bonne_ligne == "oui":
                    ilignes_EFI = ilignes_EFI + 1

                    # si GPT table_efibootmgr_net = ">Boot000A<>Mint Sda1........<>d3312c62-42d0-4cd3-8c26-875eb96dd1b0<>\EFI\debian\shimx64.efi.....<"
                    # si MBR
                    table_efibootmgr_net.append(">" + order + "<>" + libel + "<>" + partUUID + "<>" + partfile + "<>" + EFI_MBR + "<")

                # =============fin if efiboot[0:6] == "Boot00":============================

        #-------ignorer les lignes non Boot000x





    if (BootOrder == ""):
        print ("no BootOrder in NVRAM, we can't go on")
        messages_ano_bootorder.append("no BootOrder in NVRAM, we are in deep shit")
        # quit()    # a reactiver
        bit_triEFI = 0













#====================== fin de la procédure extract_efibootmgr ==========================================

#===== croisement des tables efibootmgr et blkid selon l'UUID pour report de "/dev/Sdx"  de blkid vers efibootmgr====
def croisement_efibootmgr_blkid_selon_UUID():
    #-- rappel : sudo blkid donne la liste des partitions sda1, sda2,... avec leur UUID de partition
    #--          sudo efibootmgr -v  donne la liste des postes de la NVFAT et l'ordre de démarrage
    #-- pour chaque part UUIDposte de la table des lignes EFI, on cherche la même UUID dans blkid
    #-- et on en déduit le /dev/sdx  tiré de table_blkid_nette(de pos 2 à 10) de même rang.
    global table_blkid_nette
    global table_EFIsdx
    global ilignes_EFI
    global table_efibootmgr_net
    global non_monté
    global EFI_MBR

    non_monté = "non"
    for j in range(0, len(table_efibootmgr_net)):   #---- for each EFI item of efibootmgr, search among all blkid for the same UUID
        #---------- initialise le poste de table_EFIsdx
        table_EFIsdx.append("...??...")
        rang_part = len (table_EFIsdx) -1


        #for i in range(0 , iblkid):     #---cherche égalité
        for i in range(0, len(table_blkid_nette)):

            #  table_efibootmgr_net[j][34:70] est l'UUID de la ligne de efibootmgr -v
            #============== si égalité entre les UUID
            if table_efibootmgr_net[j][34:70] == table_blkid_nette[i][13:49]:  # dans table_efi_nette, partUUID est de 13 à 49
                table_EFIsdx[rang_part] = table_blkid_nette[i][2:10]      # dans table_efi_nette, le device /dev/sdx est de 2 à 10
                break       #------- if found, stop equality search, sdx found, break loop
            # !!!!!!!!!!!! attention, it's possible that we do not find a unit (dismantled) and then table_EFIsdx[rang_part] still contains "...???..."

        if (table_EFIsdx[len(table_EFIsdx)-1] =="...??..."):
            non_monté = "oui"

        #============ end of table matching procedure ================================================================

#=======================================display procedure=================
def affichage():
    global ilignes_print
    global table_EFI_print
    global table_EFI_Entete
    global lignes_de_commentaire
    global table_commentaire
    global table_intermed
    global table_bootorder
    global table_efibootmgr_net
    global messages_ano_bootorder
    global EFI_MBR
    global table_lignes_affichees
    table_lignes_affichees = []
    messages_ano_bootorder = []



    # ------la table table_EFI_print contient les lignes à afficher concernant les lanceurs EFI --------------

    table_EFI_Entete = []   #-------------------- trois lignes d'entête dans  table_EFI_Entete
    table_EFI_Entete.append("                          table efibootmgr  ")
    table_EFI_Entete.append("   " + BootOrder[0:len(BootOrder) - 1])  # remove the line break to the right of the BootOrder string
    table_EFI_Entete.append("     rank      designation                    Launcher in ESP                     Partition UUID  ")

    ilignes_print = 0
    table_EFI_print = []
    for j in range(0, ilignes_EFI):

        ligne = table_efibootmgr_net[j][1:9] + "|" + table_efibootmgr_net[j][11:31] + "|" + str(table_EFIsdx[j]) + table_efibootmgr_net[j][72:107] \
                + "|" + table_efibootmgr_net[j][34:70] + "|>" + table_efibootmgr_net[j][104:107] + "<"

        table_EFI_print.append(ligne)
        ilignes_print = ilignes_print + 1


    #-------------------- lignes de boot composées, dans table_EFI_print de 0 à  ilignes_print exclu

    # ----on constitue une table des bootorders
    table_bootorder = []
    #   >BootOrder = "BootOrder: 0000,0001,0003,0008,0004,0007"   non reclassé
    inter_char = BootOrder  # ------- tiré de efibootmgr -v
    caracteres_a_remplacer = (',', '-', '!', '?', 'BootOrder: ')  # --- liste de chaines à remplacer "
    for r in caracteres_a_remplacer:        # pour tout élément "r" de la liste, le remplacer par un blanc
        inter_char = inter_char.replace(r, ' ')
    # inter_char est devenu  "0000 0001 0003 0008 0004 0007"   non reclassé, et sans virgules
    mots = inter_char.split()  # ----- mots est la liste (table) de bootorders

    for x in mots:
        table_bootorder.append(x)  # table_bootorder est la liste des rangs de boot
    # table bootorder est constituée

    #---------- pour que les lignes s'affichent dans l'ordre de BootOrder, on utilise une table intermédiaire
    #---------- dans laquelle on met table_EFI_print
    table_intermed = []
    table_intermed = table_EFI_print
    #======== ajout d'un argument de tri à droite de chaque ligne. C'est son rang dans BootOrder ou un numéro > 10 si n'est pas cité
    anonum = 99
    for i in range(0, len(table_intermed)):
        trouvé = "non"
        for j in range(0, len(table_bootorder)):
            if table_intermed[i][4:8] == table_bootorder[j]:
                trouvé = "oui"
                rangchar = "00000" + str(j)
                fin = len(rangchar)
                deb = fin - 5
                rangchar = rangchar[deb:fin]
                table_intermed[i] = table_intermed[i] + "    " + rangchar
                pass
        if trouvé != "oui":
            anonum = anonum + 1
            rangchar = "00000" + str(anonum)
            fin = len(rangchar)
            deb = fin - 5
            rangchar = rangchar[deb:fin]
            table_intermed[i] = table_intermed[i] + "    " + rangchar
        trouvé = "non"

    #---si on préfère classer par bootorder
    if bit_triEFI == 1:
        # ============= l'argument de tri est en fin de ligne, on trie
        for i in range (0,len(table_intermed)-1):
            fin1 = len(table_intermed[i])
            deb1 = fin1 - 5
            cle_i=table_intermed[i][deb1:fin1]
            for j in range (i+1, len(table_intermed)):
                fin2 = len(table_intermed[j])
                deb2=fin2 - 5
                cle_j=table_intermed[j][deb2:fin2]
                if (cle_j < cle_i):
                    tampon=table_intermed[i]
                    table_intermed[i]=table_intermed[j]
                    table_intermed[j]=tampon
                    fin1 = len(table_intermed[i])
                    deb1 = fin1 - 5
                    cle_i = table_intermed[i][deb1:fin1]



    #   la table table_intermed a alors le dessin suivant, triée selon l'argument de tri de 5 caractères qui est à droite
    #   Si la valeur de cet argument est supérieure à 00100, alors il s'agit d'un poste non cité dans BootOrder
    #   Boot0000|Refind MintUsb...|...??...\EFI\refind\refind_x64.efi....|b4f736db-41cf-5743-bebd-9c1f4340d126|>EFI<    00103

    #============ on peut maintenant remettre table_intermed dans table_EFI_print ===================
    table_EFI_print=table_intermed

    # searching for EFI items not mentioned in bootorder, we mark them with "?" on the left of the line
    # ?  Boot0000|Refind MintUsb...|...??...\EFI\refind\refind_x64.efi....|b4f736db-41cf-5743-bebd-9c1f4340d126|>EFI<    00103
    postes_efi_en_trop="non"
    for i in range (0,len(table_EFI_print)):
        # verif que ce numéro est cité dans bootorder
        fin=len(table_EFI_print[i])
        deb=fin - 5
        arg_tri=table_EFI_print[i][deb:fin]

        if (arg_tri > "00099"):
            table_EFI_print[i] = " ? " + table_EFI_print[i]
            postes_efi_en_trop = "oui"
        else:
            table_EFI_print[i] = "   " + table_EFI_print[i]

    if (postes_efi_en_trop == "oui"):
        table_EFI_print.append('   "?" on the left of a row indicates that this item is not quoted in BootOrder')

    #-- recherche si postes bootorder sans poste EFI
    messages_ano_bootorder = []
    for j in range(0, len(table_bootorder)):  # pour chaque poste de bootorder
        indic_trouve = "non"

        for k in range(0, len(table_EFI_print)):  # pour chaque ligne de table table_EFI_print
            if table_bootorder[j] == table_EFI_print[k][7:11]:
                indic_trouve = "oui"
                break
            if (indic_trouve == "oui") :
                break

        if indic_trouve == "non":
            messages_ano_bootorder.append("       Le BootOrder " + table_bootorder[j] + " n'a pas de ligne EFI")

    if (len( messages_ano_bootorder) != 0):
        for j in range (0,len( messages_ano_bootorder)):
            table_EFI_print.append(messages_ano_bootorder[j])


    if (non_monté == "oui"):
        #==== ce peut être un poste MBR incongru
        table_EFI_print.append('   "...??..."' + " reports that this line does not point to a launcher in an accessible EFI partition")

    if printer == "oui":
        print("-------table EFI finale-------")
        for j in range(0 , len(table_EFI_print)):
            print (table_EFI_print[j])


    #--------------------  table_EFI_print est reclassée -----------------------------
    #--------------- sinon (si chk_triEFI = false) , on laisse   table_EFI_print en l'état


    #------------------------ écriture de l'entête
    separateur="oui"
    resultat.tag_config('black', foreground='black')  # <-- tag pour changer la couleur du texte avec tag 'black' en noir.
    resultat.tag_config('red', foreground='red')  # <--  tag pour changer la couleur du texte avec tag 'red' en rouge.
    resultat.tag_config('blue', foreground='blue')  # <--  tag pour changer la couleur du texte avec tag 'blue' en bleu
    yadesmbr="non"


    for j in range (0,len(table_EFI_Entete)):
        ligne = table_EFI_Entete[j]
        resultat.insert("insert", ligne + "\n")

    j = 0

    while j < len(table_EFI_print):
        fin1 = len(table_EFI_print[j])
        deb1 = fin1 - 5
        cle_tri = table_EFI_print[j][deb1:fin1]
        ligne = table_EFI_print[j]
        EFI_MBR=ligne[107:110]
        ligne2=ligne.replace("\\", "/")   #  le caractère \ seul est un échappement. Il faut le doubler
        ligne=ligne2

        ligne = ligne[:113]

        if  (ligne[3:7] == "Boot"):
            if (ligne[0:3]==" ? "):
            #if (cle_tri > "00099"):  # non cité dans bootorder -> bootorder en rouge
                resultat.insert("insert", ligne[0:3], 'red')
            else:
                resultat.insert("insert", ligne[0:3], 'black')
            #fin else

            #Bootorder
            if (cle_tri > "00099"):    # non cité dans bootorder -> bootorder en rouge
                resultat.insert("insert", ligne[3:11], 'red')
            else:
                resultat.insert("insert", ligne[3:11], 'black')
            #fin else

            #libellé toujours en noir
            #resultat.insert("insert", ligne[11:30], 'black')
            resultat.insert("insert", ligne[11:33], 'black')

            if (ligne[33:41] == "...??..."):
                resultat.insert("insert", ligne[33:42], 'red')
            else:
                resultat.insert("insert", ligne[33:42], 'black')
            #end else

            # chemin EFI
            if (ligne[33:41] == "...??..."):
                resultat.insert("insert", ligne[42:72], 'red')
            else:
                resultat.insert("insert", ligne[42:72], 'black')
             #fin else

            #UUID
            if (ligne[33:41] == "...??..."):
                resultat.insert("insert", ligne[72:len(ligne)], 'red')
            else:
                resultat.insert("insert", ligne[72:len(ligne)], 'black')
             #fin else

            #passage à la ligne
            resultat.insert("insert", '\n')

            table_lignes_affichees.append(ligne)

        else:   # ligne non "   Boot..."
            # --- sinon, ce sont des lignes de commentaires
            if (separateur == "oui"):
                separateur = "non"
                resultat.insert("insert", "   ------------------------------------------------------------------------------------------------------", 'blue', '\n')
            resultat.insert("insert", ligne, 'blue', '\n')
        #fin else

        if yadesmbr == "oui":
            ligne2 = '   MBR en rouge signale un lanceur "MBR" et non EFI. Problème probable de partition sur ce disque'
            resultat.insert("insert", ligne2, 'blue', "\n")

        if printer == "oui":
            for i in range(0, 3):
                ligne = table_EFI_Entete[i] + "\n"
                print(ligne)
            print("--------------------------------------------------------------------------")
            for i in range(1, len(table_EFI_print)):
             print(table_EFI_print[i])

        j = j + 1
    #fin while


    if (separateur == "oui"):  # ========= cas où aucune ligne de commentaires n(a été écrite jusque là, le séparateur nn plus
        separateur = "non"
        resultat.insert("insert", "   ------------------------------------------------------------------------------------------------------", 'blue',
                        '\n')

    if (verbeux=="1") :
        # -----------------affichage du commentaire
        for i in range (0,len(table_commentaire)):
            ligne = "  " + table_commentaire[i] + "  "
            #resultat.insert("insert", ligne + "\n")
            idx1=str.find(ligne, "<")  #  idx1 est de type int
            idx2=str.find(ligne, ">")
            if (idx1 >= 0) and (idx2 >= 0) :
                resultat.insert("insert", ligne[0:(idx1-1)],'blue', ligne [(idx1+1):idx2], 'red', ligne[(idx2 +1):len(ligne)],'blue', "\n")
            else:
                resultat.insert("insert", ligne + "\n")

    if printer == "oui":
        for i in range(0 , len(table_commentaire)):
            print(table_commentaire[i])

#======================================fin de la procédure d'affichage=======================================

#------------------------------ procédure déclenchée quand on coche la case choix de l'ordre de tri ---------
def chk_triEFI():
    global bit_triEFI
    if bit_triEFI == 0:
        chk_triEFI.select()
        bit_triEFI = 1
    else:
        chk_triEFI.deselect()
        bit_triEFI = 0
    faire_ou_refaire_le_boulot()
# -------------------------------fin de traitement du clic sur cocher pour trier EFI-------------------------
# -------------------------------switches from verbose display to reduced display and reverse-------------------------
def basculer():
    global verbeux
    global window_large
    global LargeurScreen
    global HauteurScreen
    global largeur_fenetre
    global hauteur_fenetre
    global coin_x
    global coin_y
    global bit_bouton
#__________________________________________________ici
    if bit_bouton == 1 :
        if verbeux=="1":
            verbeux="0"
            Bouton_verbeux.config(text="more info ?")
            largeur_fenetre = 930
            hauteur_fenetre = 420
        else:
            verbeux="1"
            Bouton_verbeux.config(text="less info ?")
            largeur_fenetre = 1024
            hauteur_fenetre = 600
    #bit_bouton=0
    recadrer()

#------------------------------ procédure déclenchée quand bouton recadrer ---------
def recadrer():
    global verbeux
    global window_large
    global LargeurScreen
    global HauteurScreen
    global largeur_fenetre
    global hauteur_fenetre
    global coin_x
    global coin_y
    marge=37
#__________________________________________________ici


    window.geometry('%dx%d+%d+%d' % (largeur_fenetre, hauteur_fenetre, coin_x, coin_y))

    #resultat.place(x=0, y=30, width=largeur_fenetre, height=hauteur_fenetre - marge)


    #--------------------------------------positionnement de resultat à 5 pix sous les boutons
    delta=Bouton_quitter.winfo_height() + 5

    resultat.place(x=0, y=delta, width=largeur_fenetre, height=(hauteur_fenetre - marge))




    retirer=70

    place_bouton=  (largeur_fenetre - retirer - Bouton_quitter.winfo_width() - Bouton_actualise.winfo_width())/6

    x1 = place_bouton
    Bouton_creat.place(x=x1, y=0)

    x1 = (place_bouton*2)
    Bouton_modif.place(x=x1, y=0)

    x1 =place_bouton*3
    Bouton_suppr.place(x=x1, y=0)

    x1 = place_bouton*4
    Bouton_order.place(x=x1, y=0)

    x1=place_bouton*5
    Bouton_verbeux.place(x=x1, y=0)

    x1=place_bouton*6
    chk_triEFI.place(x=x1, y=0)

    x1= largeur_fenetre - 95
    Bouton_quitter.place(x=x1, y=0)


    faire_ou_refaire_le_boulot()

#-------------------------------fin de traitement du clic sur bouton recadrer-------------------------



#----------------------- procédure globale faisant tout le travail-------------------------------------------
def faire_ou_refaire_le_boulot():
    global table_blkid_brute
    global table_blkid_nette
    global table_efibootmgr_net
    global table_EFIsdx
    global table_intermed
    global messages_ano_bootorder
    global iblkid
    global ilignes_EFI
    global BootOrder
    global EFI_MBR
    global global_booCurrent


    table_blkid_brute = []
    table_blkid_nette = []
    table_efibootmgr_net = []
    table_EFIsdx = []
    table_intermed = []
    messages_ano_bootorder = []
    iblkid = 0
    ilignes_EFI = 0
    BootOrder = ""
    EFI_MBR = "EFI"



    #instruction1 = " blkid > " + dir_travail + "/blkid.txt"
    #instruction2 = " efibootmgr -v > " + dir_travail + "/efiboot.txt"
    instruction1 = " blkid > blkid.txt"
    instruction2 = " efibootmgr -v > efiboot.txt"


    #----------------------va demander le mot de passe au terminal une seule fois------
    code_retour = os.system("sudo" + instruction1 + "&&" + instruction2)
    if code_retour != 0:
        print("crash blkid or efibootmgr -v with return code =", code_retour)

    resultat.delete("1.0", "end")
    resultat.insert("insert", "   current boot = " + global_booCurrent)

    extrac_dev_partUUID_de_blkid()
    extract_efibootmgr()
    croisement_efibootmgr_blkid_selon_UUID()
    affichage()

    # -------------------------------fin faire_ou_refaire_le_boulot _______________________

#-------------------- fin de la procédure globale de traitement ---------------------------


#====================================================================================================================

# ------ allocation en mémoire d'un objet tk.tk() qu'on nomme window et qui a les propriétés et méthodes de tk.tk()
#window = tk.Tk()
window.configure(bg="blue")
# ---------------------------------------------------ici
window.resizable(1, 1)


# ------ allocation d'un cadre qui sera ancré dans window et portera les autres objets
zone = tk.Frame(window, bg='light gray')


# ----------------------------------------------------------------ici
zone.pack(padx=1, pady=1, fill='both', expand=1)

# ------ bouton lançant l'actualisation du texte
Bouton_actualise = tk.Button(zone, activebackground="red", bg="cyan", fg="black", command=faire_ou_refaire_le_boulot, width=8)
Bouton_actualise.config(text="Refresh")
Bouton_actualise.pack(padx=2, pady=8, side="top")
Bouton_actualise.place(x=1, y=1)
Bouton_actualise.config(height=1, width=10)

if verbeux == "1" :
    Bouton_verbeux = tk.Button(zone, width=10, text="less info ??", command=basculer,relief="flat")
else :
    Bouton_verbeux = tk.Button(zone, width=10, text="more info ??", command=basculer,relief="flat")#

Bouton_verbeux.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black')


# ---------------- bouton modif : lance le module ouvrant la fenêtre modif

def popup_creat():
    import tkinter as tk
    #import tkinter.font as tkf
    import tkinter.ttk as ttk
    index_combo=0
    coin_x=window.winfo_x()  # position de la fenêtre mère
    coin_y=window.winfo_y()   # position de la fenêtre mère
    largeur_wincourante=800
    hauteur_wincourante=150
    win_creat  = tk.Toplevel()		  # Popup -> Toplevel()
    win_creat.transient(window)
    win_creat .title('creation')
    # calcule position x, y

    x = coin_x + (int(largeur_fenetre)/2)  - (int(largeur_wincourante) / 2)
    y = coin_y + (int(hauteur_fenetre)/2) -(int(hauteur_wincourante) / 2)
    win_creat .geometry('%dx%d+%d+%d' % (largeur_wincourante, hauteur_wincourante, x, y))
    win_creat .config(bg="cyan")

    zone1 = tk.Frame(win_creat, bg='light blue')
    zone1.pack(padx=1, pady=1, fill='both', expand=1)
    table_partitions_EFI=[]
    global volume
    volume=""
    global partition
    partition=""
    global libellé_EFI
    libellé_EFI=""
    global path_EFI
    path_EFI = ""
    global commande

    # =============================== commande lsblk et extraction des partitions EFI =================
    #def liste_part_EFI():
    instruction = "lsblk -i -o +PARTTYPE   > " + dir_travail + "/lsblk.txt"
    code_retour = os.system("sudo " + instruction)
    if code_retour != 0:
        print("crash sudo lsblk -i -o +PARTTYPE  with return code =", code_retour)
    fichier_partitions = open("lsblk.txt", 'r')
    table_partitions = fichier_partitions.readlines()
    fichier_partitions.close()  # ferme le fichier fich_efiboot

    os.remove(dir_travail + "/lsblk.txt")  # -------------------on n'en aura plus besoin
    # =================================fin commande lsblk et extraction des partitions EFI ======
    # ================================= extraction volume /dev/sdx  si EFI
    for i in range (0,len(table_partitions)):
        #=========== rechercher partitions de type EFI.

        # "c12a7328-f81f-11d2-ba4b-00a0c93ec93b" est le type d'UUID "EFI"
        trouve_EFI= str.find(table_partitions[i],"c12a7328-f81f-11d2-ba4b-00a0c93ec93b")   #   str.find retourne -1 si non trouvé

        if (trouve_EFI != -1):   #========= si on a trouvé en bout de ligne "BIOS ou "EFI"
            table_partitions_EFI.append(("/dev/" + table_partitions[i][2:6]))

    # ================================= /dev/sdx  si EFI  mis dans la table table_partitions_EFI

    # ===================================== un_Device_selecte appelée si événement ComboboxSelected de combo_device.bind
    def un_Device_selecte(eventobject):
        change_choix_device()  # ========= action effectuée suite à cet événement
    # ================================= fin =================================================================================

    def change_choix_device():
        global index_combo
        global volume
        global partition
        global libellé_EFI
        global path_EFI
        global commande
        label_titre0['text'] = ""
        volume=combo_device.get()[0:8]
        partition=combo_device.get()[8:9]
        #print ("------------------------------" +  libellé_EFI)
        commande="sudo efibootmgr --create --disk "+ volume +" --part "+ partition + " --label " + '"' + libellé_EFI.rstrip(" ") + '"' + " --loader "+ path_EFI.rstrip(" ")
        inter=commande.replace('\\','/')
        commande=inter
        label_commande.configure(text=commande)
        index_combo = combo_device.current()

    def annul_creat():
        win_creat.destroy()

    annuler = tk.Button(zone1, activebackground = "red", bg = "cyan", fg = "black", command = annul_creat, width = 9)
    annuler.config(text="Cancel")
    annuler.pack(padx=2, pady=8, side="top")
    annuler.place(x=674, y=1)
    annuler.config(height=1, width=12)


    def executer_commande():
        global commande
        global volume
        global partition
        global libellé_EFI
        global path_EFI
        if volume=="":
            label_titre0['text'] ="You forgot to choose the partition"
            return
        if (libellé_EFI == "Libellé de l'EFI") or (libellé_EFI == ""):
            label_titre0['text'] ="You forgot the designation of the EFI"
            return
        if (path_EFI == "/EFI/") or (path_EFI == ""):
            label_titre0['text'] = "You forgot the path to the EFI"
            return
        commande = "sudo efibootmgr --create --disk " + volume + " --part " + partition + " --label " + '"' + libellé_EFI.rstrip(" ") + '"' + " --loader " + path_EFI.rstrip(" ")
        #print ("la commande va être """ + commande )
        code_retour = os.system(commande)
        if code_retour != 0:
            commande=commande + blancs
            print("plantage " + commande[0:30] + "... avec code retour =", code_retour)
            label_titre0['text']="plantage " + commande[0:30] + " avec code retour =" + str(code_retour)
        else:
            faire_ou_refaire_le_boulot()
            win_creat.destroy()

    # ================================ bouton executer et quitter ===================================
    executer = tk.Button(zone1, activebackground = "red", bg = "cyan", fg = "black", command = executer_commande, width = 9)
    executer.config(text="Run & Exit")
    executer.pack(padx=2, pady=8, side="top")
    executer.place(x=1, y=1)
    executer.config(height=1, width=12)
    # ================================= fin bouton executer et quitter ================================

    # ============================ et construit la liste déroulante des partitions possibles ===========================
    combo_device = ttk.Combobox(zone1, width=10, values=table_partitions_EFI)
    combo_device.place(x=10,y=60)
    combo_device.current(index_combo)
    combo_device.bind("<<ComboboxSelected>>", un_Device_selecte)  # ==action "un_pays_selecte" quand uévénement ComboboxSelected
    # ============================ fin liste partitions possibles ===========================
    label_titre0 = tk.Label(zone1, text="", bg='light blue', fg='red', width=66)
    label_titre0.place(x=135, y=0)
    label_titre1 = tk.Label(zone1, text="ESP", bg='light blue', fg='black', width=10)
    label_titre1.place(x=10, y=35)
    label_titre2 = tk.Label(zone1, text="Label of the EFI", bg='light blue', fg='black', width=20)
    label_titre2.place(x=205, y=35)
    label_titre3 = tk.Label(zone1, text="path of the l'EFI", bg='light blue', fg='black', width=20)
    label_titre3.place(x=540, y=35)
    label_titre4 = tk.Label(zone1, text="Command that will be executed", bg='light blue', fg='black', width=30)
    label_titre4.place(x=270, y=90)

    value1 = tk.StringVar(zone1)
    value1.set("Label of the EFI")
    entree1 = tk.Entry(zone1, textvariable=value1, width=20)
    entree1.pack()
    #entree1.place(x=195,y=58)
    entree1.place(x=230, y=58)

    def change_libel_chemin(event):
        global libellé_EFI
        global volume
        global partition
        global commande
        label_titre0['text'] =""
        libellé_EFI=entree1.get()
        if len(libellé_EFI) > 20 :
            label_titre0.configure(text="La longueur du libellé du poste EFI est limitée à 20 caractères xxx")
            #value1.set(libellé_EFI[:20])
            value1.set(libellé_EFI[:20])
            return

        commande="sudo efibootmgr --create --disk "+ volume +" --part "+ partition + " --label " + '"' + libellé_EFI.rstrip(" ") + '"' + " --loader "+ path_EFI.rstrip(" ")
        inter=commande.replace('\\','/')
        commande=inter
        label_commande.configure(text=commande)

    # On lie la fonction à l'Entry
    # La fonction sera exécutée à chaque fois que l'utilisateur appuie sur "Entrée"
    entree1.bind("<KeyRelease>", change_libel_chemin)

    value2 = tk.StringVar(zone1)
    value2.set("/EFI/")
    entree2 = tk.Entry(zone1, textvariable=value2, width=30)
    entree2.pack()
    entree2.place(x=500,y=58)

    def change_path_EFI(event):
        global libellé_EFI
        global volume
        global partition
        global path_EFI
        global commande
        label_titre0['text'] = ""
        path_EFI=entree2.get()



        # ici

        # if len(path_EFI) > 30 :
        if len(path_EFI) > 40:
            label_titre0.configure(text="La longueur du chemin du poste EFI est limitée à 40 caractères")
            #value1.set(libellé_EFI[:20])
            value2.set(path_EFI[:40])
            return

        commande="sudo efibootmgr --create --disk "+ volume +" --part "+ partition + " --label " + '"' + libellé_EFI.rstrip(" ") + '"' + " --loader "+ path_EFI.rstrip(" ")
        inter=commande.replace('\\','/')
        commande=inter
        label_commande.configure(text=commande)

    # On lie la fonction à l'Entry
    # La fonction sera exécutée à chaque fois que l'utilisateur appuie sur une touche
    entree2.bind("<KeyRelease>", change_path_EFI)
    device_choisi = combo_device.get()
    label_commande = tk.Label(zone1, text=device_choisi, bg='ivory', fg='black', width=97)
    label_commande.place(x=10, y=115)

    win_creat.transient(window) 	  # Réduction popup impossible
    win_creat.grab_set()		  # Interaction avec fenetre window impossible
    window.wait_window(win_creat)   # Arrêt script principal



def popup_modif():
    import tkinter as tk
    #import tkinter.font as tkf
    import tkinter.ttk as ttk
    global table_efibootmgr_net
    global table_bootnum
    global table_lignes_affichees
    global commande
    global partition
    global bootnum
    global volume
    global global_bootorder
    global table_bootorder
    global Poste_libre

    coin_x=window.winfo_x()  # position de la fenêtre mère
    coin_y=window.winfo_y()   # position de la fenêtre mère
    largeur_wincourante=910
    hauteur_wincourante=205
    win_modif = tk.Toplevel()		  # Popup -> Toplevel()
    win_modif.transient(window)
    win_modif.title('modif')
    # calcul position x, y
    x = coin_x + (int(largeur_fenetre)/2)  - (int(largeur_wincourante) / 2)
    y = coin_y + (int(hauteur_fenetre)/2) -(int(hauteur_wincourante) / 2) + 100
    win_modif.geometry('%dx%d+%d+%d' % (largeur_wincourante, hauteur_wincourante, x, y))
    win_modif.config(bg="cyan")
    commande = "pas de commande"
    zefi = table_lignes_affichees[0]
    numposte = 0
    Boot_a_modif = zefi[7:11]
    bootnum = zefi[7:11]
    libellé_EFI = zefi[12:32]
    volume = "/" + zefi[33:42]

    idx = str.find(zefi.casefold(), ".efi")
    idx = idx + 4
    chemin = zefi[41:idx]

    for i in range (0,len(table_lignes_affichees)):
        ligne1=table_lignes_affichees[i]
        ligne2=ligne1.replace('|','   ')
        table_lignes_affichees[i]=ligne2

    zone5 = tk.Frame(win_modif, bg='light blue')
    zone5.pack(padx=1, pady=1, fill='both', expand=1)
    index_combo = 0

    def change_choix_boot():
        global index_combo
        global volume
        global partition
        global libellé_EFI
        global path_EFI
        global commande
        global bootnum
        global chemin
        global numposte
        global table_bootorder
        global table_bootorder_projet

        zefi = combo_boot.get()
        numposte = 0
        bootnum = zefi[7:11]
        libellé_EFI = zefi[14:34]

        idx = str.find(zefi.casefold(), ".efi")
        idx = idx + 4

# ici

        # chemin = zefi[41:idx]
        chemin = zefi[45:idx]
        label_valeur_ESP.configure(text=bootnum)
        change_libel_chemin(libellé_EFI, chemin)
        value1.set(libellé_EFI.rstrip(" "))
        value2.set(chemin)

        return
    #---------------------------------------------------------------------------------
    def un_boot_selecte(eventobject):
        change_choix_boot()  # ========= action effectuée suite à cet événement
    # ================================= fin =============================================================================

    # ========================================= executer commande de suppression ========================================
    def executer_commande():
        global commande1
        global commande2
        global commande3
        global global_bootorder
        global volume
        if volume == "/...??...":
            label_anomalie.configure(text="Attention ! on ne peut pas renommer ce poste car sa localisation est inconnue")
            return

        #print("BootOrder avant ", global_bootorder)
        code_retour = 0
        code_retour = os.system(commande1)
        if code_retour != 0:
            commande1=commande1 + blancs
            print("plantage " + commande1[0:30] + "... avec code retour =", code_retour)
            label_anomalie['text']="plantage " + commande1[0:30] + " avec code retour =" + str(code_retour)
            return
        else:
            print ("commande >" + commande1 + "< exécutée")
            faire_ou_refaire_le_boulot()
            print("BootOrder apres ", global_bootorder)
            code_retour = os.system(commande2)
            if code_retour != 0:
                commande2 = commande2 + blancs
                print("plantage " + commande2[0:30] + "... avec code retour =", code_retour)
                label_anomalie['text'] = "plantage " + commande2[0:30] + " avec code retour =" + str(code_retour)
                return
            else:
                print("commande >" + commande2 + "< exécutée")
                faire_ou_refaire_le_boulot()
                print ("BootOrder apres ",global_bootorder)
                code_retour = os.system(commande3)
                if code_retour != 0:
                    commande3 = commande3 + blancs
                    print("plantage " + commande3[0:30] + "... avec code retour =", code_retour)
                    label_anomalie['text'] = "plantage " + commande3[0:30] + " avec code retour =" + str(code_retour)
                    return
                else:
                    print("commande >" + commande3 + "< exécutée")
                    faire_ou_refaire_le_boulot()
                    print("BootOrder apres ", global_bootorder)


        win_modif.destroy()
    # ================================== fin executer commande de suppression ===========================================
    def annuler_modif():
        win_modif.destroy()
    #=============================== bouton annuler =====================================================================
    annuler = tk.Button(zone5, activebackground = "red", bg = "cyan", fg = "black", command = annuler_modif, width = 9)
    annuler.config(text="Cancel")
    annuler.pack(padx=2, pady=8, side="top")
    place=largeur_wincourante - 129
    annuler.place(x=674, y=1)
    annuler.place(x=place, y=1)
    annuler.config(height=1, width=12)
    #================================ fin bouton annuler ================================================================

    # ================================ bouton executer et quitter ===================================
    executer = tk.Button(zone5, activebackground = "red", bg = "cyan", fg = "black", command = executer_commande, width = 9)
    executer.config(text="Run & Exit")
    executer.pack(padx=2, pady=8, side="top")
    executer.place(x=1, y=1)
    executer.config(height=1, width=12)
    # ================================= fin bouton executer et quitter ================================

    # ============================ construit la liste déroulante des EFI presents ===========================
    label_anomalie = tk.Label(zone5, text="", bg='light blue', fg='red', width=78)
    label_anomalie.place(x=135, y=0)

    label_titre2 = tk.Label(zone5, text="choose the item to edit", bg='light blue', fg='black', width=30)
    label_titre2.place(x=300, y=20)

    #combo_boot = ttk.Combobox   table_lignes_affichees
    combo_boot = ttk.Combobox(zone5, width=100, values=table_lignes_affichees)
    combo_boot.place(x=40,y=45)
    combo_boot.current(index_combo)
    combo_boot.bind("<<ComboboxSelected>>", un_boot_selecte)  # ==action "un_pays_selecte" quand uévénement ComboboxSelected
    # ============================ fin liste partitions possibles ============================================

    label_titre_ESP = tk.Label(zone5, text="Boot", bg='light blue', fg='black', width=4)
    label_titre_ESP.place(x=90, y=80)
    label_valeur_ESP = tk.Label(zone5, text="----", bg='ivory', fg='black', width=4)
    label_valeur_ESP.place(x=130, y=80)

    label_libel_ESP = tk.Label(zone5, text="Libellé ", bg='light blue', fg='black', width=8)
    label_libel_ESP.place(x=165, y=80)

    label_chemin_ESP = tk.Label(zone5, text="path   ", bg='light blue', fg='black', width=8)
    label_chemin_ESP.place(x=400, y=80)


    value1 = tk.StringVar(zone5)
    value1.set("------------------------------")
    entree1 = tk.Entry(zone5, textvariable=value1, width=20, bg='ivory')
    entree1.pack()
    entree1.place(x=230,y=78)

    value2 = tk.StringVar(zone5)
    value2.set("------------------------------")
    entree2 = tk.Entry(zone5, textvariable=value2, width=39, bg='ivory')
    entree2.pack()
    entree2.place(x=470,y=78)

    def change_libel_chemin(libellé_EFI,chemin):
        global label_libel_ESP_valeur
        global volume
        global partition
        global commande
        global commande1
        global commande2
        global commande3
        global bootnum
        #global chemin
        #global libellé_EFI
        global table_bootorder
        global global_bootorder
        zefi=combo_boot.get()
        commande2=""
        if len(libellé_EFI) > 20 :
            label_anomalie.configure(text="The length of the EFI item label is limited to 20 characters")
            value1.set(libellé_EFI[:20])
            return




        # ici
        # if len(chemin) > 30 :
        if len(chemin) > 40:
            label_anomalie.configure(text="The length of the EFI item label is limited to 40 characters")
            value2.set(chemin[:30])
            return
        # -------------------------------------------------------------------------
        bootnum = zefi[7:11]
        #idx = str.find(zefi.casefold(), ".efi")
        #idx = idx + 4
        #chemin= zefi[41:idx]
        volume = "/" + zefi[37:45]
        if volume == "/...??...":
            label_anomalie.configure(text="we cannot rename this item because its location is unknown")
            return

        label_anomalie.configure(text="")
        commande1 = "sudo efibootmgr -b " + bootnum + " -B"
        label_commande.configure(text=commande1)
        commande2 = "sudo efibootmgr -c -d " + volume[0:8] + " -p " + volume[8:9] + ' -L "' + libellé_EFI.rstrip(" ") + '" -l ' + chemin.rstrip(" ")
        label_commande2.configure(text=commande2)

        table_bootorder_projet = []
        for i in range(0, len(table_bootorder)):
            if table_bootorder[i] != bootnum:
                table_bootorder_projet.append(table_bootorder[i])

        # recherche du poste disponible : dans table_bootorder_projet, le plus petit order non compris dans la table
        # postes possibles ; C'est celui que prend efibootmgr quand il fait un nouveau poste
        table_bootorder_possibles = []
        valeurs_possibles = '0000', '0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008', '0009', '000A', '000B', '000C', '000D', '000E', '000F'
        for a in valeurs_possibles:
            table_bootorder_possibles.append(a)

        #table_bootorder_restant = []
        for i in range(0, len(table_bootorder_projet)):
            for j in range(0, len(table_bootorder_possibles)):
                if table_bootorder_projet[i] == table_bootorder_possibles[j]:
                    table_bootorder_possibles[j] = "----"

        for i in range(0, len(table_bootorder_possibles)):
            if table_bootorder_possibles[i] != "----":
                Poste_libre = table_bootorder_possibles[i]
                break
        # ========poste_libre est le numero de bootorder du poste qui sera créé
        # ========dans la liste BootOrder, il faut le placer en position du poste qui a été supprimé
        commande2 = "sudo efibootmgr -c -d " + volume[0:8] + " -p " + volume[8:9] + ' -L "' + libellé_EFI.rstrip(" ") + '" -l ' + chemin.rstrip(" ")
        label_commande2.configure(text=commande2)
        #===== recherche dans BootOrder du rang du poste qui va être renommé (rang avant suppression du poste)
        rang_futur_du_poste_cree=0
        for i in range (0,len(table_bootorder)):
            if bootnum == table_bootorder[i]:
                rang_futur_du_poste_cree=i
                break

        #print ("====rang poste a creer >" + str(rang_futur_du_poste_cree))


        #======= table_bootorder est la liste des postes de BootOrder avant création du nouveau poste.
        #======= bootnum est la clé xxxx du poste créé bootxxxx, que efibootmgr place en tête de liste
        #======= du nouveau BootOrder créé après création du nouveau poste xxxx,0007,0003...
        table_bootorder_projet_fin=[]
        # ========== on reconduit les postes avant le nouveau, on injecte le nouveau, et on reconduit les suivants

        #print ("====Clé bootorder libre >" + Poste_libre)
        #print ("rang poste a creer >" + str(rang_futur_du_poste_cree))
        #print ("===table projet avant insert>",table_bootorder_projet)

        indic_injection = "non"  #========== dans le cas où c'est le dernier poste qui est modifié, on ne l'atteindra pas
        for i in range (0,len(table_bootorder_projet)):
            if i < rang_futur_du_poste_cree:
                table_bootorder_projet_fin.append(table_bootorder_projet[i])
            else:
                if i==rang_futur_du_poste_cree :
                    table_bootorder_projet_fin.append(Poste_libre)             #================ injection
                    indic_injection = "oui"   #============ l'injection du poste modifié a eu lieu
                    table_bootorder_projet_fin.append(table_bootorder_projet[i]) #===== reconduction au rang + 1
                else:
                    #===
                    table_bootorder_projet_fin.append(table_bootorder_projet[i])
                    #================ reconduction
        if indic_injection == "non" :     #========== c'est le cas où le poste modifié est en fin de liste
            #print("ajoute >" + Poste_libre + "<")
            table_bootorder_projet_fin.append(Poste_libre)



        commande3="sudo efibootmgr -o "

        # ========== fabrication BootOrder au bout de "sudo efibootmgr -o " par ajout du premier poste puis de "," + poste pour les suivants
        for i in range (0,len(table_bootorder_projet_fin)):
            if i==0:
                commande3 = commande3 + str(table_bootorder_projet_fin[i])          # ====== premier poste non précédé de virgule
            else:
                commande3 = commande3 + "," +str (table_bootorder_projet_fin[i])
        label_commande3.configure(text=commande3)

        #print ("=======commande3>" +commande3 + "<" )

    def chemin_ou_libel_a_ete_modifie(event):
        libellé_EFI = entree1.get()
        chemin = entree2.get()
        change_libel_chemin(libellé_EFI, chemin)

    # On lie la fonction aux deux Entry. La fonction est exécutée à chaque fois que l'utilisateur appuie sur une touche sur entree1 ou entree2
    entree1.bind("<KeyRelease>", chemin_ou_libel_a_ete_modifie)
    entree2.bind("<KeyRelease>", chemin_ou_libel_a_ete_modifie)
#=================================================================================================================================
    label_titre4 = tk.Label(zone5, text="Commands that will be executed", bg='light blue', fg='black', width=30)
    label_titre4.place(x=275, y=110)

    label_commande = tk.Label(zone5, text="Command that will be executed", bg='ivory', fg='black', width=111)
    label_commande.place(x=10, y=135)

    label_commande2 = tk.Label(zone5, text="Command that will be executed", bg='ivory', fg='black', width=111)
    label_commande2.place(x=10, y=155)

    label_commande3 = tk.Label(zone5, text="Command that will be executed", bg='ivory', fg='black', width=111)
    label_commande3.place(x=10, y=175)

    #=========initialisation===============
    boot_choisi = combo_boot.get()
    Boot_a_suppr = combo_boot.get()[3:12]
    commande = "sudo efibootmgr -b " + Boot_a_suppr[4:9] + " -B"
    label_commande.configure(text=commande)
#======================================================================
    zefi = table_lignes_affichees[0]

    numposte = 0
    bootnum = zefi[7:11]
    Boot_a_modif = bootnum
    libellé_EFI = zefi[14:31]
    idx = str.find(zefi.casefold(), ".efi")
    if idx ==-1 :
        idx = str.find(zefi, ".EFI")


    idx = idx + 4
    chemin = zefi[45:idx]


    # ====str.find(zefi.casefold(),".efi")
    # print ("zefi=" + zefi + "<")
    # print ("zefi=01234567890123456789012345678901234567890123456789")


    path_EFI = chemin
    volume = "/" + zefi[37:46]

    if volume == "/...??...":
        label_anomalie.configure(text="we cannot rename this item because its location is unknown")
        return
    else:
        label_anomalie.configure(text="")
        commande1 = "sudo efibootmgr -b " + bootnum + " -B"
        label_commande.configure(text=commande1)

        commande2 = "sudo efibootmgr -c -d " + volume[0:8] + " -p " + volume[8:9] + ' -L "' + libellé_EFI.rstrip(" ") + '" -l ' + chemin.rstrip(" ")

        label_commande2.configure(text=commande2)

    libellé_EFI=libellé_EFI.rstrip(" ")
    chemin=chemin.rstrip(" ")

    value1.set(libellé_EFI)
    value2.set(chemin)
    label_valeur_ESP.configure(text=bootnum)

    change_libel_chemin(libellé_EFI, chemin)


    win_modif.transient(window) 	  # Réduction popup impossible
    win_modif.grab_set()		  # Interaction avec fenetre window impossible
    window.wait_window(win_modif)   # Arrêt script principal



    # ===================================== un_Device_selecte appelée si événement ComboboxSelected de combo_device.bind



#=========================================== proc de suppression d'un poste EFI ===============
def popup_suppr():
    import tkinter as tk
    #import tkinter.font as tkf
    import tkinter.ttk as ttk
    global table_efibootmgr_net
    global table_bootnum
    global table_lignes_affichees
    global commande
    commande=""
    coin_x=window.winfo_x()  # position de la fenêtre mère
    coin_y=window.winfo_y()   # position de la fenêtre mère
    largeur_wincourante=800
    hauteur_wincourante=150
    win_suppr = tk.Toplevel()		  # Popup -> Toplevel()
    win_suppr.transient(window)
    win_suppr.title('suppression')

    # calcul position x, y
    x = coin_x + (int(largeur_fenetre)/2)  - (int(largeur_wincourante) / 2)
    y = coin_y + (int(hauteur_fenetre)/2) -(int(hauteur_wincourante) / 2) + 100
    win_suppr.geometry('%dx%d+%d+%d' % (largeur_wincourante, hauteur_wincourante, x, y))
    win_suppr.config(bg="cyan")

    table_bootnum = []
    for i in range (0,len(table_lignes_affichees)):
        ligne1=table_lignes_affichees[i]
        ligne2=ligne1.replace('|','   ')
        table_lignes_affichees[i]=ligne2

    index_combo=1

    zone2 = tk.Frame(win_suppr, bg='light blue')
    zone2.pack(padx=1, pady=1, fill='both', expand=1)
    #sudo efibootmgr - b 0014 - B
    def change_choix_boot():
        global index_combo
        global volume
        global partition
        global libellé_EFI
        global path_EFI
        global commande
        global table_bootnum
        # sudo efibootmgr --create --disk /dev/sdb --part 1 --label "Ubuntu " --loader /EFI/ubuntu/shimx64.efi
        Boot_a_suppr = combo_boot.get()[3:12]
        commande = "sudo efibootmgr -b " + Boot_a_suppr[4:9] + " -B"
        label_commande.configure(text=commande)

    # ===================================== un_Device_selecte appelée si événement ComboboxSelected de combo_device.bind
    def un_boot_selecte(eventobject):
        change_choix_boot()  # ========= action effectuée suite à cet événement
    # ================================= fin =============================================================================

    # ========================================= executer commande de suppression ========================================
    def executer_commande():
        global commande
        code_retour = os.system(commande)
        if code_retour != 0:
            commande=commande + blancs
            print("crash " + commande[0:30] + "... with return code =", code_retour)
            label_titre0['text']="crash " + commande[0:30] + " with return code =" + str(code_retour)
        else:
            faire_ou_refaire_le_boulot()
            win_suppr.destroy()
    # ================================== fin executer commande de suppression ===========================================
    def annuler_suppr():
        win_suppr.destroy()
    #=============================== bouton annuler =====================================================================
    annuler = tk.Button(zone2, activebackground = "red", bg = "cyan", fg = "black", command = annuler_suppr, width = 9)
    annuler.config(text="Cancel")
    annuler.pack(padx=2, pady=8, side="top")
    annuler.place(x=674, y=1)
    annuler.config(height=1, width=12)
    #================================ fin bouton annuler ================================================================

    # ================================ bouton executer et quitter ===================================
    executer = tk.Button(zone2, activebackground = "red", bg = "cyan", fg = "black", command = executer_commande, width = 9)
    executer.config(text="Run & Exit")
    executer.pack(padx=2, pady=8, side="top")
    executer.place(x=1, y=1)
    executer.config(height=1, width=12)
    # ================================= fin bouton executer et quitter ================================

    # ============================ construit la liste déroulante des boot presents ===========================
    #combo_boot = ttk.Combobox(zone2, width=60, values=table_bootnum)    table_lignes_affichees
    combo_boot = ttk.Combobox(zone2, width=95, values=table_lignes_affichees)
    combo_boot.place(x=10,y=65)
    combo_boot.current(index_combo)
    combo_boot.bind("<<ComboboxSelected>>", un_boot_selecte)  # ==action "un_pays_selecte" quand uévénement ComboboxSelected
    # ============================ fin liste partitions possibles ============================================

    label_titre0 = tk.Label(zone2, text=" ", bg='light blue', fg='red', width=66)
    label_titre0.place(x=135, y=0)
    label_titre4 = tk.Label(zone2, text="Command that will be executed", bg='light blue', fg='black', width=30)
    label_titre4.place(x=275, y=90)
    label_titre2 = tk.Label(zone2, text="Choosing the element to delete", bg='light blue', fg='black', width=30)
    label_titre2.place(x=275, y=35)

    label_commande = tk.Label(zone2, text="Command that will be executed", bg='ivory', fg='black', width=97)
    label_commande.place(x=10, y=115)
    #=========initialisation===============
    boot_choisi = combo_boot.get()
    Boot_a_suppr = combo_boot.get()[3:12]
    commande = "sudo efibootmgr -b " + Boot_a_suppr[4:9] + " -B"
    label_commande.configure(text=commande)

    win_suppr.transient(window) 	  # Réduction popup impossible
    win_suppr.grab_set()		  # Interaction avec fenetre window impossible
    window.wait_window(win_suppr)   # Arrêt script principal

def popup_ordre():
    import tkinter as tk
    #import tkinter.font as tkf
    import tkinter.ttk as ttk
    global table_efibootmgr_net
    global global_bootorder
    global table_lignes_affichees
    global LargeurScreen
    global HauteurScreen
    global global_booCurrent
    global Boot_a_depl
    coin_x=window.winfo_x()  # position de la fenêtre mère
    coin_y=window.winfo_y()   # position de la fenêtre mère
    largeur_wincourante=800
    hauteur_wincourante=180

    win_reorg = tk.Toplevel()		  # Popup -> Toplevel()
    win_reorg.transient(window)
    win_reorg.title('Reorg BootOrder')

    # calcule position x, y
    x = coin_x + (int(largeur_fenetre)/2)  - (int(largeur_wincourante) / 2)
    y = coin_y + (int(hauteur_fenetre)/2) -(int(hauteur_wincourante) / 2) + 100
    win_reorg.geometry('%dx%d+%d+%d' % (largeur_wincourante, hauteur_wincourante, x, y))
    win_reorg.config(bg="cyan")
    table_lignes_citees=[]
    cmd=""
    index_combo=1
    win_reorg.config(bg="cyan")

    zone3 = tk.Frame(win_reorg, bg='light blue')
    zone3.pack(padx=1, pady=1, fill='both', expand=1)

    label_titre0 = tk.Label(zone3, text=" ", bg='light blue', fg='red', width=66)
    label_titre0.place(x=135, y=0)

    label_anc = tk.Label(zone3, text="Current BootOrder : ", bg='light blue', fg='black', width=17)
    label_anc.place(x=10, y=35)
    #label_anc.pack

    Boot_Actu = tk.Label(zone3, text="Current BootOrder : ", bg='white', fg='black', width=80, font=("courrier", 9))
    Boot_Actu.place(x=150, y=35)
    #Boot_Actu.pack

    label_nouv = tk.Label(zone3, text="BootOrder project : ", bg='light blue', fg='black', width=17)
    label_nouv.place(x=10, y=60)

    Boot_projet = tk.Text(zone3, bg='white', fg='blue', borderwidth=0, font=("courrier", 9), width=80)
    Boot_projet.place(x=150, y=60)
    Boot_projet.configure(tabs=('8.45c', 'center'))        # tabulation centrée à 8 cm du bord gauche

    bricole="\t123456789012345678901234567890"
    Boot_projet.configure(height=1, bg="white")
    #Boot_projet.insert(tk.END, "\n" + bricole)
    Boot_projet.insert("1.1" , bricole)
    Boot_projet.delete("1.0", "end")
    Boot_projet['state'] = 'disabled'

    label_choix_poste= tk.Label(zone3, text="Choose an item to move", bg='light blue', fg='black', width=27)
    label_choix_poste.place (x=200, y=95)
    #label_choix_poste.pack

    label_depl = tk.Label(zone3, text="move", bg='light blue', fg='grey', width=9)
    label_depl.place(x=660, y=120)
    #label_depl.pack

    label_commande_sera=tk.Label(zone3, text="the command will be: ", bg='light blue', fg='grey', width=20)
    label_commande_sera.place(x=5, y=145)
    label_commande_sera.update()
    label_commande=tk.Label(zone3, text="sudo efibootmgr -o xxxx,...", bg='light blue', fg='grey', width=86,anchor='w')
    label_commande.place(x=150, y=145)

    table_bootorder_actu = []
    #   >BootOrder = "BootOrder: 0000,0001,0003,0008,0004,0007"   non reclassé
    inter_char = global_bootorder  # ------- tiré de efibootmgr -v
    caracteres_a_remplacer = (',', '-', '!', '?', 'BootOrder: ')  # --- liste de chaines à remplacer "
    for r in caracteres_a_remplacer:        # pour tout élément "r" de la liste, le remplacer par un blanc
        inter_char = inter_char.replace(r, ' ')
    # inter_char est devenu  "0000 0001 0003 0008 0004 0007"   non reclassé, et sans virgules
    mots = inter_char.split()  # ----- mots est la liste (table) de bootorders

    for x in mots:
        table_bootorder_actu.append(x)  # table_bootorder est la liste des rangs de boot
    # table_bootorder_actu est constituée
    BootOrder_actu = ""
    table_bootorder_proj=table_bootorder_actu
    BootOrder_proj=""


    table_boot_actu=[]
    for i in range (0,len(table_bootorder)):
        table_boot_actu.append(str(table_bootorder[i]))

    def compose_ligne_boot_order(table):
        bootOrder=""
        for i in range (0,len(table)):
            if i < (len(table)-1) :
                bootOrder = bootOrder + str(table[i]) + ","
            else:
                bootOrder = bootOrder + str(table[i])
        return(bootOrder)
    #fin composition bootorder projet
    zz=compose_ligne_boot_order(table_bootorder_actu)
    Boot_Actu.config(text=zz)
    table_bootorder_proj=table_bootorder_actu
    zz = compose_ligne_boot_order(table_bootorder_proj)
    #Boot_projet.config(text=zz)
    #Boot_projet.config(text=zz)
    Boot_projet['state'] = 'normal'
    Boot_projet.delete("1.0", "end")
    Boot_projet.insert("1.1", "\t" + zz)
    pos1 = Boot_projet.search(global_booCurrent, "1.0", stopindex="end")
    pos2 = '%s+%dc' % (pos1, 5)
    Boot_projet.tag_configure('tag_bleu', background='yellow', foreground='red')
    Boot_projet.tag_add("tag_bleu", pos1, pos2)
    Boot_projet.update()
    Boot_projet['state'] = 'disabled'











    #========== tri de table_lignes_affichees selon leur rang dans bootorder
    #suppression des postes qui ne sont pas cités dans bootorder. Commencent par  " ? "
    for i in range(0, len(table_lignes_affichees)):
        if table_lignes_affichees[i][0:3] != " ? ":
            table_lignes_citees.append(table_lignes_affichees[i])

    #======================= on commence par affecter à chaque ligne citee son rang dans bootorder (on le note dans table des rangs)
    table_des_rangs= []
    for i in range(0, len(table_lignes_citees)):        # création de la table des rangs avec "00000" partout
        table_des_rangs.append("00000")
    for i in range (0,len(table_lignes_citees)):
        rng=table_lignes_citees[i][7:11]        # ligne de NVRAM commence par "   Boot" son rang est donc de 7 à 11
        for j in range (0,len(table_bootorder)):
            if rng==table_bootorder[j]:   # la ligne str de NVRAM  a le rang  j dans bootorder
                truc="00000" + str(j)
                table_des_rangs[i]=truc[-5:]    # 5 derniers caractères de "00000" + str(j)
                #print(table_des_rangs[i])
                pass
        if j >= len(table_bootorder) :   # la ligne de NVRAM de rang rng n'est pas citée dans la table bootorder
            table_des_rangs[i] = "99999"

    #====================== tri de table_lignes_affichees selon son rang dans bootorder
    if bit_triEFI == 1 :    # on est dans le cas où l'affichage des lignes de NVRAM est classé selon leur rang dans bootorder
        # print ("tri selon rang dans bootorder")
        for i in range (0,len(table_lignes_citees)-1):
            for j in range (i+1,len(table_lignes_citees)):
                if (table_des_rangs[j] < table_des_rangs[i] ) :
                    tampon1 = table_des_rangs[i]
                    tampon2 = table_lignes_citees[i]
                    table_des_rangs[i]=table_des_rangs[j]
                    table_lignes_citees[i]=table_lignes_citees[j]
                    table_des_rangs[j]=tampon1
                    table_lignes_citees[j]=tampon2
    #else:
        # print("tri selon rang en NVRAM")

    #print ("table triée ")
    #for i in range (0,len(table_lignes_citees)):
        #print (table_lignes_citees[i])
    # fin   table_lignes_citees classée selon bootorder

    # ===================================== un_Device_selecte appelée si événement ComboboxSelected de combo_device.bind
    def un_boot_selecte(eventobject):
        global cmd
        global Boot_a_depl
        #fait venir les boutons droit gauche
        droite.config(state="normal")
        gauche.config(state="normal")
        label_depl.config(fg='black')
        label_commande.config(fg='red')
        label_commande_sera.config(fg='red')
        Nouv_ordre_lignes = table_lignes_citees
        liste_boot.config(values=Nouv_ordre_lignes)

        zz = compose_ligne_boot_order(table_bootorder_proj)
        cmd = "sudo efibootmgr -o " + zz
        label_commande.config(text=cmd)
        choisi=liste_boot.get()[7:11]
        Boot_projet['state'] = 'normal'
        Boot_projet.delete("1.0", "end")
        Boot_projet.insert("1.1", "\t" + zz)
        pos1 = Boot_projet.search(choisi, "1.0", stopindex="end")
        pos2='%s+%dc' % (pos1, 5)
        Boot_projet.tag_configure('tag_bleu', background='yellow', foreground='red')
        Boot_projet.tag_add("tag_bleu", pos1, pos2)
        Boot_projet.update()
        Boot_projet['state'] = 'disabled'

    def deplace_droite():
        global cmd
        global Boot_a_depl
        zz="123456789"
        Nouv_ordre_lignes = table_lignes_citees
        Boot_a_depl = liste_boot.get()[7:11]
        borne_sup=len(table_bootorder_proj)-1
        for i in range (0, len(table_bootorder_proj)):
            if Boot_a_depl == table_bootorder_proj[i]:
                if i < borne_sup:
                    #permute avec suivant
                    tampon=table_bootorder_proj[i+1]
                    table_bootorder_proj[i+1]=table_bootorder_proj[i]
                    table_bootorder_proj[i]=tampon
                    zz=compose_ligne_boot_order(table_bootorder_proj)
                    #Boot_projet.config(text=zz)
                    Boot_projet['state'] = 'normal'
                    Boot_projet.delete("1.0", "end")
                    Boot_projet.insert("1.1", "\t" + zz)
                    Boot_projet['state'] = 'disabled'


                    #Boot_projet.config(text=zz)
                    tampon =Nouv_ordre_lignes [i+1]
                    Nouv_ordre_lignes[i + 1]=Nouv_ordre_lignes [i]
                    Nouv_ordre_lignes[i]=tampon
                    break
                break
            #fin traitementposte du poste a deplacer
        #fin balayage de la table  table_bootorder_proj
        liste_boot.config(values=Nouv_ordre_lignes)
        #cmd="sudo efibootmgr -o " + Boot_projet["text"]
        if zz != "123456789":
            cmd = "sudo efibootmgr -o " + zz
        else:
            return

        label_commande.config(text=cmd)
        bricole = zz
        Boot_projet['state'] = 'normal'
        Boot_projet.delete("1.0", "end")
        Boot_projet.insert("1.1", "\t" + bricole)
        pos1 = Boot_projet.search(Boot_a_depl, "1.0", stopindex="end")
        pos2='%s+%dc' % (pos1, 5)
        Boot_projet.tag_configure('tag_bleu', background='yellow', foreground='red')
        Boot_projet.tag_add("tag_bleu", pos1, pos2)
        Boot_projet.update()
        Boot_projet['state'] = 'disabled'



    def deplace_gauche():
        global cmd
        global Boot_a_depl
        zz="123456789"
        Nouv_ordre_lignes = table_lignes_citees
        Boot_a_depl = liste_boot.get()[7:11]
        for i in range (0, len(table_bootorder_proj)):
            if Boot_a_depl == table_bootorder_proj[i]:
                if i > 0 :
                    #permute avec precedent
                    tampon=table_bootorder_proj[i-1]
                    table_bootorder_proj[i-1]=table_bootorder_proj[i]
                    table_bootorder_proj[i]=tampon
                    zz=compose_ligne_boot_order(table_bootorder_proj)
                    #Boot_projet.config(text=zz)
                    Boot_projet['state'] = 'normal'
                    Boot_projet.delete("1.0", "end")
                    Boot_projet.insert("1.1", "\t" + zz)
                    Boot_projet['state'] = 'disabled'


                    tampon =Nouv_ordre_lignes [i-1]
                    Nouv_ordre_lignes[i -1]=Nouv_ordre_lignes [i]
                    Nouv_ordre_lignes[i]=tampon
                # fin traitement jusqu'a avant poste
            pass
            #fin traitementposte du poste a deplacer

        liste_boot.config(values=Nouv_ordre_lignes)
        #cmd="sudo efibootmgr -o " + Boot_projet.cget('text')
        #cmd = "sudo efibootmgr -o " + Boot_projet.cget('text')
        if zz != "123456789":
            cmd = "sudo efibootmgr -o " + zz
        else:
            return




        label_commande.config(text=cmd)

        bricole = zz
        Boot_projet['state'] = 'normal'
        Boot_projet.delete("1.0", "end")
        Boot_projet.insert(tk.END, "\t" + bricole)
        pos1 = Boot_projet.search(Boot_a_depl, "1.0", stopindex="end")
        pos2='%s+%dc' % (pos1, 5)
        Boot_projet.tag_configure('tag_bleu', background='yellow', foreground='red')
        Boot_projet.tag_add("tag_bleu", pos1, pos2)
        Boot_projet.update()
        Boot_projet['state'] = 'disabled'


    # ================================= fin =============================================================================




    droite = tk.Button(zone3, activebackground="red", bg="light grey", fg="black", command=deplace_droite, width=9,relief="raised")
    droite.config(text=">")
    droite.pack(padx=1, pady=1, side="top")
    droite.place(x=737, y=112)
    droite.config(height=1, width=1)
    droite.config(state="disabled")

    gauche = tk.Button(zone3, activebackground="red", bg="light grey", fg="black", command=deplace_gauche, width=9,relief="raised")
    gauche.config(text="<")
    gauche.pack(padx=1, pady=1, side="top")
    gauche.place(x=630, y=112)
    gauche.config(height=1, width=1)
    gauche.config(state="disabled")

    # ============================ fin liste partitions possibles ============================================
    text_font=('Courrier', "9")
    liste_boot=ttk.Combobox(zone3,font=text_font,width=75, values=table_lignes_citees)
    liste_boot.place(x=10,y=120)
    liste_boot.config(background="pink")
    liste_boot.update()
    liste_boot.bind("<<ComboboxSelected>>", un_boot_selecte)
    cmd = "sudo efibootmgr -o " + Boot_projet.get('1.0', 'end')
    def executer_commande():
        global cmd
        un=Boot_Actu.cget('text')
        deux=Boot_projet.get("1.0","end").lstrip()
        l=len(deux) - 1     # un saut de ligne à droite, à enlever
        deux=deux[0:l]
        if un == deux:
            label_titre0['text']="nothing was done"
            return
        else:
            label_titre0['text'] = ""
        #print ("la commande va être """ + cmd )
        code_retour = os.system(cmd)
        if code_retour != 0:
            cmd=cmd + blancs
            print("crash " + cmd[0:30] + "... with return code =", code_retour)
            label_titre0['text']="crash " + cmd[0:50] + " , return code " + str(code_retour)
        else:
            faire_ou_refaire_le_boulot()
            win_reorg.destroy()

    def quitter():
        win_reorg.destroy()
    # ================================== fin executer commande de reorg===========================================

    # =============================== bouton annuler =====================================================================
    annuler = tk.Button(zone3, activebackground="red", bg="cyan", fg="black", command=quitter, width=9)
    annuler.config(text="Cancel")
    annuler.pack(padx=2, pady=8, side="top")
    annuler.place(x=674, y=1)
    annuler.config(height=1, width=12)
    # ================================ fin bouton annuler ================================================================

    # ================================ bouton executer et quitter ===================================
    executer = tk.Button(zone3, activebackground="red", bg="cyan", fg="black", command=executer_commande, width=9)
    executer.config(text="Run & Exit")
    executer.pack(padx=2, pady=8, side="top")
    executer.place(x=1, y=1)
    executer.config(height=1, width=12)
    # ================================= fin bouton executer et quitter ================================

    win_reorg.transient(window) 	  # Réduction popup impossible
    win_reorg.grab_set()		  # Interaction avec fenetre window impossible
    window.wait_window(win_reorg)   # Arrêt script principal

def popup_quitter():
    print ("and then press the enter key")
    sys.exit()








Bouton_creat = tk.Button(zone, width=8, text="create", command=popup_creat, relief="flat")
Bouton_creat.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black')

Bouton_modif = tk.Button(zone, width=8, text="edit", command=popup_modif, relief="flat")
Bouton_modif.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black')


Bouton_suppr = tk.Button(zone, width=8, text="delete", command=popup_suppr)
Bouton_suppr.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black', relief="flat")

# ------ bouton pour modifier BootOrder
Bouton_order = tk.Button(zone, width=8, text="Reorg Order", command=popup_ordre, relief="flat")
Bouton_order.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black')



Bouton_quitter = tk.Button(zone, width=8, text="End", command=popup_quitter)
Bouton_quitter.config(bg='cyan', fg='black', activebackground='red', activeforeground='black')




# ------ checkbox (case à cocher) pour choisir l'ordre d'affichage des lignes EFI naturel ou selon bootorder
chk_triEFI: Checkbutton = tk.Checkbutton(zone, width=16, text="Sorted / BootOrder", bd=4 , var=chk_triEFI, command=chk_triEFI)
chk_triEFI.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black', selectcolor="white")
chk_triEFI.select()
chk_triEFI.pack(padx=3, pady=10, side="top")






# ------- zone de texte contenant la liste des postes EFI obtenus par "sudo efibootmgr -v" complétée
from tkinter import scrolledtext



#-----------------------------------------------------ici
#resultat = scrolledtext.ScrolledText(zone1, wrap=tk.WORD,
resultat = scrolledtext.ScrolledText(zone, wrap=tk.WORD,
                                     background="light cyan",
                                     foreground="black")
#resultat=

" ---------------------------------------------------ici"

resultat.place(x=0, y=35,)

resultat.pack(fill='both')

#-----------------------------------------ici
from threading import Timer

def resize(event):
    global largeur_fenetre
    global hauteur_fenetre
    global LargeurScreen
    global HauteurScreen
    global coin_x
    global coin_y
    largeur_fenetre = window.winfo_width()
    hauteur_fenetre = window.winfo_height()
    LargeurScreen = window.winfo_screenwidth()
    HauteurScreen = window.winfo_screenheight()
    coin_x=(LargeurScreen - largeur_fenetre)/2
    coin_y=(HauteurScreen - hauteur_fenetre)/2

    t = Timer(0.3, Timer_souris)
    t.start()



zone.bind("<Configure>", resize)

#-------------------------------------------------ici
def Timer_souris():
    global bit_bouton
    bit_bouton = 0
    Bouton_verbeux.invoke()
    bit_bouton=1



print (dir_travail + "/" + os.path.basename(__file__))

#positions initiales

verbeux="0"

#=============================== boucle principale

window.title (dir_travail + "/" + os.path.basename(__file__))

recadrer()
#faire_ou_refaire_le_boulot()


window.mainloop()

#-------------------------------fin de boucle----------------------------------------
if os.path.exists(dir_travail + "/blkid.txt"):  # supprime le fichier résidu éventuel
    os.remove(dir_travail + "/blkid.txt")

if os.path.exists(dir_travail + "/efiboot.txt"):  # supprime le fichier résidu éventuel
    os.remove(dir_travail + "/efiboot.txt")

print ("---------------------terminé----------------------------------")
#--------------------------------fin du programme--------------------------------------
