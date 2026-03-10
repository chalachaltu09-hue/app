"""
PDF Tools Module
PDF to Text Extractor and PDF to Audio Converter
Bilingual: English and Amharic
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
import threading
import shutil

# PDF to Text imports
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# PDF to Audio imports
try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

STRINGS = {
    'en': {
        # PDF to Text
        'pdf_to_text': 'PDF to Text',
        'select_pdf': 'Select PDF:',
        'choose_pdf': 'Choose PDF',
        'extract': 'Extract Text',
        'preview': 'Preview:',
        'save_txt': 'Save as TXT',
        'copy': 'Copy',
        'clear': 'Clear',
        'back': 'Back to Home',
        'select_pdf_first': 'Please select a PDF first',
        'no_pypdf2': 'PDF extractor not available. Install PyPDF2',
        'extracting': 'Extracting text...',
        'page': 'Page',
        'of': 'of',
        'complete': 'Text extraction complete!',
        'error': 'Error extracting text',
        'saved': 'Text saved successfully!',
        'save_error': 'Error saving text',
        'copied': 'Text copied to clipboard!',
        'copy_error': 'Error copying text',
        'pages': 'Pages',
        'ready': 'Ready',
        
        # PDF to Audio
        'pdf_to_audio': 'PDF to Audio',
        'select_lang': 'Select Language:',
        'convert': 'Convert to Audio',
        'play': 'Play',
        'stop': 'Stop',
        'save_audio': 'Save as MP3',
        'no_gtts': 'Text to speech not available',
        'converting': 'Converting to speech...',
        'playing': 'Playing audio...',
        'stopped': 'Stopped'
    },
    'am': {
        # PDF to Text
        'pdf_to_text': 'PDF ወደ ጽሁፍ',
        'select_pdf': 'PDF ይምረጡ:',
        'choose_pdf': 'PDF ምረጥ',
        'extract': 'ጽሁፍ አውጣ',
        'preview': 'ቅድመ እይታ:',
        'save_txt': 'እንደ TXT አስቀምጥ',
        'copy': 'ቅዳ',
        'clear': 'አጽዳ',
        'back': 'ወደ መነሻ',
        'select_pdf_first': 'እባክዎ መጀመሪያ PDF ይምረጡ',
        'no_pypdf2': 'PDF አውጪ አይገኝም። PyPDF2 ይጫኑ',
        'extracting': 'ጽሁፍ በማውጣት ላይ...',
        'page': 'ገጽ',
        'of': 'ከ',
        'complete': 'ጽሁፍ ማውጣት ተጠናቋል!',
        'error': 'ጽሁፍ በማውጣት ላይ ስህተት',
        'saved': 'ጽሁፍ በተሳካ ሁኔታ ተቀምጧል!',
        'save_error': 'ጽሁፍ በማስቀመጥ ላይ ስህተት',
        'copied': 'ጽሁፍ ወደ ክሊፕቦርድ ተቀድቷል!',
        'copy_error': 'ጽሁፍ በመቅዳት ላይ ስህተት',
        'pages': 'ገጾች',
        'ready': 'ዝግጁ',
        
        # PDF to Audio
        'pdf_to_audio': 'PDF ወደ ድምጽ',
        'select_lang': 'ቋንቋ ይምረጡ:',
        'convert': 'ወደ ድምጽ ቀይር',
        'play': 'አጫውት',
        'stop': 'አቁም',
        'save_audio': 'እንደ MP3 አስቀምጥ',
        'no_gtts': 'ጽሁፍ ወደ ድምጽ መቀየሪያ አይገኝም',
        'converting': 'ወደ ድምጽ በመቀየር ላይ...',
        'playing': 'ድምጽ በማጫወት ላይ...',
        'stopped': 'ቆሟል'
    }
}

class PDFExtractorFrame(tk.Frame):
    """PDF to Text Extractor Frame"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#f0f0f0')
        
        self.pdf_path = None
        self.extracted_text = ""
        self.total_pages = 0
        
        self.create_widgets()
        
        # Initialize pygame mixer for audio
        if GTTS_AVAILABLE:
            pygame.mixer.init()
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg='#3498db', height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Button(header, text='←', font=('Arial', 16),
                 bg='#3498db', fg='white', relief='flat',
                 command=self.go_back).pack(side='left', padx=10)
        
        self.title_label = tk.Label(header, text='',
                                   font=('Arial', 14, 'bold'),
                                   bg='#3498db', fg='white')
        self.title_label.pack(side='left', padx=20)
        
        # Main content
        main = tk.Frame(self, bg='#f0f0f0', padx=20, pady=20)
        main.pack(fill='both', expand=True)
        
        # PDF selection
        select_frame = tk.Frame(main, bg='#f0f0f0')
        select_frame.pack(fill='x', pady=10)
        
        self.select_label = tk.Label(select_frame, text='',
                                     font=('Arial', 12),
                                     bg='#f0f0f0', fg='#333333')
        self.select_label.pack(side='left')
        
        self.select_btn = tk.Button(select_frame, text='',
                                    bg='#3498db', fg='white',
                                    font=('Arial', 11),
                                    command=self.choose_pdf)
        self.select_btn.pack(side='right')
        
        # PDF info
        self.info_label = tk.Label(main, text='',
                                   font=('Arial', 11),
                                   bg='#f0f0f0', fg='#333333',
                                   anchor='w')
        self.info_label.pack(fill='x', pady=5)
        
        # Extract button
        self.extract_btn = tk.Button(main, text='',
                                     bg='#27ae60', fg='white',
                                     font=('Arial', 12, 'bold'),
                                     command=self.extract_text)
        self.extract_btn.pack(fill='x', pady=10)
        
        # Progress section
        progress_frame = tk.Frame(main, bg='#f0f0f0')
        progress_frame.pack(fill='x', pady=10)
        
        self.progress_label = tk.Label(progress_frame, text='',
                                       font=('Arial', 11),
                                       bg='#f0f0f0', fg='#333333')
        self.progress_label.pack(anchor='w')
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=300,
                                            mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)
        
        self.status_label = tk.Label(progress_frame, text='',
                                     font=('Arial', 10),
                                     bg='#f0f0f0', fg='#666666')
        self.status_label.pack(anchor='w')
        
        # Text preview
        preview_frame = tk.LabelFrame(main, text='', font=('Arial', 12),
                                      bg='#f0f0f0', fg='#333333')
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        self.preview_label = tk.Label(preview_frame, text='',
                                      bg='#f0f0f0', fg='#333333')
        self.preview_label.pack(padx=5, pady=5)
        
        # Text area with scrollbar
        text_frame = tk.Frame(preview_frame, bg='#f0f0f0')
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.text_area = tk.Text(text_frame, height=8,
                                  font=('Arial', 11),
                                  bg='white', fg='#333333',
                                  wrap='word')
        self.text_area.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical',
                                  command=self.text_area.yview)
        scrollbar.pack(side='right', fill='y')
        self.text_area.config(yscrollcommand=scrollbar.set)
        
        # Action buttons
        button_frame = tk.Frame(main, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=10)
        
        self.save_btn = tk.Button(button_frame, text='',
                                  bg='#9b59b6', fg='white',
                                  font=('Arial', 11),
                                  command=self.save_text,
                                  state='disabled')
        self.save_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        self.copy_btn = tk.Button(button_frame, text='',
                                  bg='#3498db', fg='white',
                                  font=('Arial', 11),
                                  command=self.copy_text,
                                  state='disabled')
        self.copy_btn.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Clear button
        self.clear_btn = tk.Button(main, text='',
                                   bg='#95a5a6', fg='white',
                                   font=('Arial', 11),
                                   command=self.clear_all)
        self.clear_btn.pack(fill='x', pady=5)
        
        self.update_language()
    
    def update_language(self):
        """Update UI language"""
        self.title_label.config(text=STRINGS[self.controller.current_lang]['pdf_to_text'])
        self.select_label.config(text=STRINGS[self.controller.current_lang]['select_pdf'])
        self.select_btn.config(text=STRINGS[self.controller.current_lang]['choose_pdf'])
        self.extract_btn.config(text=STRINGS[self.controller.current_lang]['extract'])
        self.save_btn.config(text=STRINGS[self.controller.current_lang]['save_txt'])
        self.copy_btn.config(text=STRINGS[self.controller.current_lang]['copy'])
        self.clear_btn.config(text=STRINGS[self.controller.current_lang]['clear'])
        
        # Update frame labels
        preview_frame = self.nametowidget(self.preview_frame)
        preview_frame.config(text=STRINGS[self.controller.current_lang]['preview'])
    
    def update_theme(self, bg_color, fg_color):
        """Update theme colors"""
        self.configure(bg=bg_color)
        for widget in self.winfo_children():
            try:
                if isinstance(widget, (tk.Label, tk.Frame, tk.Button)):
                    widget.configure(bg=bg_color)
                if hasattr(widget, 'fg'):
                    widget.configure(fg=fg_color)
            except:
                pass
    
    def on_show(self):
        """Called when frame is shown"""
        self.update_language()
    
    def go_back(self):
        """Return to home screen"""
        self.controller.show_frame('home')
    
    def choose_pdf(self):
        """Open file chooser for PDF"""
        filename = filedialog.askopenfilename(
            title=STRINGS[self.controller.current_lang]['select_pdf'],
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if filename:
            self.pdf_path = filename
            self.get_pdf_info()
            self.status_label.config(text=STRINGS[self.controller.current_lang]['ready'])
    
    def get_pdf_info(self):
        """Get PDF information"""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                self.total_pages = len(pdf_reader.pages)
                info_text = f"{STRINGS[self.controller.current_lang]['pages']}: {self.total_pages}"
                self.info_label.config(text=info_text)
        except Exception as e:
            self.info_label.config(text=STRINGS[self.controller.current_lang]['error'])
    
    def extract_text(self):
        """Extract text from PDF"""
        if not self.pdf_path:
            messagebox.showwarning("Warning",
                                  STRINGS[self.controller.current_lang]['select_pdf_first'])
            return
        
        if not PYPDF2_AVAILABLE:
            messagebox.showerror("Error",
                                STRINGS[self.controller.current_lang]['no_pypdf2'])
            return
        
        self.extract_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.progress_label.config(text=STRINGS[self.controller.current_lang]['extracting'])
        self.status_label.config(text=STRINGS[self.controller.current_lang]['extracting'])
        
        threading.Thread(target=self._extract_thread).start()
    
    def _extract_thread(self):
        """Background extraction thread"""
        try:
            text = ""
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for i, page in enumerate(pdf_reader.pages):
                    text += page.extract_text()
                    progress = ((i + 1) / self.total_pages) * 100
                    status = f"{STRINGS[self.controller.current_lang]['page']} {i+1} {STRINGS[self.controller.current_lang]['of']} {self.total_pages}"
                    self.after(0, lambda p=progress, s=status: self._update_progress(p, s))
            
            self.after(0, lambda: self._extract_complete(text))
            
        except Exception as e:
            self.after(0, lambda: self._extract_error(str(e)))
    
    def _update_progress(self, value, text):
        """Update progress display"""
        self.progress_bar['value'] = value
        self.status_label.config(text=text)
    
    def _extract_complete(self, text):
        """Handle extraction completion"""
        self.extracted_text = text
        self.text_area.delete('1.0', 'end')
        self.text_area.insert('1.0', text[:5000] + ("..." if len(text) > 5000 else ""))
        self.progress_bar['value'] = 100
        self.progress_label.config(text=STRINGS[self.controller.current_lang]['complete'])
        self.status_label.config(text=STRINGS[self.controller.current_lang]['complete'])
        self.save_btn.config(state='normal')
        self.copy_btn.config(state='normal')
        self.extract_btn.config(state='normal')
    
    def _extract_error(self, error):
        """Handle extraction error"""
        self.progress_label.config(text=STRINGS[self.controller.current_lang]['error'])
        self.status_label.config(text=STRINGS[self.controller.current_lang]['error'])
        self.extract_btn.config(state='normal')
        messagebox.showerror("Error", STRINGS[self.controller.current_lang]['error'])
    
    def save_text(self):
        """Save extracted text"""
        if not self.extracted_text:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"extracted_{timestamp}.txt"
            save_path = os.path.join(self.controller.get_storage_path('downloads'), filename)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.extracted_text)
            
            messagebox.showinfo("Success",
                               f"✓ Saved in: eyoTools > Downloads\nFile: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", STRINGS[self.controller.current_lang]['save_error'])
    
    def copy_text(self):
        """Copy text to clipboard"""
        if self.extracted_text:
            self.clipboard_clear()
            self.clipboard_append(self.extracted_text)
            messagebox.showinfo("Success", STRINGS[self.controller.current_lang]['copied'])
    
    def clear_all(self):
        """Clear all fields"""
        self.pdf_path = None
        self.extracted_text = ""
        self.info_label.config(text='')
        self.text_area.delete('1.0', 'end')
        self.progress_bar['value'] = 0
        self.progress_label.config(text='')
        self.status_label.config(text='')
        self.save_btn.config(state='disabled')
        self.copy_btn.config(state='disabled')


class PDFToAudioFrame(tk.Frame):
    """PDF to Audio Converter Frame"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#f0f0f0')
        
        self.pdf_path = None
        self.audio_path = None
        self.extracted_text = ""
        self.is_playing = False
        self.selected_lang = 'en'
        
        self.create_widgets()
        
        # Initialize pygame mixer
        if GTTS_AVAILABLE:
            pygame.mixer.init()
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg='#3498db', height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Button(header, text='←', font=('Arial', 16),
                 bg='#3498db', fg='white', relief='flat',
                 command=self.go_back).pack(side='left', padx=10)
        
        self.title_label = tk.Label(header, text='',
                                   font=('Arial', 14, 'bold'),
                                   bg='#3498db', fg='white')
        self.title_label.pack(side='left', padx=20)
        
        # Main content
        main = tk.Frame(self, bg='#f0f0f0', padx=20, pady=20)
        main.pack(fill='both', expand=True)
        
        # PDF selection
        select_frame = tk.Frame(main, bg='#f0f0f0')
        select_frame.pack(fill='x', pady=10)
        
        self.select_label = tk.Label(select_frame, text='',
                                     font=('Arial', 12),
                                     bg='#f0f0f0', fg='#333333')
        self.select_label.pack(side='left')
        
        self.select_btn = tk.Button(select_frame, text='',
                                    bg='#3498db', fg='white',
                                    font=('Arial', 11),
                                    command=self.choose_pdf)
        self.select_btn.pack(side='right')
        
        # Language selection
        lang_frame = tk.Frame(main, bg='#f0f0f0')
        lang_frame.pack(fill='x', pady=10)
        
        self.lang_label = tk.Label(lang_frame, text='',
                                   font=('Arial', 12),
                                   bg='#f0f0f0', fg='#333333')
        self.lang_label.pack(side='left')
        
        self.lang_var = tk.StringVar(value='English')
        self.lang_combo = ttk.Combobox(lang_frame,
                                       textvariable=self.lang_var,
                                       values=['English', 'አማርኛ'],
                                       state='readonly',
                                       font=('Arial', 11))
        self.lang_combo.pack(side='right')
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_language_select)
        
        # Convert button
        self.convert_btn = tk.Button(main, text='',
                                     bg='#27ae60', fg='white',
                                     font=('Arial', 12, 'bold'),
                                     command=self.convert_to_audio)
        self.convert_btn.pack(fill='x', pady=10)
        
        # Progress section
        progress_frame = tk.Frame(main, bg='#f0f0f0')
        progress_frame.pack(fill='x', pady=10)
        
        self.progress_label = tk.Label(progress_frame, text='',
                                       font=('Arial', 11),
                                       bg='#f0f0f0', fg='#333333')
        self.progress_label.pack(anchor='w')
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=300,
                                            mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)
        
        self.status_label = tk.Label(progress_frame, text='',
                                     font=('Arial', 10),
                                     bg='#f0f0f0', fg='#666666')
        self.status_label.pack(anchor='w')
        
        # Audio controls
        audio_frame = tk.Frame(main, bg='#f0f0f0')
        audio_frame.pack(fill='x', pady=20)
        
        self.play_btn = tk.Button(audio_frame, text='',
                                  bg='#3498db', fg='white',
                                  font=('Arial', 12),
                                  command=self.play_audio,
                                  state='disabled')
        self.play_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        self.stop_btn = tk.Button(audio_frame, text='',
                                  bg='#e74c3c', fg='white',
                                  font=('Arial', 12),
                                  command=self.stop_audio,
                                  state='disabled')
        self.stop_btn.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Save button
        self.save_btn = tk.Button(main, text='',
                                  bg='#9b59b6', fg='white',
                                  font=('Arial', 11),
                                  command=self.save_audio,
                                  state='disabled')
        self.save_btn.pack(fill='x', pady=5)
        
        # Clear button
        self.clear_btn = tk.Button(main, text='',
                                   bg='#95a5a6', fg='white',
                                   font=('Arial', 11),
                                   command=self.clear_all)
        self.clear_btn.pack(fill='x', pady=5)
        
        self.update_language()
    
    def update_language(self):
        """Update UI language"""
        self.title_label.config(text=STRINGS[self.controller.current_lang]['pdf_to_audio'])
        self.select_label.config(text=STRINGS[self.controller.current_lang]['select_pdf'])
        self.select_btn.config(text=STRINGS[self.controller.current_lang]['choose_pdf'])
        self.lang_label.config(text=STRINGS[self.controller.current_lang]['select_lang'])
        self.convert_btn.config(text=STRINGS[self.controller.current_lang]['convert'])
        self.play_btn.config(text=STRINGS[self.controller.current_lang]['play'])
        self.stop_btn.config(text=STRINGS[self.controller.current_lang]['stop'])
        self.save_btn.config(text=STRINGS[self.controller.current_lang]['save_audio'])
        self.clear_btn.config(text=STRINGS[self.controller.current_lang]['clear'])
    
    def update_theme(self, bg_color, fg_color):
        """Update theme colors"""
        self.configure(bg=bg_color)
        for widget in self.winfo_children():
            try:
                if isinstance(widget, (tk.Label, tk.Frame, tk.Button)):
                    widget.configure(bg=bg_color)
                if hasattr(widget, 'fg'):
                    widget.configure(fg=fg_color)
            except:
                pass
    
    def on_show(self):
        """Called when frame is shown"""
        self.update_language()
    
    def go_back(self):
        """Return to home screen"""
        self.stop_audio()
        self.controller.show_frame('home')
    
    def choose_pdf(self):
        """Open file chooser for PDF"""
        filename = filedialog.askopenfilename(
            title=STRINGS[self.controller.current_lang]['select_pdf'],
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if filename:
            self.pdf_path = filename
            self.status_label.config(text=STRINGS[self.controller.current_lang]['ready'])
    
    def on_language_select(self, event):
        """Handle language selection"""
        if self.lang_var.get() == 'አማርኛ':
            self.selected_lang = 'am'
        else:
            self.selected_lang = 'en'
    
    def convert_to_audio(self):
        """Convert PDF to audio"""
        if not self.pdf_path:
            messagebox.showwarning("Warning",
                                  STRINGS[self.controller.current_lang]['select_pdf_first'])
            return
        
        if not PYPDF2_AVAILABLE:
            messagebox.showerror("Error", STRINGS[self.controller.current_lang]['no_pypdf2'])
            return
        
        if not GTTS_AVAILABLE:
            messagebox.showerror("Error", STRINGS[self.controller.current_lang]['no_gtts'])
            return
        
        self.convert_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.progress_label.config(text=STRINGS[self.controller.current_lang]['extracting'])
        self.status_label.config(text=STRINGS[self.controller.current_lang]['extracting'])
        
        threading.Thread(target=self._convert_thread).start()
    
    def _convert_thread(self):
        """Background conversion thread"""
        try:
            # Extract text from PDF
            self.after(0, lambda: self._update_progress(20, STRINGS[self.controller.current_lang]['extracting']))
            
            text = ""
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            self.extracted_text = text
            
            if not text.strip():
                raise Exception("No text found in PDF")
            
            # Convert to speech
            self.after(0, lambda: self._update_progress(50, STRINGS[self.controller.current_lang]['converting']))
            
            lang_code = 'am' if self.selected_lang == 'am' else 'en'
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            temp_path = os.path.join(self.controller.get_storage_path('audio'), 'temp_audio.mp3')
            tts.save(temp_path)
            
            self.after(0, lambda: self._convert_complete(temp_path))
            
        except Exception as e:
            self.after(0, lambda: self._convert_error(str(e)))
    
    def _update_progress(self, value, text):
        """Update progress display"""
        self.progress_bar['value'] = value
        self.status_label.config(text=text)
    
    def _convert_complete(self, audio_path):
        """Handle conversion completion"""
        self.audio_path = audio_path
        self.progress_bar['value'] = 100
        self.progress_label.config(text=STRINGS[self.controller.current_lang]['complete'])
        self.status_label.config(text=STRINGS[self.controller.current_lang]['complete'])
        self.play_btn.config(state='normal')
        self.save_btn.config(state='normal')
        self.convert_btn.config(state='normal')
        messagebox.showinfo("Success", STRINGS[self.controller.current_lang]['complete'])
    
    def _convert_error(self, error):
        """Handle conversion error"""
        self.progress_label.config(text=STRINGS[self.controller.current_lang]['error'])
        self.status_label.config(text=STRINGS[self.controller.current_lang]['error'])
        self.convert_btn.config(state='normal')
        messagebox.showerror("Error", STRINGS[self.controller.current_lang]['error'])
    
    def play_audio(self):
        """Play audio"""
        if not self.audio_path:
            return
        
        try:
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.play_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_label.config(text=STRINGS[self.controller.current_lang]['playing'])
        except Exception as e:
            messagebox.showerror("Error", STRINGS[self.controller.current_lang]['error'])
    
    def stop_audio(self):
        """Stop audio"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text=STRINGS[self.controller.current_lang]['stopped'])
    
    def save_audio(self):
        """Save audio file"""
        if not self.audio_path:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"audiobook_{timestamp}.mp3"
            save_path = os.path.join(self.controller.get_storage_path('audio'), filename)
            
            shutil.copy2(self.audio_path, save_path)
            
            messagebox.showinfo("Success",
                               f"✓ Saved in: eyoTools > Audio\nFile: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", STRINGS[self.controller.current_lang]['save_error'])
    
    def clear_all(self):
        """Clear all fields"""
        self.stop_audio()
        self.pdf_path = None
        self.audio_path = None
        self.extracted_text = ""
        self.progress_bar['value'] = 0
        self.progress_label.config(text='')
        self.status_label.config(text='')
        self.play_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        self.convert_btn.config(state='normal')