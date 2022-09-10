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

The used "efibootmgr" commands are displayed at the bottom of each window before being executed.

==== Setup :  
in any folder, copy the efibootmgr_Us.bash script and the python script efibootmgr_Us.py. In the efibootmgr_Us.bash script, change the name of the folder containing these two files (change "python3 /home/bernard/.Scripts/efibootmgr_Us.py" to "python3 /home/your folder/efibootmgr_Us.py".
And then, create a launcher on the desktop that launches the efibootmgr_Us.bash script in a terminal.
There are also two icons that may be useful to you, EFI.png and efibootmgr_sdx.png.
The program requires python3, python3-tk

As I'm a casual programmer, be indulgent and modify this program as you wish if you are able. It works on ASUS PC with Debian and Mint as well as Old Apple with Mint and Kubuntu.



![screenshot_a](https://user-images.githubusercontent.com/111367455/185114243-e16fbb3d-427c-4ec6-8b80-0efa94fbbe4a.png)


![screenshot_b](https://user-images.githubusercontent.com/111367455/185114276-87b7e71e-9220-4928-9d50-30bef5a1066d.png)

![screenshot_f](https://user-images.githubusercontent.com/111367455/189486817-ca9d1ca8-9a46-47da-9567-2af5ceb9e99f.png)
