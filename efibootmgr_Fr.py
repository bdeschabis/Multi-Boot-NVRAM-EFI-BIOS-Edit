# -*-coding:Latin-1 -*
# 09/06/2021
# -- rappel : sudo blkid donne la liste des partitions sda1, sda2,... avec leur UUID de partition, comme ceci :
# /dev/sda2: UUID="ec29c189-4443-477d-a5b2-cc27ee4f2f5f" TYPE="ext4" PARTUUID="53fdb494-8960-43d9-9046-05d9a9535af2"
# /dev/sdb1: LABEL_FATBOOT="EFI" LABEL="EFI" UUID="70D6-1701" TYPE="vfat" PARTLABEL="EFI System Partition" PARTUUID="44114127-5172-48c4-8013-a08d6ae5998d"
# /dev/sdb2: UUID="595f05fc-254f-404d-85aa-e3738190a1b3" TYPE="apfs" PARTLABEL="macOS" PARTUUID="aea857a6-cd93-485e-8bbd-38479205d2c8"
# /dev/sda1: UUID="56B9-798D" TYPE="vfat" PARTLABEL="Efi Sda1" PARTUUID="c3312c62-42d0-4cd3-8c26-875eb96dd1b0"
# /dev/sda3: UUID="4dd750d9-d6e7-46dd-af8e-dce0ef7215b7" TYPE="swap" PARTUUID="e45e375c-3841-4d4f-82ef-2fc522663841"
# /dev/sda4: UUID="b1917d60-2061-4f87-b5c4-8450dc43bbd8" TYPE="ext4" PARTUUID="982182cb-d81a-4eb8-8a83-7b4a4b158cd4"
# /dev/sda5: LABEL="Exfat" UUID="1075-3F3C" TYPE="exfat" PTTYPE="dos" PARTUUID="c113352b-2888-7648-a50e-a8450cb27dd9"

# --          sudo efibootmgr -v  donne la liste des postes de la NVFAT et l'ordre de d�marrage
# BootOrder: 0003,0004,0005,0006,0001
# Boot0001* Refind AppleSdb	HD(1,GPT,44114127-5172-48c4-8013-a08d6ae5998d,0x28,0x64000)/File(\EFI\refind\refind_x64.efi)
# Boot0003* Refind Sda1	HD(1,GPT,c3312c62-42d0-4cd3-8c26-875eb96dd1b0,0x800,0x100000)/File(\EFI\refind\refind_x64.efi)
# Boot0004* Mint Sda1	HD(1,GPT,c3312c62-42d0-4cd3-8c26-875eb96dd1b0,0x800,0x100000)/File(\EFI\debian\shimx64.efi)
# Boot0005* Refind Sdc	HD(1,GPT,483d0a05-f775-45f0-8904-07eedefc4935,0x800,0x79800)/File(\EFI\refind\refind_x64.efi)
# Boot0006* Kubuntu Sdc	HD(1,GPT,483d0a05-f775-45f0-8904-07eedefc4935,0x800,0x79800)/File(\EFI\debian\shimx64.efi)
# BootFFFF* 	PciRoot(0x0)/Pci(0x1f,0x2)/Sata(0,0,0)/HD(1,GPT,c3312c62-42d0-4cd3-8c26-875eb96dd1b0,0x800,0x100000)/File(\EFI\BOOT\BOOTX64.efi)

#================================================================
# pour lancer le script, ne pas utiliser exec mais sudo dans un terminal

import os  # fonctions propres � l'OS linux, window, ...dont on peut tirer le s�parateur syst�me et change dir
import sys
import time
import subprocess
import tkinter as tk
from tkinter import Checkbutton

#passage au r�pertoire contenant le programme
dir=format(os.getcwd())
os.chdir(dir)

#================== doit �tre root , v�rifie et �ventuellement, le devient===================================
euid = os.geteuid()
if euid != 0:   # v�rifie que le script tourne sous super user (vrai si euid=0)
    print ("Demande privil�ges Sudo.")
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    # the next line replaces the currently-running process with the sudo
    os.execlpe('sudo', *args)

print ('OK, tourne en super utilisateur')


#===========================d�claration des variables qui seront globales dans les proc�dures
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


non_mont� = "non"    # indicateur signalant des lignes EFI valides mais dont la partUUID n'est pas dans blkid
blancs="                                                                                 "
dir_travail = os.path.abspath(os.path.dirname(__file__))  # d�termine le r�pertoire du programme
os.chdir(dir_travail)  # CD dossier o� est "efibootmgr_Fr.py"
#================================  efibootmgr ne fonctionne bien que si sudo
if os.getuid() != 0:
    print("ce programme doit �tre lanc� en tant que super utilisateur")
    print("Presser la touche entr�e")
    sys.exit()
#--------v�rifiation de la pr�sence de blkid et efibootmgr n�cessaires � ce programme----------------------
#=============   le r�sultat de "which efibootmgr" est "/bin/efibootmgr" ou rien si efibootmgr pas install�
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
os.remove(dir_travail + "/efibootmgr_blkid.txt")  # efface fichier r�sidu d'un pr�c�dent passage �ventuellement

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

# ------------------------------- fin de v�rification de la pr�sence de blkid , efibootmgr et lsblk-----------


# ============================= proc�dure d'affichage du message si aide demand�e (param "h" en fin de commande)=============================
def aidez_moi():
    print("program displaying the EFI launchers of this system. It uses the sudo efibootmgr and blkid commands")
    print("as well as python3 libraries os, sys, tkinter, signal, ")
    print("It can receive parameters ""h"" (help me), ""t"" (display in terminal) and ""v"" (with comment)")
    print("It must be launched as a super user (root)")
    print("by example : sudo python3 /home/path to.../efibootmgr_sdy.py 'h'")
    if os.getuid() != 0:   #---v�rification que lanc� as root
        print("Comme ce n'est pas le cas, vous allez �tre vir� dans 10 secondes.")
        time.sleep(10)
        quit()

# =================================fin de proc�dure aidez_moi ===================================================

# ------------------acquisition des param�tres de la ligne de commande---------------------


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
# -------------------------------fin acquisition param�tres --------------------------------


# -------------------- suppression d'anciens fichiers si n�cessaire-----------------------------
if os.path.exists(dir_travail + "/blkid.txt"):  # supprime le fichier r�sidu �ventuel
    os.remove(dir_travail + "/blkid.txt")

if os.path.exists(dir_travail + "/efiboot.txt"):  # supprime le fichier r�sidu �ventuel
    os.remove(dir_travail + "/efiboot.txt")


# ======== valeurs initiales pour les fen�tres

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

window.geometry('%dx%d+%d+%d' % (largeur_fenetre, hauteur_fenetre, coin_x, coin_y))
window.configure(bg="light blue")
#window.update()

bit_triEFI = 1  #----utilis� pour l'affichage des lignes EFI en ordre naturel ou selon la table BootOrder NVRAM
verbeux="0"

#===================================  composition d'un baratin explicatif =============================
#-----------------la table table_commentaire contient les lignes du baratin affich�es en bas de fen�tre
table_commentaire.append("            ")
table_commentaire.append("< efibootmgr_Fr.py et efibootmgr_US.py sont deux GUI (graphical user interfaces) pour la commande Linux efibootmgr.>")
table_commentaire.append("   ")
table_commentaire.append("Lexique : la NVRAM est une m�moire non volatile conserv�e sur la carte m�re. Elle contient, entre autres, une liste")
table_commentaire.append("des modules ex�cutables lan�ant les diff�rents OS (Operating System : windows, linux, ...), avec leur localisation ")
table_commentaire.append("dans les diff�rentes unit�s h�bergeant ces OS. Elle contient �galement une table de priorit� indiquant dans quel")
table_commentaire.append("ordre est examin�e la liste de ces modules lors du d�marrage de l'ordinateur (table BootOrder ci-dessus)")
table_commentaire.append("Lors de l'installation d'un nouvel OS, son programme d'installation enrichit la NVRAM en y inscrivant une ligne")
table_commentaire.append("localisant son propre module de d�marrage, et il place ce nouveau poste en t�te de BootOrder")
table_commentaire.append("La ligne 'BootOrder' de cet �cran pr�sente l'ordre de prise en compte (priorit�s) des diff�rents modules, et les")
table_commentaire.append("lignes suivantes pr�sentent les diff�rents modules avec leur localisation")
table_commentaire.append("     ")
table_commentaire.append(" <Attention !!!> Ces lignes sont celles de la NVRAM et peuvent ne pas �tre toutes valides � cet instant.")
table_commentaire.append("On y trouve en effet tous les lanceurs des dossiers EFI des partitions ESP avec lesquels l'ordinateur a d�j� boot�.")
table_commentaire.append("Utilisez Refind pour voir tous les lanceurs au moment du boot, et efibootmgr ou le pr�sent logiciel logiciel pour")
table_commentaire.append("les reclasser.")
table_commentaire.append("La commande 'sudo efibootmgr -v' montre les entr�es de boot avec les UUID des partitions EFI les contenant, mais")
table_commentaire.append("l'utilisation de l'UUID est peu pratique. Le but de efibootmgr_Fr.py est de fournir en plus pour chaque UUID")
table_commentaire.append("de partition son nom commun linux : sda1, sdb1, sdc1.... en s'appuyant sur le r�sultat de la commande 'blkid'")
table_commentaire.append("Afin de ne jamais �tre bloqu� au boot, on a int�r�t, pour chaque syst�me, � placer en t�te le lanceur du logiciel")
table_commentaire.append("Refind (entr�e '\EFI\\refind\\refind_x64.efi') qui, lui, d�tecte toutes les entr�es bootables � la vol�e.")
table_commentaire.append("Le programme d'installation de Refind s'installe comme un lanceur dans /boot/efi/EFI/refind/refind_x64.efi.")
table_commentaire.append("(si la partition ESP est /dev/sdc1 et root est /dev/sdc2, alors /dev/sdc1/EFI/  est mont� dans  /dev/sdc2/boot/efi)")
table_commentaire.append("le script efibootmgrgui_Fr permet �galement de changer l'ordre de d�marrage des lanceurs ou d'en inscrire de nouveaux,")
table_commentaire.append("tout comme efibootmgr")
table_commentaire.append("De m�me, l'installeur de Grub ajoute ses propres lanceurs /boot/efi/EFI/ubuntu/shimx64.efi et grubx64.efi ")
table_commentaire.append("Sur un syst�mes dont l'EFIbios n'accepte que les lanceurs sign�s num�riquement, on ne peut pas d�marrer � l'aide de")
table_commentaire.append("grubx64.efi, qui n'est pas sign�. Shimx64.efi par contre est sign�, et est donc accept�. Il passe alors la main �")
table_commentaire.append("grubx64.efi et le tour est jou�. ")
table_commentaire.append("                                    efibootmgr : commandes utiles ")
table_commentaire.append('Liste de la NVRAM : <" sudo efibootmgr -v " >          ')
table_commentaire.append("Remplacement de l" + chr(39) + 'enregistrement BootOrder :  <"sudo efibootmgr -o 0002,0001,0000,00003,00007"> ')
table_commentaire.append('Suppression du poste bootloader 000x : <"sudo efibootmgr -b 000x -B">')
table_commentaire.append('< Attention, dans ce qui suit, le \ habituel des chemins de Linux doit imp�rativement �tre remplac� par />')
table_commentaire.append("ajout d" + chr(39) + "un poste '"'/EFI/refind/refind_x64.efi'"' pour la partition ESP sdc1 par exemple : <>")
table_commentaire.append('< sudo efibootmgr --create --disk /dev/sdc --part 1 --label "Refind " --loader /EFI/refind/refind_x64.efi>')
table_commentaire.append("ajout d" + chr(39) + "un poste '"'/EFI/ubuntu/shimx64.efi'"' dans la partition ESP sdb1 par exemple : <>")
table_commentaire.append('< sudo efibootmgr --create --disk /dev/sdb --part 1 --label "Ubuntu " --loader /EFI/ubuntu/shimx64.efi>')
table_commentaire.append("(ce loader, sign�, quant-� lui lance grubx64.efi, non sign�, qui est dans le m�me r�pertoire). <> ")
table_commentaire.append("")
table_commentaire.append("=================================================================================================")
table_commentaire.append("====================================================================================================")
table_commentaire.append("      Quelques explications concernant le d�marrage des ordinateurs dits 'UEFI' ou  'EFI-BIOS'")
table_commentaire.append("Sur toute carte m�re est implant�e une m�moire qui ne s'efface pas m�me apr�s arr�t de l'ordinateur. Cette m�moire,")
table_commentaire.append("non volatile, est souvent appel�e NVRAM (acronyme de 'Non Volatile Random Access Memory'). Elle contient entre autres")
table_commentaire.append("une table dont chaque poste peut indiquer le nom d'un programme dont l'ex�cution est imm�diate avant activation de tout")
table_commentaire.append("OS (Windows, Linux,...) plus l'unit� physique sur laquelle est ce programme (UUID de sa partition) plus dans cette")
table_commentaire.append("unit� le chemin qui conduit � lui, plus son nom de fichier (par exemple /EFI/ubuntu/shimx64.efi).")
table_commentaire.append("Elle contient �galement une table indiquant dans quel ordre doivent �tre parcourus les postes de la table pr�c�dente")
table_commentaire.append("pour d�cider quel syst�me lancer en premier, puis en second en cas d'�chec du premier, puis du troisi�me...etc. ")
table_commentaire.append("Tr�s logiquement cette seconde table est appel�e 'BootOrder', et chacun de ses postes contient le rang d'un poste ")
table_commentaire.append("de la premi�re table, sous la forme d'un nombre de quatre chiffres en notation hexad�cimale (0000,0001,...000A....) ")
table_commentaire.append("Un petit programme, lui aussi pr�sent en m�moire non volatile (on l'appelle BIOS) s'ex�cute d�s la mise sous tension.")
table_commentaire.append("Il d�tecte par lecture de la table BootOrder quel poste de la premi�re table il doit exploiter et donc quel programme")
table_commentaire.append("il doit charger pour ex�cution imm�diate. N'�tant pas tr�s intelligent, il ne comprend rien d'autre que le syst�me de")
table_commentaire.append("fichiers FAT32. Les partitions dont les UUID figurent dans la premi�re table doivent donc �tre au format FAT32 afin")
table_commentaire.append("que ce petit programme sache trouver charger et ex�cuter le programme de lancement de l'OS")
table_commentaire.append("Elles doivent de plus �tre marqu�es 'ESP' (ou 'EFI') et 'Bootable', sinon, elles sont ignor�es dans ce processus")
table_commentaire.append("")
table_commentaire.append("Sur les cartes m�res de qualit�, le BIOS est assez intelligent pour offrir, en affichage graphique, les outils")
table_commentaire.append("permettant de cr�er ou modifier des postes de la premi�re table, et de r�ordonner BootOrder. Mais sur des syst�mes")
table_commentaire.append("rustiques ou anciens, cet outil est tr�s rudimentaire ou absent. Dans ce dernier cas, les tables ne peuvent �tre")
table_commentaire.append("modifi�es que par un programme, charg� en cas de probl�me depuis un CD ou une cl� USB bootable.")
table_commentaire.append("Enfin, lors de l'installation d'un OS (UBUNTU par exemple), le programme d'installation (GRUB-INSTALL pour UBUNTU)")
table_commentaire.append("enrichit la NVRAM en y inscrivant une ligne localisant le module de d�marrage (shimx64.efi pour UBUNTU), et il ajoute")
table_commentaire.append("le rang de ce nouveau poste en t�te de BootOrder ")
table_commentaire.append("Au d�marrage suivant, c'est donc dans cet exemple shimx64.efi qui sera ex�cut�, lequel lancera UBUNTU.  ")
table_commentaire.append("")
table_commentaire.append("Remarque : un m�canisme d'authentification a �t� imagin� pour prot�ger l'ordinateur contre l'installation de programmes")
table_commentaire.append("de d�marrage non authentiques. Ce m�canisme est inclus dans le BIOS, qui v�rifie la 'signature' de chaque programme")
table_commentaire.append("avant de le lancer.  ")
table_commentaire.append("Or, diff�rents lanceurs existent sous Linux, non sign�s, pour lesquels dans un ordinateur prot�g� le lancement serait")
table_commentaire.append("refus� sauf �  tous les authentifier pr�alablement.")
table_commentaire.append("C'est pourquoi on utilise le programme 'shimx64.efi' qui, lui, est sign�, et dont le seul r�le est de lancer le")
table_commentaire.append("programme grubx64.efi (c'est le boot loader de Grub) propre � chaque variante de Linux.")
table_commentaire.append("")
table_commentaire.append("========================================= but du pr�sent programme ===============================")
table_commentaire.append("Le BIOS ne sachant lire que les partitions FAT32  dont le drapeau est 'ESP' (ou EFI), Le pr�sent programme se limite")
table_commentaire.append("�galement � ne pr�senter que ces unit�s sous la forme sda1, sdb1, sdc2....selon la convention de Linux.")
table_commentaire.append("Il permet de cr�er, modifier, supprimer des postes de la table listant les programmes de d�marrage des OS, et ")
table_commentaire.append("il permet �galement de modifier le classement de la table BootOrder.")
table_commentaire.append("")
table_commentaire.append("En fait, il compose en fonction des indications qui lui sont fournies et du contenu de la NVRAM les commandes ")
table_commentaire.append("que l'on aurait pu passer laborieusement � la main dans un terminal pour arriver au m�me r�sultat.")
table_commentaire.append("Les commandes utilis�es sont affich�es en bas de fen�tre avant d'�tre ex�cut�es.")
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
    # ----------- mise en m�moire de la table r�sultant de la commande "sudo blkid" . Exemples de lignes :-------------
    # --- /dev/sda2: UUID="ec29c189-4443-477d-a5b2-cc27ee4f2f5f" TYPE="ext4" PARTUUID="53fdb494-8960-43d9-9046-05d9a..."
    # --- /dev/sdb1: UUID="DD33-62A7" TYPE="vfat" PARTLABEL="Efi Sdb1" PARTUUID="483d0a05-f775-45f0-8904-07eedefc4935"

    #------------------le fichier blkid.txt a �t� cr�� dans la proc�dure faire_ou_refaire_le_boulot--------------------
    fich_blkid = open("blkid.txt", 'r')  # defines the object fich-blkid as readable file blkid.txt
    table_blkid_brute = fich_blkid.readlines()  # done, table_blkid_brute is done
    fich_blkid.close()  # close fich_blkid
    os.remove(dir_travail + "/blkid.txt")  #-------------------on n'en aura plus besoin
    # -------------------------- fin de mise en m�moire de la table  "table_blkid_brute"-------------------------------------------
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

        #--  Au final, pour trouver le device associ� � chaque poste de efibootmgr, il suffit de conserver device + partUUID dans table_blkid_nette
        ligne = "!" + dev_sd + "!" + partuuid + "!"  # sous cette forme  !/dev/sda2: !53fdb49...d9a9535af2!  with dev from 2 to 10 and PartUUID from 13 to 49
        table_blkid_nette.append(ligne)
        iblkid = iblkid+1
#============== fin extrac_dev_partUUID_de_blkid


#======================proc�dure d'extraction des infos de "efibootmgr -v" ===================================
def extract_efibootmgr():
    #======================= m�morisation des r�sultats de la commande "efibootmgr -v" comme ceci ==========
    #    order    |  efibootmgr_libel |       table_efibootmgr_EFIpart        |     table_efibootmgr_partfile
    #  Boot0000*  | Refind Sda1...... |  c3312c62-42d0-4cd3-8c26-875eb96dd1b0 |  \EFI\refind\refind_x64.efi....
    #  Boot0001*  | Elementary Sdc1.. |  4611294d-5452-4f5c-a21c-3a6ebecdd797 |  \EFI\ubuntu\shimx64.efi.......
    # ------------------le fichier efiboot.txt a �t� cr�� dans la proc�dure faire_ou_refaire_le_boulot---------------


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
    BootOrder = "pas de Boot0rder, EFIbios agira par d�faut ou faites ""sudo efibootmgr -o 0000,0001,0002 par exemple"""   # initialisation bootorder

    # la commande sudo efibootmgrgui liste les postes EFI, et permet de les reclasser (choix du boot) d'en cr�er ou supprimer.
    # la ligne  de efibootmgrgui est pour le poste 0003 par exemple "0003   ubuntu   \EFI\refind\refind_x64.efi"
    #           il y manque donc le volume /dev/sdx, car il peut y avoir plus d'un dossier \EFI\refind\refind_x64.efi (un par disque bootable)
    #
    # la ligne de la commande blkid est "/dev/sda1: UUID="56B9-798D" TYPE="vfat" PARTLABEL="Efi Sda1" PARTUUID="c3312c62-42d0-4cd3-8c26-875eb96dd1b0"
    #                                ce qui �tablit le lien entre volume (/dev/sdx) et partUUID
    # la ligne de efibootmgr -v est "Boot0003* ubuntu 	HD(1,GPT,c3312c62-42d0-4cd3-8c26-875eb96dd1b0,0x800,0x100000)/File(\EFI\refind\refind_x64.efi)
    #           cette derni�re nous donne tout, sauf le volume en clair (/dev/sda1)
    #
    # aussi, par EFI, nous allons afficher "Boot0003 | ubuntu ....| /dev/sda1 | \EFI\refind\refind_x64.efi....| c3312c62-42d0-4cd3-8c26-875eb96dd1b0"
    #                           ce qui nous dira quel est le volume ^^^^^^^^^  associ� � la ligne  "Boot0003" de efibootmgrgr.

    ilignes_EFI = 0
    partfile = " non d�fini                          "
    BootOrder=""

    for efiboot in table_efiboot:  # pour chaque ligne de sudo efibootmgr -v-

        if efiboot[0:9] == "BootOrder":
            BootOrder = efiboot
            global_bootorder=BootOrder
        else:
            if efiboot[0:13] == "BootCurrent: ":
                global_booCurrent=efiboot[13:17]
             #==================================d�but lignes non Bootorder=========================================
            else:
                if efiboot[0:6] == "Boot00":   #�limine les lignes Timeout, BootOrder, ...mais garde Boot00xx
                    EFI_MBR ="EFI"
                    deb_UUID = 0
                    efiboot = efiboot + blancs
                    order = efiboot[0:8]  # extrait Boot0001*
                    idx1 = 10

                    #idx2 = str.find(efiboot, chr(9))  # attention   entre quotes, caract�re ascii 09 (tabulation horizontale)

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
                    idx2=efiboot.find(')',idx1 )            #============parent�se fermante apr�s /File(
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
        print ("pas de BootOrder en NVRAM, on ne peut continuer")
        messages_ano_bootorder.append("pas de BootOrder en NVRAM, c'est le caca")
        # quit()    # a reactiver
        bit_triEFI = 0













#====================== fin de la proc�dure extract_efibootmgr ==========================================


#====================== affiche la fen�tre ==========================================

window.update()



#===== croisement des tables efibootmgr et blkid selon l'UUID pour report de "/dev/Sdx"  de blkid vers efibootmgr====
def croisement_efibootmgr_blkid_selon_UUID():
    #-- rappel : sudo blkid donne la liste des partitions sda1, sda2,... avec leur UUID de partition
    #--          sudo efibootmgr -v  donne la liste des postes de la NVFAT et l'ordre de d�marrage
    #-- pour chaque part UUIDposte de la table des lignes EFI, on cherche la m�me UUID dans blkid
    #-- et on en d�duit le /dev/sdx  tir� de table_blkid_nette(de pos 2 � 10) de m�me rang.
    global table_blkid_nette
    global table_EFIsdx
    global ilignes_EFI
    global table_efibootmgr_net
    global non_mont�
    global EFI_MBR

    non_mont� = "non"
    for j in range(0, len(table_efibootmgr_net)):   #---- pour chaque ligne EFI de efibootmgr, cherche parmi toutes blkid la m�me UUID
        #---------- initialise le poste de table_EFIsdx
        table_EFIsdx.append("...??...")
        rang_part = len (table_EFIsdx) -1


        #for i in range(0 , iblkid):     #---cherche �galit�
        for i in range(0, len(table_blkid_nette)):

            #  table_efibootmgr_net[j][34:70] est l'UUID de la ligne de efibootmgr -v
            #============== si �galit� entre les UUID
            if table_efibootmgr_net[j][34:70] == table_blkid_nette[i][13:49]:  # dans table_efi_nette, partUUID est de 13 � 49
                table_EFIsdx[rang_part] = table_blkid_nette[i][2:10]      # dans table_efi_nette, le device /dev/sdx est de 2 � 10
                break       #------- si trouv�, arr�ter la recherche d'�galit�, sdx trouv�, casser la boucle
            # !!!!!!!!!!!! attention, il se peut qu'on ne trouve pas d'unit� (d�mont�e) et alors table_EFIsdx[rang_part] est rest� � "...???..."

        if (table_EFIsdx[len(table_EFIsdx)-1] =="...??..."):
            non_mont� = "oui"

        #============ fin de proc�dure de croisement des tables  ================================================================

#=======================================proc�dure d'affichage dans window et dans terminal=================
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



    # ------la table table_EFI_print contient les lignes � afficher concernant les lanceurs EFI --------------

    table_EFI_Entete = []   #-------------------- trois lignes d'ent�te dans  table_EFI_Entete
    table_EFI_Entete.append("                          table efibootmgr  ")
    table_EFI_Entete.append("   " + BootOrder[0:len(BootOrder) - 1])  # retire le saut de ligne � droite de la cha�ne BootOrder
    table_EFI_Entete.append("     rang       libell�                      Lanceur dans ESP                     UUID de la partition  ")

    ilignes_print = 0
    table_EFI_print = []
    for j in range(0, ilignes_EFI):

        ligne = table_efibootmgr_net[j][1:9] + "|" + table_efibootmgr_net[j][11:31] + "|" + str(table_EFIsdx[j]) + table_efibootmgr_net[j][72:107] \
                + "|" + table_efibootmgr_net[j][34:70] + "|>" + table_efibootmgr_net[j][104:107] + "<"

        table_EFI_print.append(ligne)
        ilignes_print = ilignes_print + 1


    #-------------------- lignes de boot compos�es, dans table_EFI_print de 0 �  ilignes_print exclu

    # ----on constitue une table des bootorders
    table_bootorder = []
    #   >BootOrder = "BootOrder: 0000,0001,0003,0008,0004,0007"   non reclass�
    inter_char = BootOrder  # ------- tir� de efibootmgr -v
    caracteres_a_remplacer = (',', '-', '!', '?', 'BootOrder: ')  # --- liste de chaines � remplacer "
    for r in caracteres_a_remplacer:        # pour tout �l�ment "r" de la liste, le remplacer par un blanc
        inter_char = inter_char.replace(r, ' ')
    # inter_char est devenu  "0000 0001 0003 0008 0004 0007"   non reclass�, et sans virgules
    mots = inter_char.split()  # ----- mots est la liste (table) de bootorders

    for x in mots:
        table_bootorder.append(x)  # table_bootorder est la liste des rangs de boot
    # table bootorder est constitu�e

    #---------- pour que les lignes s'affichent dans l'ordre de BootOrder, on utilise une table interm�diaire
    #---------- dans laquelle on met table_EFI_print
    table_intermed = []
    table_intermed = table_EFI_print
    #======== ajout d'un argument de tri � droite de chaque ligne. C'est son rang dans BootOrder ou un num�ro > 10 si n'est pas cit�
    anonum = 99
    for i in range(0, len(table_intermed)):
        trouv� = "non"
        for j in range(0, len(table_bootorder)):
            if table_intermed[i][4:8] == table_bootorder[j]:
                trouv� = "oui"
                rangchar = "00000" + str(j)
                fin = len(rangchar)
                deb = fin - 5
                rangchar = rangchar[deb:fin]
                table_intermed[i] = table_intermed[i] + "    " + rangchar
                pass
        if trouv� != "oui":
            anonum = anonum + 1
            rangchar = "00000" + str(anonum)
            fin = len(rangchar)
            deb = fin - 5
            rangchar = rangchar[deb:fin]
            table_intermed[i] = table_intermed[i] + "    " + rangchar
        trouv� = "non"

    #---si on pr�f�re classer par bootorder
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



    #   la table table_intermed a alors le dessin suivant, tri�e selon l'argument de tri de 5 caract�res qui est � droite
    #   Si la valeur de cet argument est sup�rieure � 00100, alors il s'agit d'un poste non cit� dans BootOrder
    #   Boot0000|Refind MintUsb...|...??...\EFI\refind\refind_x64.efi....|b4f736db-41cf-5743-bebd-9c1f4340d126|>EFI<    00103

    #============ on peut maintenant remettre table_intermed dans table_EFI_print ===================
    table_EFI_print=table_intermed

    # searching for EFI items not mentioned in bootorder, we mark them with "?" on the left of the line
    # ?  Boot0000|Refind MintUsb...|...??...\EFI\refind\refind_x64.efi....|b4f736db-41cf-5743-bebd-9c1f4340d126|>EFI<    00103
    postes_efi_en_trop="non"
    for i in range (0,len(table_EFI_print)):
        # verif que ce num�ro est cit� dans bootorder
        fin=len(table_EFI_print[i])
        deb=fin - 5
        arg_tri=table_EFI_print[i][deb:fin]

        if (arg_tri > "00099"):
            table_EFI_print[i] = " ? " + table_EFI_print[i]
            postes_efi_en_trop = "oui"
        else:
            table_EFI_print[i] = "   " + table_EFI_print[i]

    if (postes_efi_en_trop == "oui"):
        table_EFI_print.append('   "?" � gauche d''un poste signale que ce poste n''est pas cit� dans BootOrder')

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


    if (non_mont� == "oui"):
        #==== ce peut �tre un poste MBR incongru
        table_EFI_print.append('   "...??..."' + " indique que cette ligne ne pointe pas vers un lanceur dans une partition EFI accessible")

    if printer == "oui":
        print("-------table EFI finale-------")
        for j in range(0 , len(table_EFI_print)):
            print (table_EFI_print[j])


    #--------------------  table_EFI_print est reclass�e -----------------------------
    #--------------- sinon (si chk_triEFI = false) , on laisse   table_EFI_print en l'�tat


    #------------------------ �criture de l'ent�te
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
        ligne2=ligne.replace("\\", "/")   #  le caract�re \ seul est un �chappement. Il faut le doubler
        ligne=ligne2

        ligne = ligne[:113]

        if  (ligne[3:7] == "Boot"):
            if (ligne[0:3]==" ? "):
            #if (cle_tri > "00099"):  # non cit� dans bootorder -> bootorder en rouge
                resultat.insert("insert", ligne[0:3], 'red')
            else:
                resultat.insert("insert", ligne[0:3], 'black')
            #fin else

            #Bootorder
            if (cle_tri > "00099"):    # non cit� dans bootorder -> bootorder en rouge
                resultat.insert("insert", ligne[3:11], 'red')
            else:
                resultat.insert("insert", ligne[3:11], 'black')
            #fin else

            #libell� toujours en noir
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

            #passage � la ligne
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
            ligne2 = '   MBR en rouge signale un lanceur "MBR" et non EFI. Probl�me probable de partition sur ce disque'
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


    if (separateur == "oui"):  # ========= cas o� aucune ligne de commentaires n a �t� �crite jusque l�, le s�parateur nn plus
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

#======================================fin de la proc�dure d'affichage=======================================

#------------------------------ proc�dure d�clench�e quand on coche la case choix de l'ordre de tri ---------
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
            Bouton_verbeux.config(text="plus d'info ?")
            #largeur_fenetre = 930
            #hauteur_fenetre = 420
        else:
            verbeux="1"
            Bouton_verbeux.config(text="moins d'info ?")
            #largeur_fenetre = 1024
            #hauteur_fenetre = 600
    #bit_bouton=0

    coin_x=window.winfo_x()
    coin_y=window.winfo_y()

    recadrer()

#------------------------------ proc�dure d�clench�e quand bouton recadrer ---------
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

    #--------------------------------------positionnement de resultat � 5 pix sous les boutons
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



#----------------------- proc�dure globale faisant tout le travail-------------------------------------------
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
        print("plantage blkid ou efibootmgr -v avec code retour =", code_retour)

    resultat.delete("1.0", "end")
    resultat.insert("insert", "   current boot = " + global_booCurrent)

    extrac_dev_partUUID_de_blkid()
    extract_efibootmgr()
    croisement_efibootmgr_blkid_selon_UUID()
    affichage()

    # -------------------------------fin faire_ou_refaire_le_boulot _______________________

#-------------------- fin de la proc�dure globale de traitement ---------------------------


#====================================================================================================================

# ------ allocation en m�moire d'un objet tk.tk() qu'on nomme window et qui a les propri�t�s et m�thodes de tk.tk()
#window = tk.Tk()
window.configure(bg="blue")
# ---------------------------------------------------ici
window.resizable(1, 1)

# ------ allocation d'un cadre qui sera ancr� dans window et portera les autres objets
zone = tk.Frame(window, bg='light gray')


# ----------------------------------------------------------------ici
zone.pack(padx=1, pady=1, fill='both', expand=1)

# ------ bouton lan�ant l'actualisation du texte
Bouton_actualise = tk.Button(zone, activebackground="red", bg="cyan", fg="black", command=faire_ou_refaire_le_boulot, width=8,highlightthickness=0)
Bouton_actualise.config(text="actualiser")
Bouton_actualise.pack(padx=2, pady=8, side="top")
Bouton_actualise.place(x=1, y=1)
Bouton_actualise.config(height=1, width=10)

Bouton_verbeux = tk.Button(zone, width=10, command=basculer,relief="flat",highlightthickness=0)
Bouton_verbeux.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black',highlightthickness=0)


if verbeux == "1" :
    Bouton_verbeux.config(text="moins d'info ??")
else:
    Bouton_verbeux.config(text="plus d'info ??")

# ---------------- bouton modif : lance le module ouvrant la fen�tre modif

def popup_creat():
    import tkinter as tk
    import tkinter.ttk as ttk
    index_combo=0
    largeur_wincourante=800
    hauteur_wincourante=150
    win_creat  = tk.Toplevel()		  # Popup -> Toplevel()
    win_creat.transient(window)
    win_creat .title('cr�ation')
    # calcule position x, y




    x = coin_x + (int(largeur_fenetre)/2)  - (int(largeur_wincourante) / 2)
    y = coin_y + (int(hauteur_fenetre)/2) -(int(hauteur_wincourante) / 2) + 100
    win_creat .geometry('%dx%d+%d+%d' % (largeur_wincourante, hauteur_wincourante, x, y))
    win_creat .config(bg="cyan")

    zone1 = tk.Frame(win_creat, bg='light blue')
    zone1.pack(padx=1, pady=1, fill='both', expand=1)
    table_partitions_EFI=[]
    global volume
    volume=""
    global partition
    partition=""
    global libell�_EFI
    libell�_EFI=""
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
        trouve_EFI= str.find(table_partitions[i],"c12a7328-f81f-11d2-ba4b-00a0c93ec93b")   #   str.find retourne -1 si non trouv�

        if (trouve_EFI != -1):   #========= si on a trouv� en bout de ligne "BIOS ou "EFI"
            table_partitions_EFI.append(("/dev/" + table_partitions[i][2:6]))

    # ================================= /dev/sdx  si EFI  mis dans la table table_partitions_EFI

    # ===================================== un_Device_selecte appel�e si �v�nement ComboboxSelected de combo_device.bind
    def un_Device_selecte(eventobject):
        change_choix_device()  # ========= action effectu�e suite � cet �v�nement
    # ================================= fin =================================================================================

    def change_choix_device():
        global index_combo
        global volume
        global partition
        global libell�_EFI
        global path_EFI
        global commande
        label_titre0['text'] = ""
        volume=combo_device.get()[0:8]
        partition=combo_device.get()[8:9]
        #print ("------------------------------" +  libell�_EFI)
        commande="sudo efibootmgr --create --disk "+ volume +" --part "+ partition + " --label " + '"' + libell�_EFI.rstrip(" ") + '"' + " --loader "+ path_EFI.rstrip(" ")
        inter=commande.replace('\\','/')
        commande=inter
        label_commande.configure(text=commande)
        index_combo = combo_device.current()

    def annul_creat():
        win_creat.destroy()

    annuler = tk.Button(zone1, activebackground = "red", bg = "cyan", fg = "black", command = annul_creat, width = 9,highlightthickness=0)
    annuler.config(text="Cancel")
    annuler.pack(padx=2, pady=8, side="top")
    annuler.place(x=674, y=1)
    annuler.config(height=1, width=12)


    def executer_commande():
        global commande
        global volume
        global partition
        global libell�_EFI
        global path_EFI
        if volume=="":
            label_titre0['text'] ="Vous avez oubli� de choisir la partition"
            return
        if (libell�_EFI == "Libell� de l'EFI") or (libell�_EFI == ""):
            label_titre0['text'] ="You forgot the designation of the EFI"
            return
        if (path_EFI == "/EFI/") or (path_EFI == ""):
            label_titre0['text'] = "Vous avez oubli� le libell� de l'EFI"
            return
        commande = "sudo efibootmgr --create --disk " + volume + " --part " + partition + " --label " + '"' + libell�_EFI.rstrip(" ") + '"' + " --loader " + path_EFI.rstrip(" ")
        #print ("la commande va �tre """ + commande )
        code_retour = os.system(commande)
        if code_retour != 0:
            commande=commande + blancs
            print("plantage " + commande[0:30] + "... avec code retour =", code_retour)
            label_titre0['text']="plantage " + commande[0:30] + " avec code retour =" + str(code_retour)
        else:
            faire_ou_refaire_le_boulot()
            win_creat.destroy()

    # ================================ bouton executer et quitter ===================================
    executer = tk.Button(zone1, activebackground = "red", bg = "cyan", fg = "black", command = executer_commande, width = 9,highlightthickness=0)
    executer.config(text="Run & Exit")
    executer.pack(padx=2, pady=8, side="top")
    executer.place(x=1, y=1)
    executer.config(height=1, width=12)
    # ================================= fin bouton executer et quitter ================================

    # ============================ et construit la liste d�roulante des partitions possibles ===========================
    combo_device = ttk.Combobox(zone1, width=10, values=table_partitions_EFI )

    combo_device.place(x=10,y=60)
    combo_device.current(index_combo)
    combo_device.bind("<<ComboboxSelected>>", un_Device_selecte)  # ==action "un_pays_selecte" quand u�v�nement ComboboxSelected
    # ============================ fin liste partitions possibles ===========================
    label_titre0 = tk.Label(zone1, text="", bg='light blue', fg='red', width=66)
    label_titre0.place(x=135, y=0)
    label_titre1 = tk.Label(zone1, text="ESP", bg='light blue', fg='black', width=10)

    label_titre1.place(x=10, y=35)
    label_titre2 = tk.Label(zone1, text="Libell� de l'EFI", bg='light blue', fg='black', width=20, highlightthickness=0)
    label_titre2.place(x=205, y=35)
    label_titre3 = tk.Label(zone1, text="chemin de l'EFI", bg='light blue', fg='black', width=20, highlightthickness=0)
    label_titre3.place(x=540, y=35)
    label_titre4 = tk.Label(zone1, text="Commande qui sera ex�cut�e", bg='light blue', fg='black', width=30)
    label_titre4.place(x=270, y=90)

    value1 = tk.StringVar(zone1)
    value1.set("Label of the EFI")
    entree1 = tk.Entry(zone1, textvariable=value1, width=20, bg="white", fg="black", highlightthickness=0)






    entree1.pack()
    #entree1.place(x=195,y=58)
    entree1.place(x=230, y=58)

    def change_libel_chemin(event):
        global libell�_EFI
        global volume
        global partition
        global commande
        label_titre0['text'] =""
        libell�_EFI=entree1.get()
        if len(libell�_EFI) > 20 :
            label_titre0.configure(text="La longueur du libell� du poste EFI est limit�e � 20 caract�res xxx")
            #value1.set(libell�_EFI[:20])
            value1.set(libell�_EFI[:20])
            return

        commande="sudo efibootmgr --create --disk "+ volume +" --part "+ partition + " --label " + '"' + libell�_EFI.rstrip(" ") + '"' + " --loader "+ path_EFI.rstrip(" ")
        inter=commande.replace('\\','/')
        commande=inter
        label_commande.configure(text=commande)

    # On lie la fonction � l'Entry
    # La fonction sera ex�cut�e � chaque fois que l'utilisateur appuie sur "Entr�e"
    entree1.bind("<KeyRelease>", change_libel_chemin)

    value2 = tk.StringVar(zone1)
    value2.set("/EFI/")
    entree2 = tk.Entry(zone1, textvariable=value2, width=30, bg="white", fg="black", highlightthickness=0 )
    entree2.pack()
    entree2.place(x=500,y=58)

    def change_path_EFI(event):
        global libell�_EFI
        global volume
        global partition
        global path_EFI
        global commande
        label_titre0['text'] = ""
        path_EFI=entree2.get()



        # ici

        # if len(path_EFI) > 30 :
        if len(path_EFI) > 40:
            label_titre0.configure(text="La longueur du chemin du poste EFI est limit�e � 40 caract�res")
            #value1.set(libell�_EFI[:20])
            value2.set(path_EFI[:40])
            return

        commande="sudo efibootmgr --create --disk "+ volume +" --part "+ partition + " --label " + '"' + libell�_EFI.rstrip(" ") + '"' + " --loader "+ path_EFI.rstrip(" ")
        inter=commande.replace('\\','/')
        commande=inter
        label_commande.configure(text=commande)

    # On lie la fonction � l'Entry
    # La fonction sera ex�cut�e � chaque fois que l'utilisateur appuie sur une touche
    entree2.bind("<KeyRelease>", change_path_EFI)
    device_choisi = combo_device.get()
    label_commande = tk.Label(zone1, text=device_choisi, bg='ivory', fg='black', width=97)
    label_commande.place(x=10, y=115)

    win_creat.transient(window) 	  # R�duction popup impossible
    win_creat.grab_set()		  # Interaction avec fenetre window impossible
    window.wait_window(win_creat)   # Arr�t script principal



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

    largeur_wincourante=910
    hauteur_wincourante=205
    win_modif = tk.Toplevel()		  # Popup -> Toplevel()
    win_modif.transient(window)
    win_modif.title('modify')
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
    libell�_EFI = zefi[12:32]
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
        global libell�_EFI
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
        libell�_EFI = zefi[14:34]

        idx = str.find(zefi.casefold(), ".efi")
        idx = idx + 4

# ici

        # chemin = zefi[41:idx]
        chemin = zefi[45:idx]
        label_valeur_ESP.configure(text=bootnum)
        change_libel_chemin(libell�_EFI, chemin)
        value1.set(libell�_EFI.rstrip(" "))
        value2.set(chemin)

        return
    #---------------------------------------------------------------------------------
    def un_boot_selecte(eventobject):
        change_choix_boot()  # ========= action effectu�e suite � cet �v�nement
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
            print ("commande >" + commande1 + "< ex�cut�e")
            faire_ou_refaire_le_boulot()
            print("BootOrder apres ", global_bootorder)
            code_retour = os.system(commande2)
            if code_retour != 0:
                commande2 = commande2 + blancs
                print("plantage " + commande2[0:30] + "... avec code retour =", code_retour)
                label_anomalie['text'] = "plantage " + commande2[0:30] + " avec code retour =" + str(code_retour)
                return
            else:
                print("commande >" + commande2 + "< ex�cut�e")
                faire_ou_refaire_le_boulot()
                print ("BootOrder apres ",global_bootorder)
                code_retour = os.system(commande3)
                if code_retour != 0:
                    commande3 = commande3 + blancs
                    print("plantage " + commande3[0:30] + "... avec code retour =", code_retour)
                    label_anomalie['text'] = "plantage " + commande3[0:30] + " avec code retour =" + str(code_retour)
                    return
                else:
                    print("commande >" + commande3 + "< ex�cut�e")
                    faire_ou_refaire_le_boulot()
                    print("BootOrder apres ", global_bootorder)


        win_modif.destroy()
    # ================================== fin executer commande de suppression ===========================================
    def annuler_modif():
        win_modif.destroy()
    #=============================== bouton annuler =====================================================================
    annuler = tk.Button(zone5, activebackground = "red", bg = "cyan", fg = "black", command = annuler_modif, width = 9,highlightthickness=0)
    annuler.config(text="Annuler")
    annuler.pack(padx=2, pady=8, side="top")
    place=largeur_wincourante - 129
    annuler.place(x=674, y=1)
    annuler.place(x=place, y=1)
    annuler.config(height=1, width=12)
    #================================ fin bouton annuler ================================================================

    # ================================ bouton executer et quitter ===================================
    executer = tk.Button(zone5, activebackground = "red", bg = "cyan", fg = "black", command = executer_commande, width = 9,highlightthickness=0)
    executer.config(text="Ex�cuter & quitter")
    executer.pack(padx=2, pady=8, side="top")
    executer.place(x=1, y=1)
    executer.config(height=1, width=12)
    # ================================= fin bouton executer et quitter ================================

    # ============================ construit la liste d�roulante des EFI presents ===========================
    label_anomalie = tk.Label(zone5, text="", bg='light blue', fg='red', width=78)
    label_anomalie.place(x=135, y=0)

    label_titre2 = tk.Label(zone5, text="Choix de l'�l�ment � modifier", bg='light blue', fg='black', width=30)
    label_titre2.place(x=300, y=20)

    #combo_boot = ttk.Combobox   table_lignes_affichees
    combo_boot = ttk.Combobox(zone5, width=100, values=table_lignes_affichees)
    combo_boot.place(x=40,y=45)
    combo_boot.current(index_combo)
    combo_boot.bind("<<ComboboxSelected>>", un_boot_selecte)  # ==action "un_pays_selecte" quand u�v�nement ComboboxSelected
    # ============================ fin liste partitions possibles ============================================

    label_titre_ESP = tk.Label(zone5, text="Boot", bg='light blue', fg='black', width=4)
    label_titre_ESP.place(x=90, y=80)
    label_valeur_ESP = tk.Label(zone5, text="----", bg='ivory', fg='black', width=4)
    label_valeur_ESP.place(x=130, y=80)

    label_libel_ESP = tk.Label(zone5, text="Libell� ", bg='light blue', fg='black', width=8)
    label_libel_ESP.place(x=165, y=80)

    label_chemin_ESP = tk.Label(zone5, text="chemin ", bg='light blue', fg='black', width=8)
    label_chemin_ESP.place(x=400, y=80)


    value1 = tk.StringVar(zone5)
    value1.set("------------------------------")
    entree1 = tk.Entry(zone5, textvariable=value1, width=20, bg='ivory',highlightthickness=0, fg="black")
    entree1.pack()
    entree1.place(x=230,y=78)

    value2 = tk.StringVar(zone5)
    value2.set("------------------------------")
    entree2 = tk.Entry(zone5, textvariable=value2, width=39, bg='ivory',highlightthickness=0, fg="black")
    entree2.pack()
    entree2.place(x=470,y=78)

    def change_libel_chemin(libell�_EFI,chemin):
        global label_libel_ESP_valeur
        global volume
        global partition
        global commande
        global commande1
        global commande2
        global commande3
        global bootnum
        #global chemin
        #global libell�_EFI
        global table_bootorder
        global global_bootorder
        zefi=combo_boot.get()
        commande2=""
        if len(libell�_EFI) > 20 :
            label_anomalie.configure(text="La longueur du libell� du poste EFI est limit�e � 20 caract�res")
            value1.set(libell�_EFI[:20])
            return




        # ici
        # if len(chemin) > 30 :
        if len(chemin) > 40:
            label_anomalie.configure(text="La longueur du chemin du poste EFI est limit�e � 40 caract�res")
            value2.set(chemin[:30])
            return
        # -------------------------------------------------------------------------
        bootnum = zefi[7:11]
        #idx = str.find(zefi.casefold(), ".efi")
        #idx = idx + 4
        #chemin= zefi[41:idx]
        volume = "/" + zefi[37:45]
        if volume == "/...??...":
            label_anomalie.configure(text="on ne peut pas renommer ce poste car sa localisation est inconnue")
            return

        label_anomalie.configure(text="")
        commande1 = "sudo efibootmgr -b " + bootnum + " -B"
        label_commande.configure(text=commande1)
        commande2 = "sudo efibootmgr -c -d " + volume[0:8] + " -p " + volume[8:9] + ' -L "' + libell�_EFI.rstrip(" ") + '" -l ' + chemin.rstrip(" ")
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
        # ========poste_libre est le numero de bootorder du poste qui sera cr��
        # ========dans la liste BootOrder, il faut le placer en position du poste qui a �t� supprim�
        commande2 = "sudo efibootmgr -c -d " + volume[0:8] + " -p " + volume[8:9] + ' -L "' + libell�_EFI.rstrip(" ") + '" -l ' + chemin.rstrip(" ")
        label_commande2.configure(text=commande2)
        #===== recherche dans BootOrder du rang du poste qui va �tre renomm� (rang avant suppression du poste)
        rang_futur_du_poste_cree=0
        for i in range (0,len(table_bootorder)):
            if bootnum == table_bootorder[i]:
                rang_futur_du_poste_cree=i
                break

        #print ("====rang poste a creer >" + str(rang_futur_du_poste_cree))


        #======= table_bootorder est la liste des postes de BootOrder avant cr�ation du nouveau poste.
        #======= bootnum est la cl� xxxx du poste cr�� bootxxxx, que efibootmgr place en t�te de liste
        #======= du nouveau BootOrder cr�� apr�s cr�ation du nouveau poste xxxx,0007,0003...
        table_bootorder_projet_fin=[]
        # ========== on reconduit les postes avant le nouveau, on injecte le nouveau, et on reconduit les suivants

        #print ("====Cl� bootorder libre >" + Poste_libre)
        #print ("rang poste a creer >" + str(rang_futur_du_poste_cree))
        #print ("===table projet avant insert>",table_bootorder_projet)

        indic_injection = "non"  #========== dans le cas o� c'est le dernier poste qui est modifi�, on ne l'atteindra pas
        for i in range (0,len(table_bootorder_projet)):
            if i < rang_futur_du_poste_cree:
                table_bootorder_projet_fin.append(table_bootorder_projet[i])
            else:
                if i==rang_futur_du_poste_cree :
                    table_bootorder_projet_fin.append(Poste_libre)             #================ injection
                    indic_injection = "oui"   #============ l'injection du poste modifi� a eu lieu
                    table_bootorder_projet_fin.append(table_bootorder_projet[i]) #===== reconduction au rang + 1
                else:
                    #===
                    table_bootorder_projet_fin.append(table_bootorder_projet[i])
                    #================ reconduction
        if indic_injection == "non" :     #========== c'est le cas o� le poste modifi� est en fin de liste
            #print("ajoute >" + Poste_libre + "<")
            table_bootorder_projet_fin.append(Poste_libre)



        commande3="sudo efibootmgr -o "

        # ========== fabrication BootOrder au bout de "sudo efibootmgr -o " par ajout du premier poste puis de "," + poste pour les suivants
        for i in range (0,len(table_bootorder_projet_fin)):
            if i==0:
                commande3 = commande3 + str(table_bootorder_projet_fin[i])          # ====== premier poste non pr�c�d� de virgule
            else:
                commande3 = commande3 + "," +str (table_bootorder_projet_fin[i])
        label_commande3.configure(text=commande3)

        #print ("=======commande3>" +commande3 + "<" )

    def chemin_ou_libel_a_ete_modifie(event):
        libell�_EFI = entree1.get()
        chemin = entree2.get()
        change_libel_chemin(libell�_EFI, chemin)

    # On lie la fonction aux deux Entry. La fonction est ex�cut�e � chaque fois que l'utilisateur appuie sur une touche sur entree1 ou entree2
    entree1.bind("<KeyRelease>", chemin_ou_libel_a_ete_modifie)
    entree2.bind("<KeyRelease>", chemin_ou_libel_a_ete_modifie)
#=================================================================================================================================
    label_titre4 = tk.Label(zone5, text="Commandes qui seront ex�cut�es", bg='light blue', fg='black', width=30)
    label_titre4.place(x=275, y=110)

    label_commande = tk.Label(zone5, text="commande qui sera execut�e", bg='ivory', fg='black', width=111)
    label_commande.place(x=10, y=135)

    label_commande2 = tk.Label(zone5, text="commande qui sera execut�e", bg='ivory', fg='black', width=111)
    label_commande2.place(x=10, y=155)

    label_commande3 = tk.Label(zone5, text="commande qui sera execut�e", bg='ivory', fg='black', width=111)
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
    libell�_EFI = zefi[14:31]
    idx = str.find(zefi.casefold(), ".efi")
    if idx ==-1 :
        idx = str.find(zefi, ".EFI")


    idx = idx + 4
    chemin = zefi[45:idx]


    path_EFI = chemin
    volume = "/" + zefi[37:46]

    if volume == "/...??...":
        label_anomalie.configure(text="on ne peut pas renommer ce poste car sa localisation est inconnue")
        return
    else:
        label_anomalie.configure(text="")
        commande1 = "sudo efibootmgr -b " + bootnum + " -B"
        label_commande.configure(text=commande1)

        commande2 = "sudo efibootmgr -c -d " + volume[0:8] + " -p " + volume[8:9] + ' -L "' + libell�_EFI.rstrip(" ") + '" -l ' + chemin.rstrip(" ")

        label_commande2.configure(text=commande2)

    libell�_EFI=libell�_EFI.rstrip(" ")
    chemin=chemin.rstrip(" ")

    value1.set(libell�_EFI)
    value2.set(chemin)
    label_valeur_ESP.configure(text=bootnum)

    change_libel_chemin(libell�_EFI, chemin)


    win_modif.transient(window) 	  # R�duction popup impossible
    win_modif.grab_set()		  # Interaction avec fenetre window impossible
    window.wait_window(win_modif)   # Arr�t script principal



    # ===================================== un_Device_selecte appel�e si �v�nement ComboboxSelected de combo_device.bind



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
    largeur_wincourante=800
    hauteur_wincourante=150
    win_suppr = tk.Toplevel()		  # Popup -> Toplevel()
    win_suppr.transient(window)
    win_suppr.title('delete')

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
        global libell�_EFI
        global path_EFI
        global commande
        global table_bootnum
        # sudo efibootmgr --create --disk /dev/sdb --part 1 --label "Ubuntu " --loader /EFI/ubuntu/shimx64.efi
        Boot_a_suppr = combo_boot.get()[3:12]
        commande = "sudo efibootmgr -b " + Boot_a_suppr[4:9] + " -B"
        label_commande.configure(text=commande)

    # ===================================== un_Device_selecte appel�e si �v�nement ComboboxSelected de combo_device.bind
    def un_boot_selecte(eventobject):
        change_choix_boot()  # ========= action effectu�e suite � cet �v�nement
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
    annuler = tk.Button(zone2, activebackground = "red", bg = "cyan", fg = "black", command = annuler_suppr, width = 9,highlightthickness=0)
    annuler.config(text="Annuler")
    annuler.pack(padx=2, pady=8, side="top")
    annuler.place(x=674, y=1)
    annuler.config(height=1, width=12)
    #================================ fin bouton annuler ================================================================

    # ================================ bouton executer et quitter ===================================
    executer = tk.Button(zone2, activebackground = "red", bg = "cyan", fg = "black", command = executer_commande, width = 9,highlightthickness=0)
    executer.config(text="Ex�cuter & quitter")
    executer.pack(padx=2, pady=8, side="top")
    executer.place(x=1, y=1)
    executer.config(height=1, width=12)
    # ================================= fin bouton executer et quitter ================================

    # ============================ construit la liste d�roulante des boot presents ===========================
    bb="Boot" + global_booCurrent   # reconstruit le boot current sous la forme Boot0001 par exemple
    table_sauf_bootcurrent=[]
    for i in range (0,len(table_lignes_affichees)):
        if bb in table_lignes_affichees[i]:
            pass    #le bootcurrent n'est pas pr�sent� pour suppression
        else :
            table_sauf_bootcurrent.append(table_lignes_affichees[i])
    combo_boot = ttk.Combobox(zone2, width=95, values=table_sauf_bootcurrent)
    # table_sauf_bootcurrent ne pr�sentera donc pas le bootcurrent pour suppression
    combo_boot.place(x=10,y=65)
    combo_boot.current(index_combo)
    combo_boot.bind("<<ComboboxSelected>>", un_boot_selecte)  # ==action "un_boot_selecte" quand u�v�nement ComboboxSelected
    # ============================ fin liste partitions possibles ============================================

    label_titre0 = tk.Label(zone2, text=" ", bg='light blue', fg='red', width=66)

    label_titre0.place(x=135, y=0)
    label_titre4 = tk.Label(zone2, text="Commande qui sera ex�cut�e", bg='light blue', fg='black', width=30)
    label_titre4.place(x=275, y=90)
    label_titre2 = tk.Label(zone2, text="Choix de l'�l�ment � supprimer", bg='light blue', fg='black', width=30)
    label_titre2.place(x=275, y=35)

    label_commande = tk.Label(zone2, text="commande qui sera execut�e", bg='ivory', fg='black', width=97)
    label_commande.place(x=10, y=115)
    #=========initialisation===============
    boot_choisi = combo_boot.get()
    Boot_a_suppr = combo_boot.get()[3:12]
    commande = "sudo efibootmgr -b " + Boot_a_suppr[4:9] + " -B"
    label_commande.configure(text=commande)

    win_suppr.transient(window) 	  # R�duction popup impossible
    win_suppr.grab_set()		  # Interaction avec fenetre window impossible
    window.wait_window(win_suppr)   # Arr�t script principal

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
    largeur_wincourante=800
    hauteur_wincourante=180

    def quitter():
        win_reorg.destroy()

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

    label_titre0 = tk.Label(zone3, text=" ", bg='light blue', fg='red', width=80)
    label_titre0.place(x=10, y=0)

    label_anc = tk.Label(zone3, text="BootOrder actuel : ", bg='light blue', fg='black', width=17)
    label_anc.place(x=10, y=35)

    Boot_Actuel = tk.Text(zone3, bg='white', fg='black', borderwidth=0, font=("courrier", 9), width=80)
    Boot_Actuel.place(x=150, y=35)
    Boot_Actuel.configure(tabs=('8.45c', 'center'))  # tabulation centr�e � 8 cm du bord gauche

    bricole="\t123456789012345678901234567890"
    Boot_Actuel.configure(height=1, bg="white",highlightthickness=0)

    #Boot_Actuel.insert(tk.END, "\n" + bricole)
    Boot_Actuel.insert("1.1" , bricole)
    Boot_Actuel.delete("1.0", "end")

    Boot_Actuel['state'] = 'disabled'


    label_nouv = tk.Label(zone3, text="BootOrder projet : ", bg='light blue', fg='black', width=17)
    label_nouv.place(x=10, y=60)

    Boot_projet = tk.Text(zone3, bg='white', fg='blue', borderwidth=0, font=("courrier", 9), width=80)
    Boot_projet.place(x=150, y=60)
    Boot_projet.configure(tabs=('8.45c', 'center'))        # tabulation centr�e � 8 cm du bord gauche

    bricole="\t123456789012345678901234567890"
    Boot_projet.configure(height=1, bg="white",highlightthickness=0)

    #Boot_projet.insert(tk.END, "\n" + bricole)
    Boot_projet.insert("1.1" , bricole)
    Boot_projet.delete("1.0", "end")
    Boot_projet['state'] = 'disabled'


    label_choix_poste= tk.Label(zone3, text="choisir un poste � d�placer", bg='light blue', fg='black', width=27)
    label_choix_poste.place (x=200, y=95)

    label_depl = tk.Label(zone3, text="--d�place--", bg='light blue', fg='grey', width=9)
    label_depl.place(x=678, y=120)

    label_commande_sera=tk.Label(zone3, text="la commande sera : ", bg='light blue', fg='grey', width=20)
    label_commande_sera.place(x=5, y=145)
    label_commande_sera.update()
    label_commande=tk.Label(zone3, text="sudo efibootmgr -o xxxx,...", bg='light blue', fg='grey', width=86,anchor='w')
    label_commande.place(x=150, y=145)

    table_bootorder_actu = []
    #   >BootOrder = "BootOrder: 0000,0001,0003,0008,0004,0007"   non reclass�
    inter_char = global_bootorder  # ------- tir� de efibootmgr -v
    caracteres_a_remplacer = (',', '-', '!', '?', 'BootOrder: ')  # --- liste de chaines � remplacer "
    for r in caracteres_a_remplacer:        # pour tout �l�ment "r" de la liste, le remplacer par un blanc
        inter_char = inter_char.replace(r, ' ')
    # inter_char est devenu  "0000 0001 0003 0008 0004 0007"   non reclass�, et sans virgules
    mots = inter_char.split()  # ----- mots est la liste (table) de bootorders

    for x in mots:
        table_bootorder_actu.append(x)  # table_bootorder est la liste des rangs de boot
    # table_bootorder_actu est constitu�e
    BootOrder_actu = ""
    table_bootorder_proj=table_bootorder_actu
    BootOrder_proj=""


    table_Boot_Actuel=[]
    for i in range (0,len(table_bootorder)):
        table_Boot_Actuel.append(str(table_bootorder[i]))

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

    Boot_Actuel['state'] = 'normal'
    Boot_Actuel.delete("1.0", "end")
    Boot_Actuel.insert("1.1", "\t" + zz)
    Boot_Actuel.update()
    Boot_Actuel['state'] = 'disabled'



    table_bootorder_proj=table_bootorder_actu
    zz = compose_ligne_boot_order(table_bootorder_proj)
    Boot_projet['state'] = 'normal'
    Boot_projet.delete("1.0", "end")
    Boot_projet.insert("1.1", "\t" + zz)
    pos1 = Boot_projet.search(global_booCurrent, "1.0", stopindex="end")

    if pos1 == "":
        print("Boot current not in bootorder. Close all and Reboot")
        label_titre0[
            'text'] = "'Boot current' " + global_booCurrent + " n''est pas dans 'bootorder', comment est-ce possible ? Reboot et voyez le Bios"
        # =============================== bouton annuler =====================================================================
        annuler = tk.Button(zone3, activebackground="red", bg="cyan", fg="black", command=quitter, width=9, highlightthickness=0)
        annuler.config(text="Cancel")
        annuler.pack(padx=2, pady=8, side="top")
        annuler.place(x=674, y=1)
        annuler.config(height=1, width=12)
        # ================================ fin bouton annuler ================================================================
        # win_reorg.destroy()
        return
    else:
        pos2 = '%s+%dc' % (pos1, 5)
        Boot_projet.tag_configure('tag_bleu', background='yellow', foreground='red')
        Boot_projet.tag_add("tag_bleu", pos1, pos2)
        Boot_projet.update()
        Boot_projet['state'] = 'disabled'




    #========== tri de table_lignes_affichees selon leur rang dans bootorder
    #suppression des postes qui ne sont pas cit�s dans bootorder. Commencent par  " ? "
    for i in range(0, len(table_lignes_affichees)):
        if table_lignes_affichees[i][0:3] != " ? ":
            table_lignes_citees.append(table_lignes_affichees[i])

    #======================= on commence par affecter � chaque ligne citee son rang dans bootorder (on le note dans table des rangs)
    table_des_rangs= []
    for i in range(0, len(table_lignes_citees)):        # cr�ation de la table des rangs avec "00000" partout
        table_des_rangs.append("00000")
    for i in range (0,len(table_lignes_citees)):
        rng=table_lignes_citees[i][7:11]        # ligne de NVRAM commence par "   Boot" son rang est donc de 7 � 11
        for j in range (0,len(table_bootorder)):
            if rng==table_bootorder[j]:   # la ligne str de NVRAM  a le rang  j dans bootorder
                truc="00000" + str(j)
                table_des_rangs[i]=truc[-5:]    # 5 derniers caract�res de "00000" + str(j)
                #print(table_des_rangs[i])
                pass
        if j >= len(table_bootorder) :   # la ligne de NVRAM de rang rng n'est pas cit�e dans la table bootorder
            table_des_rangs[i] = "99999"

    #====================== tri de table_lignes_affichees selon son rang dans bootorder
    if bit_triEFI == 1 :    # on est dans le cas o� l'affichage des lignes de NVRAM est class� selon leur rang dans bootorder
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


    # ===================================== un_Device_selecte appel�e si �v�nement ComboboxSelected de combo_device.bind
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




    droite = tk.Button(zone3, activebackground="red", bg="light grey", fg="black", command=deplace_droite, width=9,relief="raised",highlightthickness=0)

    text_font = ('Courrier', "12")
    droite.config(text=">")
    droite.pack(padx=1, pady=1, side="top")
    droite.place(x=758, y=112)
    droite.config(height=1, width=1, font=text_font)
    droite.config(state="disabled")

    gauche = tk.Button(zone3, activebackground="red", bg="light grey", fg="black", command=deplace_gauche, width=9,relief="raised",highlightthickness=0)
    gauche.config(text="<")
    gauche.pack(padx=1, pady=1, side="top")
    gauche.place(x=640, y=112)
    gauche.config(height=1, width=1, font=text_font)
    gauche.config(state="disabled")

    # ============================ fin liste partitions possibles ============================================

    text_font=('Courrier', "10")
    liste_boot=ttk.Combobox(zone3,font=text_font,width=75, values=table_lignes_citees)
    liste_boot.place(x=10,y=120)
    liste_boot.update()
    liste_boot.bind("<<ComboboxSelected>>", un_boot_selecte)
    cmd = "sudo efibootmgr -o " + Boot_projet.get('1.0', 'end')
    def executer_commande():
        global cmd

        un=Boot_Actuel.get("1.0","end").lstrip()
        l = len(un) - 1  # un saut de ligne � droite, � enlever
        un = un[0:l]

        deux=Boot_projet.get("1.0","end").lstrip()
        l=len(deux) - 1     # un saut de ligne � droite, � enlever
        deux=deux[0:l]

        if un == deux:
            label_titre0['text']="nothing was done"
            return
        else:
            label_titre0['text'] = ""
        #print ("la commande va �tre """ + cmd )


        code_retour = os.system(cmd)
        if code_retour != 0:
            cmd=cmd + blancs
            print("plantage " + cmd[0:30] + "... avec code retour =", code_retour)
            label_titre0['text']="crash " + cmd[0:50] + " , return code " + str(code_retour)
        else:
            faire_ou_refaire_le_boulot()
            win_reorg.destroy()

    # ================================== fin executer commande de reorg===========================================

    # =============================== bouton annuler =====================================================================
    annuler = tk.Button(zone3, activebackground="red", bg="cyan", fg="black", command=quitter, width=9,highlightthickness=0)
    annuler.config(text="Annuler")
    annuler.pack(padx=2, pady=8, side="top")
    annuler.place(x=674, y=1)
    annuler.config(height=1, width=12)
    # ================================ fin bouton annuler ================================================================

    # ================================ bouton executer et quitter ===================================
    executer = tk.Button(zone3, activebackground="red", bg="cyan", fg="black", command=executer_commande, width=9,highlightthickness=0)
    executer.config(text="Ex�cuter & quitter")
    executer.pack(padx=2, pady=8, side="top")
    executer.place(x=1, y=1)
    executer.config(height=1, width=12)
    # ================================= fin bouton executer et quitter ================================

    win_reorg.transient(window) 	  # R�duction popup impossible
    win_reorg.grab_set()		  # Interaction avec fenetre window impossible
    window.wait_window(win_reorg)   # Arr�t script principal

def popup_quitter():
    print ("et l�, presser la touche entr�e !!!")
    sys.exit()








Bouton_creat = tk.Button(zone, width=8, text="cr�er", command=popup_creat, relief="flat",highlightthickness=0)
Bouton_creat.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black')

Bouton_modif = tk.Button(zone, width=8, text="modifier", command=popup_modif, relief="flat",highlightthickness=0)
Bouton_modif.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black')


Bouton_suppr = tk.Button(zone, width=8, text="supprimer", command=popup_suppr)
Bouton_suppr.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black', relief="flat",highlightthickness=0)

# ------ bouton pour modifier BootOrder
Bouton_order = tk.Button(zone, width=8, text="Reorg Order", command=popup_ordre, relief="flat",highlightthickness=0)
Bouton_order.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black')



Bouton_quitter = tk.Button(zone, width=8, text="fin", command=popup_quitter)
Bouton_quitter.config(bg='cyan', fg='black', activebackground='red', activeforeground='black',highlightthickness=0)




# ------ checkbox (case � cocher) pour choisir l'ordre d'affichage des lignes EFI naturel ou selon bootorder
chk_triEFI: Checkbutton = tk.Checkbutton(zone, width=16, text="Tri� / BootOrder", bd=4 , var=chk_triEFI, command=chk_triEFI)
chk_triEFI.config(bg='light grey', fg='black', activebackground='grey', activeforeground='black', selectcolor="white",highlightthickness=0)
chk_triEFI.select()
chk_triEFI.pack(padx=3, pady=10, side="top")






# ------- zone de texte contenant la liste des postes EFI obtenus par "sudo efibootmgr -v" compl�t�e
from tkinter import scrolledtext



#-----------------------------------------------------ici
#resultat = scrolledtext.ScrolledText(zone1, wrap=tk.WORD,
resultat = scrolledtext.ScrolledText(zone, wrap=tk.WORD, background="light cyan", foreground="black")
resultat.vbar.configure(bg="light cyan", activebackground="cyan")

resultat.place(x=0, y=35,)

resultat.pack(fill='both')

#-----------------------------------------ici
from threading import Timer


def actualise_coins(event):
    global coin_x
    global coin_y

    coin_x=window.winfo_x()
    coin_y=window.winfo_y()

def resize(event):
    global largeur_fenetre
    global hauteur_fenetre
    global LargeurScreen
    global HauteurScreen
    global coin_x
    global coin_y

    coin_x=window.winfo_x()
    coin_y=window.winfo_y()

    t = Timer(0.005, Timer_souris)
    t.start()

    largeur_fenetre = window.winfo_width()
    hauteur_fenetre = window.winfo_height()
    LargeurScreen = window.winfo_screenwidth()
    HauteurScreen = window.winfo_screenheight()


zone.bind("<Configure>", resize)
window.bind("<Configure>",actualise_coins)
#-------------------------------------------------ici




def Timer_souris():
    global coin_x, coin_y
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
if os.path.exists(dir_travail + "/blkid.txt"):  # supprime le fichier r�sidu �ventuel
    os.remove(dir_travail + "/blkid.txt")

if os.path.exists(dir_travail + "/efiboot.txt"):  # supprime le fichier r�sidu �ventuel
    os.remove(dir_travail + "/efiboot.txt")

print ("---------------------termin�----------------------------------")
#--------------------------------fin du programme--------------------------------------






