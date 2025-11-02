from fileinput import filename
from idlelib.outwin import file_line_pats

from customtkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog
import base64
import io
import os
import threading
from socket import socket, AF_INET, SOCK_STREAM




class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('600x400')
        self.title('Logitalk')
        self.configure(fg_color="#FAEBD7")
        self.is_menu_shown = False
        self.menu_animate_speed = -5

        self.username = "sdsdsdsd"
        self.avatar_image = None

        self.menu_frame = CTkFrame(self, width=30, height=400)
        self.menu_frame.configure(fg_color="#FAEBD7", corner_radius=0)
        self.menu_frame.place(x=0, y=0)

        self.menu_btn = CTkButton(self, width=30, text="⚙", command=self.toggle_menu, fg_color="#DDADAF")
        self.menu_btn.place(x=0, y=0)

        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)

        self.msg_entry = CTkEntry(self, height=40, placeholder_text="Send a massage 💬")
        self.msg_entry.place(x=0, y=0)

        self.open_img = CTkButton(self, width=50, height=40, text="📂" , command=self.send_msg)
        self.open_img.place(x=0, y=0)

        self.send_button = CTkButton(self, width=50, height=40, text="➡", command=self.open_image)
        self.send_button.place(x=0, y=0)

        self.add_msg(f"{self.username}: test")
        self.add_msg("Image display demonstration", CTkImage(Image.open("img.png"), size=(300, 200)))

        self.adaptive_ui()

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))
            hello =f"TEXT@{self.username}@[SYSTEM]{self.username} joined the chat!\n"
            self.sock.send(hello.encode("utf-8"))
            threading.Thread(target=self.recv_msg,daemon=True).start()
        except Exception as e:
            self.add_msg(f"Failed to connect to server: {e}")


    def toggle_menu(self):
        if self.is_menu_shown:
            self.is_menu_shown = False
            self.menu_animate_speed = -self.menu_animate_speed
            self.show_menu()
        else:
            self.is_menu_shown = True
            self.menu_animate_speed = -self.menu_animate_speed
            self.show_menu()

            self.label = CTkLabel(self.menu_frame, text="Name")
            self.label.pack(pady=10)

            self.entry = CTkEntry(self.menu_frame, placeholder_text="Your nickname...")
            self.entry.insert(0, self.username)
            self.entry.pack(pady =(0, 10))




            self.avatar_btn = CTkButton(self.menu_frame,text = "Choose an avatar", command = self.choose_avatar)
            self.avatar_btn.pack(pady=(5, 10))
            self.avatar_preview = CTkLabel(self.menu_frame, text = " (none)")
            self.avatar_preview.pack(pady=(0, 10))

            if self.avatar_image:
                self.avatar_preview.configure(image=self.avatar_image, text="")

            self.save_button = CTkButton(self.menu_frame, text="save", command=self.save_name)
            self.save_button.pack()

            self.theme_option = CTkOptionMenu(self.menu_frame, values = ["Dark", "Light"], command = self.change_theme)
            self.theme_option.pack(side="bottom", pady=20)


    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.menu_animate_speed)
        if not self.menu_frame.winfo_width() >= 200 and self.is_menu_shown:
            self.after(5, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_menu_shown:
            self.after(5, self.show_menu)
            for widget in self.menu_frame.winfo_children():
                widget.destroy()


        self.after(50, self.adaptive_ui)

    def save_name(self):
        new_name = self.entry.get().strip
        if new_name:
            self.username = new_name
            self.add_msg(f"Your new nickname: {self.username}")

    def choose_avatar(self):
        file_pats = filedialog.askopenfilename(title="Choose an avatar", filetypes=[("Images","*.png;*.jpg;*.jpeg")])
        if not file_pats:
            return
        try:
            size = (40 ,40)
            img = Image.open(file_pats).resize(size)
            self.avatar_image = CTkImage(img, size=size)
            self.avatar_preview.configure(image = self.avatar_image, text="")
        except Exception as e:
            self.add_msg(f"Failed to open file: {e}")


    def adaptive_ui(self):
        self.open_img.place(x = self.winfo_width() -105, y = self.send_button.winfo_y())
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20, height=self.winfo_height() - self.msg_entry.winfo_height() - 20)
        self.chat_field.place(x = self.menu_frame.winfo_width())

        self.msg_entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 110)
        self.msg_entry.place(x = self.menu_frame.winfo_width(), y = self.send_button.winfo_y())
        self.send_button.place(x = self.winfo_width() - 50, y = self.winfo_height() - 40)

    def add_msg(self, msg, img=None, avatar=None):
        msg_frame = CTkFrame(self.chat_field, fg_color="gray")
        msg_frame.pack(pady=5, padx=5)

        wrap_size = self.winfo_width() - self.menu_frame.winfo_width() - 40

        if avatar:
            CTkLabel(msg_frame, text=avatar).pack(side="left", padx=(10,5), pady=5)


        if not img:
            CTkLabel(msg_frame, text=msg, wraplength=wrap_size, text_color="white", justify="left").pack(pady=10, padx=5)
        else:
            CTkLabel(msg_frame, text=msg, wraplength=wrap_size, text_color="white", image=img, compound="top", justify="left").pack(padx=10, pady=5)

    def send_msg(self):
        msg = self.msg_entry.get()
        if msg:
            self.add_msg(f"{self.usarname}: {msg}", avatar=self.avatar_image)
            data = f"TEXT@{self.username}@{msg}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.msg_entry.delete((0, END))

    def recv_msg(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode("otf-8", errors="ignore")
                while "\n" in buffer:
                      line, buffer = buffer.split("\n", 1)
                      self.handle_line(line.strip())
            except:
                break
            self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                msg = parts[2]
                self.add_msg((f"{author}: {msg}"))
            elif msg_type == "IMAGE":
                if len(parts) >= 4:
                    author = parts[1]
                    filename = parts[2]
                    b64_img = parts[3]
                    try:
                        img_data = base64.b64decode(b64_img)
                        pil_img = Image.open(io.BytesIO(img_data))
                        ctk_img = CTkImage(pil_img, size=(300, 300))
                        self.add_msg(f"{author} send img: {filename}", img=ctk_img)
                    except Exception as e:
                        self.add_msg(f"image dislplay eror: {e}")

            else:
                self.add_msg(line)
    def open_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64decode(raw).decode()
            short_name = os.path.basename(file_name)
            data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
            self.sock.sendall(data.encode())
            self.add_msg("", CTkImage(light_image=Image.open(file_name), size=(300, 300)), avatar=self.avatar_image)
        except Exception as e:
            self.add_msg((f""))

    def change_theme(self, value):
        if value == "Dark":
            set_appearance_mode("dark")
            self.configure(fg_color="indigo")
            self.menu_frame.configure(fg_color="indigo")
        else:
            set_appearance_mode("light")
            self.configure(fg_color="violet")
            self.menu_frame.configure(fg_color="violet")





if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()
