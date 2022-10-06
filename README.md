# Supercell-DL-SC-Editor
 A tool to edit animations (for now just sprites) for _dl.sc files from Supercell games like Clash Royale, Hayday, Clash of Clans, Brawl Stars, Boom Beach, etc.

 This was partially ported from https://github.com/jeanbmar/Ultrapowa-SC-Editor

 as well as some code borrowed from https://github.com/Vorono4ka/XCoder and https://github.com/Vorono4ka/sc-compression thank you!

 As of right now this editor is basically only capable of the things the Ultrapowa editor is capable of but it will run on any device unlike ultrapowa (only runs windows)
 
 I have found out there will be an editor coming from SCW Make which is far superior to this one. This was ported in 1 week so feel free to do with it as you like, but I suggest using the better editor!

## Known Bugs:

 - Exporting a chunk image on MacOS and selecting a file that is not a PNG totally crashes the program. This is a weird bug with tkinter and MacOS

## Features:

 - Export chunk image
 - Replace chunk image (Uses shape mask so cannot extend bounds of chunk image)
 - View movieclips, their shapes & shape chunks, as well as textures.

## Command line tool usage:
 To use simply just run `python command_line_tools.py -path-to-sc`

 with arguments either `--export` to get the texture or `--importpng path` to import a texture

## GUI Usage
 Run the program with `python main.py` and from there you can open an _dl.sc file and edit it.

Got some stuff to help me out? Shoot a friend request to Blaki#4254 on discord
