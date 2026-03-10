"""
eyoTools Desktop Application
Central hub for all utility tools with Dark Mode and Multi-language support
Bilingual: English and Amharic
Converted from Kivy to Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import ctypes
from ctypes import byref
from datetime import datetime
import threading
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageOps
import shutil
import math
import tkinter.font as tkfont

# Add functions directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))

# Try to import tool modules
try:
    from functions.youtube_dl import YouTubeDownloaderFrame
    from functions.bg_remover import BackgroundRemoverFrame
    from functions.pdf_tools import PDFExtractorFrame, PDFToAudioFrame
    from functions.ocr_tool import OCRFrame
    from functions.qr_tool import QRGeneratorFrame
    from functions.steganography import SteganographyFrame
    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some tools could not be imported: {e}")
    TOOLS_AVAILABLE = False

# ==================== FONT REGISTRATION SYSTEM ====================
def register_font(font_path):
    """
    Register a .ttf font file temporarily with the system
    Returns True if successful, False otherwise
    """
    if not os.path.exists(font_path):
        print(f"Error: Font not found at {font_path}")
        return False

    # For Windows systems
    if sys.platform.startswith('win'):
        try:
            FR_PRIVATE = 0x10
            path_buf = ctypes.create_unicode_buffer(font_path)
            add_font_resource_ex = ctypes.windll.gdi32.AddFontResourceExW
            res = add_font_resource_ex(byref(path_buf), FR_PRIVATE, 0)
            return res != 0
        except Exception as e:
            print(f"Error registering font on Windows: {e}")
            return False
    
    # For other systems (Linux/Mac) - just check if font exists
    return True

# Get the base directory (works for both script and compiled exe)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Font paths to try (in order of preference)
FONT_PATHS = [
    os.path.join(BASE_DIR, 'fonts', 'AbyssinicaSIL-Regular.ttf'),
    os.path.join(BASE_DIR, 'fonts', 'abyssinica.ttf'),
    os.path.join(BASE_DIR, 'fonts', 'Abyssinica.ttf'),
    os.path.join(BASE_DIR, 'AbyssinicaSIL-Regular.ttf'),
]

# Try to register the font
FONT_REGISTERED = False
FONT_FAMILY = 'Arial'  # Default fallback

for font_path in FONT_PATHS:
    if os.path.exists(font_path):
        if register_font(font_path):
            print(f"✅ Font registered successfully: {font_path}")
            FONT_REGISTERED = True
            # The actual font family name inside the font file
            # For Abyssinica SIL, it's typically "Abyssinica SIL"
            FONT_FAMILY = "Abyssinica SIL"
            break
        else:
            print(f"⚠️ Font found but registration failed: {font_path}")

# Check if font is available in tkinter
if FONT_REGISTERED:
    try:
        available_fonts = tkfont.families()
        if FONT_FAMILY not in available_fonts:
            print(f"⚠️ Font '{FONT_FAMILY}' not found in tkinter families")
            print("Available Amharic fonts:", [f for f in available_fonts if 'abyssinica' in f.lower() or 'nyala' in f.lower() or 'ebrima' in f.lower()])
            # Try alternative Amharic fonts
            amharic_fonts = ['Abyssinica SIL', 'Nyala', 'Ebrima', 'Kefa', 'Noto Sans Ethiopic']
            for font in amharic_fonts:
                if font in available_fonts:
                    FONT_FAMILY = font
                    print(f"✅ Using alternative Amharic font: {font}")
                    break
            else:
                FONT_REGISTERED = False
                FONT_FAMILY = 'Arial'
    except Exception as e:
        print(f"Error checking fonts: {e}")
        FONT_REGISTERED = False

if not FONT_REGISTERED:
    print("⚠️ Using default font (Arial). Amharic text may not display correctly.")
    print("Please place AbyssinicaSIL-Regular.ttf in the 'fonts' folder.")

# Language strings with proper Unicode support
STRINGS = {
    'en': {
        'app_name': 'eyoTools',
        'home': 'Home',
        'tools': 'Tools',
        'settings': 'Settings',
        'dark_mode': 'Dark Mode',
        'light_mode': 'Light Mode',
        'language': 'Language',
        'english': 'English',
        'amharic': 'አማርኛ',
        'about': 'About',
        'contact': 'Contact',
        'developer': 'Developer Info',
        'version': 'Version 1.0.0',
        'youtube': 'YouTube Downloader',
        'bg_remover': 'Background Remover',
        'pdf_extract': 'PDF to Text',
        'pdf_audio': 'PDF to Audio',
        'ocr': 'Image to Text (OCR)',
        'qr': 'QR Code Generator',
        'steganography': 'Steganography',
        'loading': 'Loading...',
        'welcome': 'Welcome to eyoTools',
        'welcome_sub': 'Your Ultimate Computer Science Toolkit',
        'cs_quote': '"Code is like humor. When you have to explain it, it\'s bad." – Cory House',
        'select_tool': 'Select a tool to get started',
        'ok': 'OK',
        'cancel': 'Cancel',
        'message': 'Message',
        'exit': 'Exit',
        'cs_students': 'For CS Students, By a CS Student'
    },
    'am': {
        'app_name': 'ኢዮ መሳሪያዎች',
        'home': 'መነሻ',
        'tools': 'መሳሪያዎች',
        'settings': 'ማስተካከያ',
        'dark_mode': 'ጨለማ ሁነታ',
        'light_mode': 'ብርሃን ሁነታ',
        'language': 'ቋንቋ',
        'english': 'እንግሊዝኛ',
        'amharic': 'አማርኛ',
        'about': 'ስለ እኛ',
        'contact': 'መገናኛ',
        'developer': 'ገንቢ መረጃ',
        'version': 'እትም 1.0.0',
        'youtube': 'ዩቲዩብ አውራጅ',
        'bg_remover': 'ዳራ አስወጋጅ',
        'pdf_extract': 'PDF ወደ ጽሁፍ',
        'pdf_audio': 'PDF ወደ ድምጽ',
        'ocr': 'ምስል ወደ ጽሁፍ',
        'qr': 'QR ኮድ አመንጪ',
        'steganography': 'ስውር መልእክት',
        'loading': 'በመጫን ላይ...',
        'welcome': 'እንኳን ወደ ኢዮ መሳሪያዎች በደህና መጡ',
        'welcome_sub': 'የእርስዎ የኮምፒውተር ሳይንስ መሳሪያዎች ስብስብ',
        'cs_quote': '"ኮድ እንደ ቀልድ ነው። ማስረዳት ሲያስፈልገው ጥሩ አይደለም።"',
        'select_tool': 'ለመጀመር መሳሪያ ይምረጡ',
        'ok': 'እሺ',
        'cancel': 'ሰርዝ',
        'message': 'መልእክት',
        'exit': 'ውጣ',
        'cs_students': 'ለኮምፒውተር ሳይንስ ተማሪዎች፣ በኮምፒውተር ሳይንስ ተማሪ'
    }
}

# Font helper function
def get_font(family=None, size=10, weight='normal'):
    """Get font tuple with proper fallback"""
    if family is None:
        family = FONT_FAMILY if FONT_REGISTERED else 'Arial'
    return (family, size, weight)

class RoundedButton(tk.Canvas):
    """Custom rounded button for tool cards"""
    def __init__(self, parent, text, command=None, width=150, height=120, 
                 bg_color="#3498db", fg_color="white", **kwargs):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=parent['bg'])
        self.command = command
        self.text = text
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.width = width
        self.height = height
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        self.draw_button(bg_color)
    
    def draw_button(self, color):
        """Draw rounded rectangle button"""
        self.delete("all")
        
        # Draw rounded rectangle
        radius = 15
        coords = (5, 5, self.width-5, self.height-5)
        self.create_rounded_rect(coords, radius, fill=color, outline="", tags="button")
        
        # Draw text with proper font
        font = get_font(size=11, weight='bold')
        self.create_text(self.width/2, self.height/2, text=self.text,
                        fill=self.fg_color, font=font,
                        width=self.width-20, tags="text")
    
    def create_rounded_rect(self, coords, radius, **kwargs):
        """Create a rounded rectangle"""
        x1, y1, x2, y2 = coords
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_click(self, event):
        """Handle click event"""
        if self.command:
            self.command()
    
    def on_enter(self, event):
        """Handle mouse enter"""
        self.draw_button(self.adjust_color(self.bg_color, 20))
    
    def on_leave(self, event):
        """Handle mouse leave"""
        self.draw_button(self.bg_color)
    
    def adjust_color(self, color, amount):
        """Lighten or darken color"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            r = min(255, max(0, r + amount))
            g = min(255, max(0, g + amount))
            b = min(255, max(0, b + amount))
            
            return f'#{r:02x}{g:02x}{b:02x}'
        return color

class CSSStudentsImage(tk.Frame):
    """Create a beautiful CSS students-themed image"""
    def __init__(self, parent, width=400, height=200, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        self.width = width
        self.height = height
        self.configure(bg='#f0f0f0')
        
        self.create_image()
    
    def create_image(self):
        """Create or load the CSS students-themed image"""
        # Try to load custom image first
        img_path = os.path.join(BASE_DIR, 'assets', 'logo.png')
        
        try:
            if os.path.exists(img_path):
                # Load and process the image
                pil_img = Image.open(img_path)
                pil_img = pil_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                
                # Add rounded corners
                mask = Image.new('L', pil_img.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle([(0, 0), pil_img.size], radius=20, fill=255)
                
                # Apply mask
                result = Image.new('RGBA', pil_img.size)
                result.paste(pil_img, mask=mask)
                
                self.photo = ImageTk.PhotoImage(result)
                
                img_label = tk.Label(self, image=self.photo, bg='#f0f0f0')
                img_label.pack(expand=True)
            else:
                # Create styled placeholder
                self.create_placeholder()
        except Exception as e:
            print(f"Error loading image: {e}")
            self.create_placeholder()
    
    def create_placeholder(self):
        """Create a styled placeholder with CS theme"""
        # Create a PIL image
        img = Image.new('RGBA', (self.width, self.height), (26, 26, 46, 255))  # #1a1a2e
        draw = ImageDraw.Draw(img)
        
        # Draw rounded rectangle border
        draw.rounded_rectangle([(5, 5), (self.width-5, self.height-5)],
                              radius=20, outline='#4ecdc4', width=3)
        
        # Draw code symbols
        # Use default font since PIL might not have custom fonts
        draw.text((self.width//2-60, 40), "{ CS }", 
                 fill='#4ecdc4', font=None)
        
        draw.text((self.width//2-80, 80), "while(alive):", 
                 fill='#ff6b6b', font=None)
        draw.text((self.width//2-60, 100), "    code.eat().sleep()",
                 fill='#ff6b6b', font=None)
        
        draw.text((self.width//2-90, 140), "# For CS Students",
                 fill='#95a5a6', font=None)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(img)
        
        img_label = tk.Label(self, image=self.photo, bg='#f0f0f0')
        img_label.pack(expand=True)

class SplashScreen(tk.Toplevel):
    """Enhanced splash screen with CS theme"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("")
        self.geometry("500x600")
        self.configure(bg='#1a1a2e')
        self.overrideredirect(True)
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f'500x600+{x}+{y}')
        
        self.create_widgets()
        self.after(100, self.animate)
    
    def create_widgets(self):
        # Canvas for background
        self.canvas = tk.Canvas(self, bg='#1a1a2e', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Draw decorative code background
        self.draw_code_background()
        
        # Main content frame
        content = tk.Frame(self.canvas, bg='#1a1a2e')
        content_window = self.canvas.create_window(250, 300, window=content)
        
        # Logo
        logo_frame = tk.Frame(content, bg='#1a1a2e')
        logo_frame.pack(pady=20)
        
        logo_canvas = tk.Canvas(logo_frame, width=200, height=200,
                                bg='#1a1a2e', highlightthickness=0)
        logo_canvas.pack()
        
        # Draw logo
        logo_canvas.create_oval(50, 50, 150, 150, outline='#4ecdc4',
                                 width=3, fill='')
        logo_canvas.create_text(100, 100, text="{CS}", fill='#4ecdc4',
                                font=get_font(size=24, weight='bold'))
        
        # Draw code symbols around
        for i, symbol in enumerate(['<', '>', '{', '}', '(', ')', '[', ']']):
            angle = i * 45 * 3.14159 / 180
            x = 100 + 80 * math.cos(angle)
            y = 100 + 80 * math.sin(angle)
            logo_canvas.create_text(x, y, text=symbol, fill='#ff6b6b',
                                    font=get_font(size=16, weight='bold'))
        
        # App name
        tk.Label(content, text="eyoTools",
                font=get_font(size=32, weight='bold'),
                fg='#4ecdc4', bg='#1a1a2e').pack(pady=10)
        
        tk.Label(content, text="For Computer Science Students",
                font=get_font(size=14),
                fg='#bdc3c7', bg='#1a1a2e').pack()
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("CS.Horizontal.TProgressbar",
                        background='#4ecdc4',
                        troughcolor='#2c3e50',
                        bordercolor='#1a1a2e',
                        lightcolor='#4ecdc4',
                        darkcolor='#4ecdc4')
        
        self.progress = ttk.Progressbar(content, length=300, 
                                        mode='determinate',
                                        style="CS.Horizontal.TProgressbar")
        self.progress.pack(pady=30)
        
        # Loading label
        self.loading_label = tk.Label(content, text="Initializing CS Tools...",
                                      font=get_font(size=11),
                                      fg='#95a5a6', bg='#1a1a2e')
        self.loading_label.pack()
        
        # Binary animation
        self.binary_label = tk.Label(self.canvas, 
                                     text="01001111 01101110 01100101",
                                     font=("Courier", 10),
                                     fg='#2c3e50', bg='#1a1a2e')
        self.canvas.create_window(250, 550, window=self.binary_label)
    
    def draw_code_background(self):
        """Draw code-like patterns in background"""
        for i in range(0, 500, 30):
            opacity = 50
            self.canvas.create_line(20, i, 480, i, fill=f'#4ecdc4{opacity:02x}',
                                   width=1, dash=(5, 3))
            
            if i % 60 == 0:
                code = f"function_{i//60}()"
                self.canvas.create_text(50, i+15, text=code,
                                       fill=f'#ff6b6b{opacity:02x}',
                                       font=("Courier", 8),
                                       anchor='w')
    
    def animate(self):
        """Animate progress bar"""
        self.progress['value'] += 2
        if self.progress['value'] < 100:
            # Update loading text
            texts = ["Loading CS modules...", 
                    "Compiling algorithms...",
                    "Initializing data structures...",
                    "Connecting to code repository...",
                    "Almost there..."]
            idx = int(self.progress['value'] / 20)
            if idx < len(texts):
                self.loading_label.config(text=texts[idx])
            
            # Update binary text
            binary = ["01001111 01101110 01100101",  # One
                     "01010100 01110111 01101111",  # Two
                     "01010100 01101000 01110010",  # Three
                     "01000110 01101111 01110101",  # Four
                     "01000110 01101001 01110110"]   # Five
            bin_idx = int(self.progress['value'] / 20) % len(binary)
            self.binary_label.config(text=binary[bin_idx])
            
            self.after(50, self.animate)
        else:
            self.after(500, self.destroy)

class NavigationMenu(tk.Frame):
    """Slide-out navigation menu with CS theme"""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.configure(bg='#1a1a2e', width=300)
        self.place(x=-300, y=0, relheight=1)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg='#16213e', height=120)
        header.pack(fill='x', pady=(0, 20))
        header.pack_propagate(False)
        
        # Logo
        logo_canvas = tk.Canvas(header, width=60, height=60,
                                bg='#16213e', highlightthickness=0)
        logo_canvas.place(x=20, y=20)
        logo_canvas.create_oval(10, 10, 50, 50, outline='#4ecdc4',
                                 width=2, fill='')
        logo_canvas.create_text(30, 30, text="CS", fill='#4ecdc4',
                                font=get_font(size=12, weight='bold'))
        
        tk.Label(header, text=self.app.get_string('app_name'),
                font=get_font(size=18, weight='bold'),
                fg='#4ecdc4', bg='#16213e').place(x=90, y=25)
        
        tk.Label(header, text=self.app.get_string('version'),
                font=get_font(size=9),
                fg='#bdc3c7', bg='#16213e').place(x=90, y=55)
        
        tk.Label(header, text="CS Student Edition",
                font=get_font(size=9, weight='italic'),
                fg='#ff6b6b', bg='#16213e').place(x=90, y=75)
        
        # Tools section
        tools_label = tk.Label(self, text=f"⚡ {self.app.get_string('tools')}",
                              font=get_font(size=13, weight='bold'),
                              fg='#4ecdc4', bg='#1a1a2e')
        tools_label.pack(pady=(0, 10), padx=20, anchor='w')
        
        self.tools_frame = tk.Frame(self, bg='#1a1a2e')
        self.tools_frame.pack(fill='both', expand=True, padx=15)
        
        self.create_tools_list()
        
        # Settings section
        settings_label = tk.Label(self, text=f"⚙️ {self.app.get_string('settings')}",
                                 font=get_font(size=13, weight='bold'),
                                 fg='#4ecdc4', bg='#1a1a2e')
        settings_label.pack(pady=(20, 10), padx=20, anchor='w')
        
        settings_frame = tk.Frame(self, bg='#1a1a2e')
        settings_frame.pack(fill='x', padx=20)
        
        # Dark mode toggle
        dark_frame = tk.Frame(settings_frame, bg='#1a1a2e')
        dark_frame.pack(fill='x', pady=5)
        
        tk.Label(dark_frame, text="🌙",
                font=get_font(size=12),
                fg='#f1c40f', bg='#1a1a2e').pack(side='left', padx=(0, 10))
        
        tk.Label(dark_frame, text=self.app.get_string('dark_mode'),
                font=get_font(size=11),
                fg='white', bg='#1a1a2e').pack(side='left')
        
        self.dark_mode_var = tk.BooleanVar(value=False)
        dark_toggle = tk.Checkbutton(dark_frame, variable=self.dark_mode_var,
                                     command=self.app.toggle_dark_mode,
                                     bg='#1a1a2e', fg='#4ecdc4',
                                     selectcolor='#1a1a2e',
                                     activebackground='#1a1a2e')
        dark_toggle.pack(side='right')
        
        # Language selection
        lang_frame = tk.Frame(settings_frame, bg='#1a1a2e')
        lang_frame.pack(fill='x', pady=5)
        
        tk.Label(lang_frame, text="🌐",
                font=get_font(size=12),
                fg='#4ecdc4', bg='#1a1a2e').pack(side='left', padx=(0, 10))
        
        tk.Label(lang_frame, text=self.app.get_string('language'),
                font=get_font(size=11),
                fg='white', bg='#1a1a2e').pack(side='left')
        
        self.lang_var = tk.StringVar(value='English')
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var,
                                  values=['English', 'አማርኛ'],
                                  state='readonly', width=10,
                                  font=get_font(size=10))
        lang_combo.pack(side='right')
        lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # Info buttons
        info_frame = tk.Frame(self, bg='#1a1a2e')
        info_frame.pack(fill='x', side='bottom', pady=20, padx=15)
        
        for text, command in [
            ('ℹ️ ' + self.app.get_string('about'), self.show_about),
            ('📧 ' + self.app.get_string('contact'), self.show_contact),
            ('👨‍💻 ' + self.app.get_string('developer'), self.show_developer)
        ]:
            btn = tk.Button(info_frame, text=text,
                           command=command,
                           bg='#16213e', fg='white',
                           font=get_font(size=10),
                           relief='flat',
                           anchor='w',
                           padx=10)
            btn.pack(fill='x', pady=2)
    
    def create_tools_list(self):
        """Create tools menu items with icons"""
        for widget in self.tools_frame.winfo_children():
            widget.destroy()
        
        tools = [
            ('youtube', 'youtube_dl', '🎥'),
            ('bg_remover', 'bg_remover', '🖼️'),
            ('pdf_extract', 'pdf_extract', '📄'),
            ('pdf_audio', 'pdf_audio', '🔊'),
            ('ocr', 'ocr', '📝'),
            ('qr', 'qr', '📱'),
            ('steganography', 'steganography', '🔐')
        ]
        
        for tool_id, screen_name, icon in tools:
            btn_frame = tk.Frame(self.tools_frame, bg='#16213e')
            btn_frame.pack(fill='x', pady=2)
            
            tk.Label(btn_frame, text=icon,
                    font=get_font(size=12),
                    fg='#4ecdc4', bg='#16213e').pack(side='left', padx=5)
            
            btn = tk.Button(btn_frame,
                           text=self.app.get_string(tool_id),
                           command=lambda s=screen_name: self.open_tool(s),
                           bg='#16213e', fg='white',
                           font=get_font(size=11),
                           relief='flat',
                           anchor='w')
            btn.pack(side='left', fill='x', expand=True)
    
    def open_tool(self, screen_name):
        """Open selected tool"""
        self.app.show_frame(screen_name)
        self.toggle()
    
    def on_language_change(self, event):
        """Handle language change"""
        if self.lang_var.get() == 'አማርኛ':
            self.app.current_lang = 'am'
        else:
            self.app.current_lang = 'en'
        self.app.update_ui_language()
        self.create_tools_list()
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(self.app.get_string('about'),
                           "eyoTools - CS Student Edition\n\n"
                           "A collection of useful utilities for\n"
                           "Computer Science students.\n\n"
                           "Version 1.0.0\n"
                           "© 2025 (2018) eyoTools")
    
    def show_contact(self):
        """Show contact info"""
        messagebox.showinfo(self.app.get_string('contact'),
                           "📧 https://eyobbegashaw.vercel.app/\n"
                           "💻 GitHub: @eyobbegashaw\n"
                           "🐦 Twitter: @eyobbegashaw")
    
    def show_developer(self):
        """Show developer info"""
        messagebox.showinfo(self.app.get_string('developer'),
                           "👨‍💻 Developed by: Dn Eyob Begashaw\n"
                           "🎓 Computer Science Student\n"
                           "📍 Ethiopia\n\n"
                           "Special thanks to all CS students!")
    
    def toggle(self):
        """Toggle menu visibility"""
        x = self.winfo_x()
        target = 0 if x < 0 else -300
        self.animate_menu(target)
    
    def animate_menu(self, target, step=20):
        """Animate menu sliding"""
        current = self.winfo_x()
        if current != target:
            if current < target:
                new = min(current + step, target)
            else:
                new = max(current - step, target)
            self.place(x=new)
            self.after(10, lambda: self.animate_menu(target, step))

# [Rest of the classes remain the same...]

class eyoToolsApp(tk.Tk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        self.title("eyoTools")
        self.geometry("500x700")
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f'500x700+{x}+{y}')
        
        # Initialize properties
        self.dark_mode = False
        self.current_lang = 'en'
        self.frames = {}
        
        # Show splash screen
        self.splash = SplashScreen(self)
        
        # Create main container
        self.container = tk.Frame(self)
        self.container.pack(fill='both', expand=True)
        
        # Create navigation menu
        self.menu = NavigationMenu(self, self)
        
        # Schedule initialization after splash
        self.after(1000, self.initialize_app)
    
    def initialize_app(self):
        """Initialize the application after splash screen"""
        # Create screens
        self.create_frames()
        
        # Show home screen
        self.show_frame('home')
        
        # Configure exit handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_frames(self):
        """Create all application frames"""
        # Home frame
        from home_screen import HomeScreen
        self.frames['home'] = HomeScreen(self.container, self)
        
        # Tool frames
        if TOOLS_AVAILABLE:
            try:
                self.frames['youtube_dl'] = YouTubeDownloaderFrame(self.container, self)
                self.frames['bg_remover'] = BackgroundRemoverFrame(self.container, self)
                self.frames['pdf_extract'] = PDFExtractorFrame(self.container, self)
                self.frames['pdf_audio'] = PDFToAudioFrame(self.container, self)
                self.frames['ocr'] = OCRFrame(self.container, self)
                self.frames['qr'] = QRGeneratorFrame(self.container, self)
                self.frames['steganography'] = SteganographyFrame(self.container, self)
            except Exception as e:
                print(f"Error loading tools: {e}")
        
        # Grid all frames
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky='nsew')
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
    
    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise()
            
            # Call on_show method if exists
            if hasattr(frame, 'on_show'):
                frame.on_show()
    
    def get_string(self, key):
        """Get string in current language"""
        return STRINGS[self.current_lang].get(key, STRINGS['en'].get(key, key))
    
    def toggle_dark_mode(self):
        """Toggle dark mode"""
        self.dark_mode = self.menu.dark_mode_var.get()
        self.update_ui_theme()
    
    def update_ui_theme(self):
        """Update UI theme for all screens"""
        bg_color = '#1a1a2e' if self.dark_mode else '#f0f0f0'
        fg_color = 'white' if self.dark_mode else '#333333'
        
        for frame in self.frames.values():
            if hasattr(frame, 'update_theme'):
                frame.update_theme(bg_color, fg_color)
    
    def update_ui_language(self):
        """Update language for all screens"""
        for frame in self.frames.values():
            if hasattr(frame, 'update_language'):
                frame.update_language()
    
    def get_storage_path(self, folder):
        """Get storage path for files"""
        base_path = os.path.join(os.path.expanduser('~'), 'eyoTools')
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)
        return path
    
    def toggle_menu(self):
        """Toggle navigation menu"""
        if hasattr(self, 'menu'):
            self.menu.toggle()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Exit", "Do you want to exit?"):
            self.destroy()


if __name__ == '__main__':
    app = eyoToolsApp()
    app.mainloop()