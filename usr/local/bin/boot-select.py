#!/usr/bin/env python3

import os
import subprocess
import gi
import threading
import time
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

# message i18n
title = "Program execution permission error"
text = "This program requires root privileges to run."
text1 = "Select the menu you want to boot from with the arrow keys and press Enter."
column1 = "Bootable menu list"
text2 = "Do you want to set it as default?\n\nIf you click Yes, the system will be restarted automatically.\n\nPlease save all the data you are working on."
progress_text = "Applying settings and rebooting..."
btn_text = "Set Default and Reboot"

# i18n based on LANG environment variable
lang = os.getenv('LANG', '')
if lang.startswith('ko'):
    title = "프로그램 실행 권한 오류"
    text = "이 프로그램은 실행을 위해서 루트 권한이 필요합니다."
    text1 = "부팅을 원하는 메뉴를 선택 후 하단의 버튼을 클릭하세요"
    column1 = "부팅 가능한 메뉴들"
    text2 = "을 기본으로 설정하시겠습니까?\n\nYes 를 누르시면 시스템이 자동으로 재시작 됩니다.\n\n작업중인 데이터를 모두 저장하시기 바랍니다."
    progress_text = "설정을 적용하고 재시작 중입니다..."
    btn_text = "저장 후 시스템 재시작"

# Check for root permission
if os.geteuid() != 0:
    dialog = Gtk.MessageDialog(
        parent=None,
        modal=True,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=text
    )
    dialog.set_title(title)
    dialog.run()
    dialog.destroy()
    exit(1)

# Function to parse grub.cfg and return menu entries
def parse_grub_cfg():
    grub_cfg_path = "/boot/grub/grub.cfg"
    menu_entries = []
    hide_upstart_recovery = False

    skipped_menu_entry = False
    in_submenu = False
    in_menu_entry = False
    next_menu_entry_no = 0
    this_submenu_major_no = 0
    next_submenu_minor_no = 0
    curr_tag = ""
    curr_text = ""

    with open(grub_cfg_path, 'r') as grub_cfg:
        for line in grub_cfg:
            line = line.strip()
            black_line = "".join(line.split())

            if black_line == "}":
                if skipped_menu_entry:
                    next_submenu_minor_no += 1
                    skipped_menu_entry = False
                    continue
                if in_menu_entry:
                    in_menu_entry = False
                    if in_submenu:
                        next_submenu_minor_no += 1
                    else:
                        next_menu_entry_no += 1
                elif in_submenu:
                    in_submenu = False
                    next_menu_entry_no += 1
                else:
                    continue
                curr_text = curr_text[:68]
                menu_entries.append((curr_tag, curr_text))

            if line.startswith("submenu"):
                in_submenu = True
                this_submenu_major_no = next_menu_entry_no
                next_submenu_minor_no = 0
                curr_tag = next_menu_entry_no
                curr_text = line.split("'")[1]
                menu_entries.append((curr_tag, curr_text))

            elif line.startswith("menuentry") and "{" in line:
                if hide_upstart_recovery:
                    if "(upstart)" in line or "(recovery mode)" in line:
                        skipped_menu_entry = True
                        continue
                in_menu_entry = True
                if in_submenu:
                    curr_tag = f"{this_submenu_major_no}>{next_submenu_minor_no}"
                else:
                    curr_tag = next_menu_entry_no
                curr_text = line.split("'")[1]

    return menu_entries

# Function to set default grub entry
def set_default_grub_entry(default_item, progress_bar, window):
    def run_tasks():
        tasks = [
            ('sudo', 'sed', '-i', '/GRUB_DEFAULT=/d', '/etc/default/grub'),
            ('sudo', 'sed', '-i', '/GRUB_SAVEDEFAULT=/d', '/etc/default/grub'),
            ('sudo', 'sed', '-i', '/GRUB_TIMEOUT=/d', '/etc/default/grub'),
            ('sh', '-c', 'echo "GRUB_DEFAULT=saved" | sudo tee -a /etc/default/grub'),
            ('sh', '-c', 'echo "GRUB_SAVEDEFAULT=true" | sudo tee -a /etc/default/grub'),
            ('sh', '-c', 'echo "GRUB_TIMEOUT=5" | sudo tee -a /etc/default/grub'),
            ('sudo', 'update-grub'),
            ('sudo', 'grub-set-default', str(default_item)),
            ('sudo', 'reboot')
        ]

        for i, task in enumerate(tasks):
            subprocess.run(task)
            GLib.idle_add(progress_bar.set_fraction, (i + 1) / len(tasks))
            time.sleep(0.5)

    window.set_sensitive(False)
    progress_window = Gtk.Window(title=progress_text)
    progress_window.set_border_width(10)
    progress_window.set_default_size(300, 100)
    progress_window.set_position(Gtk.WindowPosition.CENTER)
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    progress_window.add(vbox)

    label = Gtk.Label(label=progress_text)
    vbox.pack_start(label, True, True, 0)

    vbox.pack_start(progress_bar, True, True, 0)

    progress_window.show_all()

    threading.Thread(target=run_tasks).start()

# Function to create the main GTK window
def create_main_window():
    menu_entries = parse_grub_cfg()

    print("Parsed menu entries:")  # Debugging print
    for entry in menu_entries:
        print(entry)  # Debugging print

    window = Gtk.Window(title="Boot Menu Selector")
    window.set_border_width(10)
    window.set_default_size(600, 400)
    window.set_position(Gtk.WindowPosition.CENTER)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    window.add(vbox)

    label = Gtk.Label(label=text1)
    vbox.pack_start(label, True, True, 0)

    liststore = Gtk.ListStore(str, str)
    for i, entry in enumerate(menu_entries):
        liststore.append([str(entry[0]), entry[1]])

    treeview = Gtk.TreeView(model=liststore)

    # Set the column titles
    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("No", renderer, text=0)
    treeview.append_column(column)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn(column1, renderer, text=1)
    treeview.append_column(column)

    # Add TreeView to ScrolledWindow
    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.set_min_content_height(300)
    scrolled_window.set_min_content_width(580)
    scrolled_window.add(treeview)
    vbox.pack_start(scrolled_window, True, True, 0)

    button = Gtk.Button(label=btn_text)
    button.connect("clicked", on_button_clicked, treeview, window)
    vbox.pack_start(button, True, True, 0)

    window.connect("destroy", Gtk.main_quit)
    window.connect("key-press-event", on_key_press_event, button)
    window.show_all()

def on_button_clicked(button, treeview, window):
    selection = treeview.get_selection()
    model, treeiter = selection.get_selected()
    if treeiter is not None:
        choice = model[treeiter][0]
        choice_text = model[treeiter][1]
        dialog = Gtk.MessageDialog(
            parent=None,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"\"{choice_text}\" {text2}"
        )
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            progress_bar = Gtk.ProgressBar()
            set_default_grub_entry(choice, progress_bar, window)

def on_key_press_event(widget, event, button):
    if event.keyval == Gdk.KEY_Return:
        button.clicked()

if __name__ == "__main__":
    if not Gtk.init_check()[0]:
        print("Failed to initialize GTK")
        exit(1)

    create_main_window()
    Gtk.main()
