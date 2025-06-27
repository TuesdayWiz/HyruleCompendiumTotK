# Imports the necessary libraries
from requests import get
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import Tk, Toplevel, Canvas
from tkinter.ttk import Button, Label, Frame
from json import load

# TODO: Fix the "Treasures" screen

ids = {}
with open('ids.json', 'r') as i_file:
    ids = load(i_file)

#Sets up the tkinter window
root = Tk()
root.title('Hyrule Compendium - Tears of the Kingdom')
root.iconbitmap('compendium.ico')   # Icon by Sympnoiaicon on Flaticon.com

# Sets up the grid for use in positioning
mainframe = Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=('n', 'w', 'e', 's'))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Global widgets
title = Label(mainframe, text="Hyrule Compendium", justify="center", font=("Courier New", 20, "bold"))

# Start screen widgets
catCreatures = Button(mainframe, text="Creatures", command=lambda: change_screen(1, 'creatures'))
catMonsters = Button(mainframe, text="Monsters", command=lambda: change_screen(1, 'monsters'))
catMaterials = Button(mainframe, text="Materials", command=lambda: change_screen(1, 'materials'))
catEquipment = Button(mainframe, text="Equipment", command=lambda: change_screen(1, 'equipment'))
catTreasure = Button(mainframe, text="Treasure", command=lambda: change_screen(1, 'treasure'))
catAll = Button(mainframe, text="All", command=lambda: change_screen(1))
# TODO: Figure out the size of the buttons

# Compendium widgets
button1 = Button(mainframe, command=lambda: show_entry(1))
button2 = Button(mainframe, command=lambda: show_entry(2))
button3 = Button(mainframe, command=lambda: show_entry(3))
button4 = Button(mainframe, command=lambda: show_entry(4))
button5 = Button(mainframe, command=lambda: show_entry(5))
button6 = Button(mainframe, command=lambda: show_entry(6))
button7 = Button(mainframe, command=lambda: show_entry(7))
button8 = Button(mainframe, command=lambda: show_entry(8))
backButton = Button(mainframe, text="<--", command=lambda: change_page(False))
homeButton = Button(mainframe, text="Home", command=lambda: change_screen(0))
forwardButton = Button(mainframe, text="-->", command=lambda: change_page(True))
pageNumLabel = Label(mainframe, text='1')
# TODO: Figure out sizes for the buttons

# Global variables
pageNum = 0     # Page number, used to calculate IDs (COUNTS FROM 0)
offset = 0      # Offsets from the beginning of the ID list, used to calculate IDs
maxPages = 0    # Maximum number of pages to show, used in the logic for the page scrolling buttons (COUNTS FROM 0)
leftovers = 0   # Number of buttons on the final page that will be unused, used to disable those buttons (COUNTS FROM 1)
buttons = [button1, button2, button3, button4, button5, button6, button7, button8]

# Sets up the classes for the different entry types
class entry:
    """Master class for inheritance
    """
    def __init__(self, category:str, common_locations:list, description:str, dlc:bool, id:int, image_link:str, name:str):
        self.category = category
        self.common_locations = common_locations
        self.description = description
        self.dlc = dlc
        self.id = id
        self.image_link = image_link
        self.name = name
    
    def __str__(self):
        return f"{self.name} (ID {self.id})"

class Creature(entry):
    def __init__(self, category:str, common_locations:list, description:str, dlc:bool, id:int, image_link:str, name:str, drops:list, edible:bool):
        entry.__init__(self, category, common_locations, description, dlc, id, image_link, name)
        self.drops = drops
        self.edible = edible

class Equipment(entry):
    def __init__(self, category:str, common_locations:list, description:str, dlc:bool, id:int, image_link:str, name:str, properties:dict):
        entry.__init__(self, category, common_locations, description, dlc, id, image_link, name)
        self.properties = properties

class Material(entry):
    def __init__(self, category:str, common_locations:list, description:str, dlc:bool, id:int, image_link:str, name:str, cooking_effect:str, fuse_attack_power:int, hearts_recovered:float):
        entry.__init__(self, category, common_locations, description, dlc, id, image_link, name)
        self.cooking_effect = cooking_effect
        self.fuse_attack_power = fuse_attack_power
        self.hearts_recovered = hearts_recovered

class Monster(entry):
    def __init__(self, category:str, common_locations:list, description:str, dlc:bool, id:int, image_link:str, name:str, drops:list):
        entry.__init__(self, category, common_locations, description, dlc, id, image_link, name)
        self.drops = drops

class Treasure(entry):
    def __init__(self, category:str, common_locations:list, description:str, dlc:bool, id:int, image_link:str, name:str, drops:list):
        entry.__init__(self, category, common_locations, description, dlc, id, image_link, name)
        self.drops = drops

def get_entry(id:int):
    """Gets the data of the requested entry

    Args:
        id (int): the item ID of the requested item

    Returns:
        obj: an object containing all of the data for a given entry, with the object type corresponding to its category
    """
    url = f"https://botw-compendium.herokuapp.com/api/v3/compendium/entry/{id}?game=totk"
    data = get(url).json()['data']

    if data['category'] == "creatures":
        return Creature(data['category'], data['common_locations'], data['description'], data['dlc'], data['id'], data['image'], data['name'], data['drops'], data['edible'])
    elif data['category'] == "monsters":
        return Monster(data['category'], data['common_locations'], data['description'], data['dlc'], data['id'], data['image'], data['name'], data['drops'])
    elif data['category'] == "materials":
        return Material(data['category'], data['common_locations'], data['description'], data['dlc'], data['id'], data['image'], data['name'], data['cooking_effect'], data['fuse_attack_power'], data['hearts_recovered'])
    elif data['category'] == "equipment":
        return Equipment(data['category'], data['common_locations'], data['description'], data['dlc'], data['id'], data['image'], data['name'], data['properties'])
    elif data['category'] == "treasure":
        return Treasure(data['category'], data['common_locations'], data['description'], data['dlc'], data['id'], data['image'], data['name'], data['drops'])
    else:
        return "Invalid item"

def change_page(pos:bool):
    """Changes the "page" of entries and handles the enabling and disabling of buttons

    Args:
        pos (bool): if the page num should be added to or subtracted from
    """
    global buttons
    global pageNum
    global maxPages
    buttonsR = [button8, button7, button6, button5, button4, button3, button2, button1]
    
    if pos: # Going forward a page
        if pageNum == maxPages:
            pageNum = 0
        else:
            pageNum += 1
    else:   # Going back a page
        if pageNum == 0:
            pageNum = maxPages
        else:
            pageNum -= 1

    if pageNum == maxPages:
        # Disables all unneeded buttons on the last page
        for b in range(leftovers):
            buttonsR[b].config(text="", state='disabled')
        
        # Updates the rest of the buttons
        for c in range(8 - leftovers):
            buttons[c].config(text=ids[str(offset + (8 * pageNum) + c + 1)], state='normal')
    else:
        # Enables all buttons on every page but the last
        for b in range(len(buttons)):
            buttons[b].config(text=ids[str(offset + (8 * pageNum) + b + 1)], state='normal')
    
    # Updates the page number on the bottom of the screen
    pageNumLabel.config(text=f"Page {pageNum + 1}")

    # Makes sure all graphical changes are processed before the screen changes
    root.update()

def change_screen(screenNum:int, category:str=None):
    """Changes the widgets in the window, as if there were different screens

    Args:
        screenNum (int): The ID of the screen (0 = start, 1 = compendium)
        category (str, optional): The category to load, if changing to screen 1, defaults to None (all entries)
    """
    # Removes all current widgets
    for widget in mainframe.winfo_children():
        widget.grid_forget()
    
    # Shows widgets and, if needed, sets variables
    if screenNum == 0:      # Start screen
        catCreatures.grid(row=1, column=0)
        catMonsters.grid(row=1, column=1)
        catMaterials.grid(row=1, column=2)
        catEquipment.grid(row=2, column=0)
        catTreasure.grid(row=2, column=1)
        catAll.grid(row=2, column=2)

        title.grid(row=0, column=0, columnspan=3)
    elif screenNum == 1:    # Compendium screen
        global offset
        global maxPages
        global leftovers
        global pageNum
        
        if category == "creatures":
            offset = 0
            maxPages = 11
            leftovers = 4
        elif category == "monsters":
            offset = 92
            maxPages = 13
            leftovers = 2
        elif category == "materials":
            offset = 202
            maxPages = 15
            leftovers = 2
        elif category == "equipment":
            offset = 328
            maxPages = 21
            leftovers = 1
        elif category == "treasure":
            offset = 503
            maxPages = 0
            leftovers = 2
        else:   # All entries
            offset = 0
            maxPages = 63
            leftovers = 3
        
        pageNum = 0
        pageNumLabel.config(text=f"Page {pageNum + 1}")

        button1.grid(row=1, column=0)
        button2.grid(row=1, column=1)
        button3.grid(row=1, column=2)
        button4.grid(row=1, column=3)
        button5.grid(row=2, column=0)
        button6.grid(row=2, column=1)
        button7.grid(row=2, column=2)
        button8.grid(row=2, column=3)

        for b in range(len(buttons)):
            buttons[b].config(text=ids[str(offset + (8 * pageNum) + b + 1)], state='normal')

        if maxPages > 1:
            backButton.grid(row=3, column=0)
            pageNumLabel.grid(row=4, column=0, columnspan=4)
            forwardButton.grid(row=3, column=3)
        
        homeButton.grid(row=3, column=1, columnspan=2)
        title.grid(row=0, column=0, columnspan=4)

def friendly_name(unfriendly:str):
    """Captalizes the first letter of every word in a string

    Args:
        unfriendly (str): A string with un-capitalized words

    Returns:
        str: A string with capitalized words
    """
    
    friendly = ''
    parts = unfriendly.split(' ')
    if len(parts) > 1:
        for p in parts:
            friendly = friendly + p.capitalize() + ' '
    else:
        friendly = unfriendly.capitalize()
    
    return friendly

def show_entry(buttonNum:int):
    """Creates a pop-up window that gives the user information about an entry

    Args:
        buttonNum (int): The ID of the button that was pressed
    """
    buttonID = offset + (8 * pageNum) + buttonNum
    thing = get_entry(buttonID)
    
    if thing == 'Invalid item':
        print("Something went wrong!  Please try again later!")
        return

    e_name = friendly_name(thing.name)
    e_category = f"Category: {friendly_name(thing.category)}"
    e_desc = thing.description
    e_id = f"ID: {thing.id}"
    
    e_photoImage = ImageTk.PhotoImage(Image.open(BytesIO(get(thing.image_link).content)))
    
    e_locations = 'Common locations: '
    if thing.common_locations:
        if len(thing.common_locations) == 1:
            e_locations = e_locations + thing.common_locations[0]
        elif len(thing.common_locations) > 1:
            for loc in thing.common_locations:
                e_locations = e_locations + f"{loc}, "
            e_locations = e_locations[0:-2]
    else:
        e_locations = e_locations + "None"
    
    e_dlc = 'DLC: '
    if thing.dlc:
        e_dlc = e_dlc + "Yes"
    else:
        e_dlc = e_dlc + "No"
    
    e_extra1 = ''
    e_extra2 = False
    e_extra3 = False
    if type(thing) is Equipment:
        attack = thing.properties['attack']
        defense = thing.properties['defense']
        effect = thing.properties['effect']
        e_type = friendly_name(thing.properties['type'])

        if len(effect) == 0:
            effect = "None"

        e_extra1 = f"Attack: {attack}\nDefense: {defense}\nEffect: {effect}\nType: {e_type}"
    elif type(thing) is Material:
        if len(thing.cooking_effect) == 0:
            e_extra1 = "Cooking Effect: None"
        else:
            e_extra1 = f"Cooking Effect: {friendly_name(thing.cooking_effect)}"
        
        e_extra2 = f"Fuse attack power: {thing.fuse_attack_power}"

        e_extra3 = f"Hearts recovered: {thing.hearts_recovered}"
    else:
        if len(thing.drops) == 0:
            e_extra1 = "Drops: None"
        elif len(thing.drops) == 1:
            e_extra1 = f"Drops: {friendly_name(thing.drops[0])}"
        else:
            e_extra1 = "Drops: "
            for d in thing.drops:
                e_extra1 = e_extra1 + f"{friendly_name(d)}, "
            e_extra1 = e_extra1[0:-2]
        
        if type(thing) is Creature:
            if thing.edible:
                e_extra2 = "Edible"
            else:
                e_extra2 = "Not edible"
    
    # Sets up the sub-window that shows the information
    info = Toplevel(root)
    info.title = e_name
    info.iconbitmap('icon.ico')
    info.columnconfigure(0, weight=1)
    info.rowconfigure(0, weight=1)
    infoframe = Frame(info, padding="3 3 12 12")
    infoframe.grid(row=0, column=0, sticky=('n', 'w', 'e', 's'))

    def close_window():
        """Closes the info window
        """
        info.destroy()
    
    # Have to do this or else the image is garbage collected
    info.e_photoImage = e_photoImage

    # Widgets for info window
    imageCanvas = Canvas(infoframe, width=280, height=280, background='white')
    nameLabel = Label(infoframe, text=e_name)
    descLabel = Label(infoframe, text=e_desc, wraplength=200)
    catLabel = Label(infoframe, text=e_category)
    locLabel = Label(infoframe,text=e_locations, wraplength=200)
    idLabel = Label(infoframe, text=e_id)
    dlcLabel = Label(infoframe, text=e_dlc)
    extraLabel1 = Label(infoframe, text=e_extra1)
    extraLabel2 = Label(infoframe)
    extraLabel3 = Label(infoframe)
    exitButton = Button(infoframe, text="Close", command=lambda: info.destroy())

    imageCanvas.create_image(140, 140, image=e_photoImage)

    imageCanvas.grid(row=0, column=0, columnspan=2)
    nameLabel.grid(row=1, column=0)
    descLabel.grid(row=1, column=1)     # TODO: Line wrapping
    catLabel.grid(row=2, column=0)
    locLabel.grid(row=2, column=1)
    idLabel.grid(row=3, column=0)
    dlcLabel.grid(row=3, column=1)
    extraLabel1.grid(row=4, column=0)
    exitButton.grid(row=6, column=0, columnspan=2)
    
    if e_extra2:
        extraLabel2.config(text=e_extra2)
        extraLabel2.grid(row=4, column=1)
    if e_extra3:
        extraLabel3.config(text=e_extra3)
        extraLabel3.grid(row=5, column=1)

# Calls the main loop of the root window
change_screen(0)
root.mainloop()