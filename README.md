# EFI BIOS NVRAM MultiBoot (Python linux to easy create, modify, delete, reorder  launchers in NVRAM for EFI-BIOS systems)
==== preamble : Here are a few explanations (to my knowledge) about the starting up  of  the computers known as UEFI or EFI BIOS.

On any mother board there is a memory which is not erased  even after the computer shuts down. This non volatile memory is often called NVRAM : acronym for Non Volatile Random Access Memory.

Among other things, that memory contains : 
A table of which every row can indicate the name of a program that is launched immediately before the activation of any OS (windows, Linux…) and also the physical unit in which the program is (UUID of its partition) and also, in that  unit, the path which leads to it and its file name (for instance /EFI/ubuntu/shimx64.efi)

It also contains a table which indicates in what order the rows of the previous table must be browsed so as to  decide which sytem must be launched first, then secondly in case the first one fails, then  thirdly and so on.

On quality mother boards, the BIOS is intelligent enough to offer, in graphical display,  the tools enabling to create or modify rows of the first table and reorder BootOrder. But on basic or ancient systems , that tool is either rudimentary or missing. In that case, the tables can only be modified by a program loaded from a CD or a bootable USB key.

==== Aim of  the present program ==================================

As the bios program can only read the FAT partitions whose flag is ESP or EFI, the program presents only those units in the "sda1, sdb1, sdc2.…" form, according to the Linux convention.

It enables one to create, modify, suppress rows from the table which contains the OS starting up programs and also to modify the classification on the Bootorder table.
In fact, according to the indications it receives from the user and to the NVRAM content, it composes and launches the "efibootmgr" commands which could have been (on Linux) laboriously created manually in a terminal to reach the same result.
====================================================================================================================================
The used "efibootmgr" commands are displayed at the bottom of each window before being executed. 
Setup :  use python3 scripts efibootmgr_Us.py (or efibootmgr_Fr.py), or use the standalone version efibootmgr_Us (or efibootmgr_Fr)
Python3 script :
in any folder, copy the efibootmgr_Us.bash script and the python script efibootmgr_Us.py. In the efibootmgr_Us.bash script, change the name of the folder containing these two files (change "python3 /home/bernard/.Scripts/efibootmgr_Us.py" to "python3 /home/your folder/efibootmgr_Us.py".
And then, create a launcher on the desktop that launches the efibootmgr_Us.bash script in a terminal (mandatory).
There are also two icons that may be useful to you, EFI.png and efibootmgr_sdx.png.
The program requires python3, python3-tk
Standalone release :
in any folder, copy the efibootmgr_Us program.  
create a launcher on the desktop that launches the efibootmgr_Us standalone program in a terminal (mandatory). You can use efibootmgr_nvram.png as icon.
=====================================================================================================================================
Screenshots :
screenshot_01.png montre ce que fournit comme informations la commande "sudo efibootmgr -v".
On remarque que pour chaque poste "lanceur" présent en NVRAM, elle donne (pour les, lanceurs des systèmes qui nous intéressent):
- son rang dans la table NVRAM en notation hexadécimale de 4 chiffres, préfixé de "Boot" ("Boot0000, Boot0001... Boot000A...")
- sa désignation ("Windows boot manager", "ubuntu", "debian"...)
- sa localisation 
    HD pour HDD
    géométrie du disque GPT, MBR
    partition 1,2 etc 
    UUID de la partition (cff17f30-8ef7.....) impossible à saisir sans faire d'erreur
    le chemin dans la partition identifiée par cet UUID \EFI\UBUNTU\GRUBX64.EFI,  \EFI\DEBIAN\GRUB64.EFI...
et la table Bootorder qui liste les postes à prendre en compte lors du boot 0000,0004,0005,0001...(le premier, puis le second 
en cas d'impossibilité, etc 

Par contre, ce même programme efibootmgr, quand on désire manipuler les postes de la table (créer, modifier, ...) exige
qu'on utilise la notation linux (sda, sdb, plus numéro de partition donc sda1, sda2, sdb1...
Ce n'est pas très commode et c'est source d'erreur (grave dans la mesure où on peut dénaturer ou supprimer le poste
qui lançait votre système préféré.
Le programme Linux Python3 efibootmgr_Us.py (ou efibootmgr_Fr) rassemble les informations fournies par les programmes en lignes
de commande efibootmgr et blkid, et en fait une synthèse sous forme de GUI plus conviviale, exposée dans les images suivantes :
screenshot_a.png,   reclassement des postes dans bootorder et par conséquent, changement éventuel de boot loader
screenshot_b.png,   modification d'un poste de la table des lanceurs de la NvRam
screenshot_c.png,   création d'un nouveau poste dans la table des lanceurs
screenshot_d.png,   suppression d'un poste dans la table des lanceurs
screenshot_e.png    affichage d'informations concernant l'EFI Boot et la NvRam
screenshot_f.png    installation de BootNext, qui permet d'utiliser le lanceur choisi pour une fois seulement, avec retour à l'état initial au boot suivant 
screenshot_g.png    suppression de BootNext

![screenshot_01](https://user-images.githubusercontent.com/111367455/190638776-7b3ac1ac-4320-49af-b44a-51dd691c5cfe.png)
![screenshot_a](https://user-images.githubusercontent.com/111367455/190638791-46118db8-3fb4-4139-ad7a-9ebf4e8313d6.png)
![screenshot_b](https://user-images.githubusercontent.com/111367455/190638803-84175974-9558-4d94-9b87-41e12ba92ea8.png)
![screenshot_c](https://user-images.githubusercontent.com/111367455/190638848-0ff8515e-7006-47ac-bf75-e97a584fbad7.png)
![screenshot_d](https://user-images.githubusercontent.com/111367455/190638876-79de50a6-08c7-4aff-8170-12d3c40da29c.png)
![screenshot_e](https://user-images.githubusercontent.com/111367455/190638884-8dcc1393-db61-4546-bfc0-4c54b78d6e63.png)
![screenshot_f](https://user-images.githubusercontent.com/111367455/190638896-0ead358f-e113-45a5-a123-e0c3cf7a0aa8.png)
![screenshot_g](https://user-images.githubusercontent.com/111367455/190638916-424a0aa9-ba18-4a72-a7f0-83ec9ff2934f.png)
