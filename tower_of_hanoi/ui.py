# Tower of Hanoi - GUI with CustomTkinter
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
import random
from . import algorithm
from .db import Database

# Appearance settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color theme
C = {
    'bg_dark': '#0a0e27', 'card_bg': '#151932', 'accent': '#6366f1',
    'accent_hover': '#4f46e5', 'text_primary': '#f8fafc', 'text_secondary': '#94a3b8',
    'success': '#22c55e', 'warning': '#f59e0b', 'error': '#ef4444',
    'gold': '#fbbf24', 'silver': '#9ca3af', 'bronze': '#d97706',
    'bg': '#0a0e27', 'panel': '#151932', 'primary': '#6366f1',
    'secondary': '#4f46e5', 'text': '#f8fafc'
}


class GameUI:
    """Game canvas with towers and disks - handles rendering and user interaction"""
    
    def __init__(self, root, disks, pegs, player, on_win, on_move, on_move_sequence=None):
        self.root = root
        self.disks = disks
        self.pegs = pegs
        self.player = player
        self.on_win = on_win
        self.on_move = on_move
        self.on_move_sequence = on_move_sequence
        
        self.peg_names = ['A', 'B', 'C', 'D'][:pegs]
        self.towers = {p: [] for p in self.peg_names}
        self.towers['A'] = list(range(disks, 0, -1))
        self.selected = None
        self.moves = 0
        self.animating = False
        self.cancelled = False
        self.move_history = []
        
        # Canvas setup
        self.w = 1200 if pegs == 4 else 1000
        self.h = 500
        self.canvas = tk.Canvas(root, width=self.w, height=self.h, bg=C['bg_dark'], highlightthickness=0, bd=0)
        self.canvas.pack(pady=20, expand=True)
        self.canvas.bind('<Button-1>', self._click)
        
        self.colors = self._gen_colors(disks)
        self.draw()
    
    def _gen_colors(self, n):
        """Generate gradient colors for disks"""
        colors = []
        for i in range(n):
            r = int(99 + (i * 12))
            g = int(102 - (i * 4))
            b = int(241 - (i * 8))
            colors.append(f'#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}')
        return colors
    
    def draw(self):
        """Render towers and disks on canvas"""
        self.canvas.delete('all')
        spacing = self.w / (self.pegs + 1)
        pos = {self.peg_names[i]: int(spacing * (i + 1)) for i in range(self.pegs)}
        
        # Base gradient
        for i in range(8):
            shade = int(21 + i * 2)
            self.canvas.create_rectangle(40, 420-i, self.w-40, 450-i, 
                fill=f'#{shade:02x}{25+i:02x}{50+i:02x}', outline='')
        
        # Pegs with glow
        for p in self.peg_names:
            x = pos[p]
            for i in range(4):
                alpha = 60 - i * 12
                self.canvas.create_rectangle(x-10-i, 140+i, x+10+i, 420, 
                    fill=f'#{alpha:02x}{alpha:02x}{alpha+20:02x}', outline='')
            self.canvas.create_rectangle(x-7, 140, x+7, 420, fill=C['card_bg'], outline=C['accent'], width=2)
            self.canvas.create_oval(x-28, 440, x+28, 496, fill=C['card_bg'], outline=C['accent'], width=3)
            self.canvas.create_text(x, 468, text=p, font=('Segoe UI', 16, 'bold'), fill=C['text_primary'])
        
        # Disks
        for p in self.peg_names:
            x = pos[p]
            for i, d in enumerate(self.towers[p]):
                w = 50 + (140 * d / self.disks)
                y1, y2 = 395 - i*28, 420 - i*28
                self.canvas.create_rectangle(x-w/2+4, y1+4, x+w/2+4, y2+4, fill='#05071a', outline='')
                color = self.colors[d-1]
                self.canvas.create_rectangle(x-w/2, y1, x+w/2, y2, fill=color, outline=C['text_primary'], width=2)
                self.canvas.create_line(x-w/2+4, y1+4, x+w/2-4, y1+4, fill='#ffffff', width=2)
                self.canvas.create_text(x, (y1+y2)/2, text=str(d), font=('Segoe UI', 10, 'bold'), fill='white')
        
        # Selection highlight
        if self.selected and self.towers[self.selected]:
            x = pos[self.selected]
            d = self.towers[self.selected][-1]
            w = 50 + (140 * d / self.disks)
            i = len(self.towers[self.selected]) - 1
            y1, y2 = 395 - i*28, 420 - i*28
            for j in [10, 6, 3]:
                self.canvas.create_rectangle(x-w/2-j, y1-j, x+w/2+j, y2+j, outline=C['gold'], width=2)
    
    def _click(self, e):
        """Handle peg click for selection/movement"""
        if self.animating: return
        spacing = self.w / (self.pegs + 1)
        for i, p in enumerate(self.peg_names):
            x = spacing * (i + 1)
            if abs(e.x - x) < 80:
                if self.selected is None:
                    if self.towers[p]:
                        self.selected = p
                        self.draw()
                elif self.selected == p:
                    self.selected = None
                    self.draw()
                else:
                    self._move(self.selected, p)
                return
    
    def _move(self, frm, to):
        """Execute disk move with validation"""
        if not self.towers[frm]: return
        disk = self.towers[frm][-1]
        if self.towers[to] and self.towers[to][-1] < disk:
            messagebox.showwarning("Invalid", "Can't place larger disk on smaller!")
            return
        self.towers[frm].pop()
        self.towers[to].append(disk)
        self.moves += 1
        self.move_history.append((frm, to))
        self.selected = None
        self.draw()
        self.on_move(self.moves)
        if self.on_move_sequence:
            self.on_move_sequence(self.move_history)
        if len(self.towers[self.peg_names[-1]]) == self.disks:
            self.on_win()
    
    def reset(self):
        """Reset game to initial state"""
        self.towers = {p: [] for p in self.peg_names}
        self.towers['A'] = list(range(self.disks, 0, -1))
        self.selected = None
        self.moves = 0
        self.move_history = []
        self.draw()
        if self.on_move_sequence:
            self.on_move_sequence([])
    
    def auto_play(self, algo_name, on_done):
        """Start auto-play animation for single algorithm"""
        if self.animating: return
        self.reset()
        self.animating = True
        self.cancelled = False
        threading.Thread(target=self._run_algo, args=(algo_name, on_done), daemon=True).start()
    
    def _run_algo(self, algo_name, on_done):
        """Execute algorithm and animate moves"""
        funcs = {
            'recursive_3peg': lambda n: algorithm.hanoi_recursive_3peg(n, 'A', 'C', 'B'),
            'iterative_3peg': lambda n: algorithm.hanoi_iterative_3peg(n, 'A', 'C', 'B'),
            'frame_stewart': lambda n: algorithm.hanoi_frame_stewart(n, 'A', 'D', 'B', 'C')
        }
        start = time.time()
        moves = funcs[algo_name](self.disks)
        elapsed = time.time() - start
        
        for frm, to in moves:
            if self.cancelled: break
            disk = self.towers[frm].pop()
            self.towers[to].append(disk)
            self.moves += 1
            self.move_history.append((frm, to))
            self.root.after(0, lambda m=self.moves: self.on_move(m))
            self.root.after(0, self.draw)
            if self.on_move_sequence:
                self.root.after(0, lambda h=list(self.move_history): self.on_move_sequence(h))
            time.sleep(max(0.05, 0.3 / self.disks))
        
        self.animating = False
        self.root.after(0, lambda: on_done(algo_name, len(moves), elapsed))
    
    def cancel(self):
        self.cancelled = True
    
    def auto_play_3peg_both(self, on_done):
        """Run both 3-peg algorithms and collect timing data"""
        if self.animating: return
        self.reset()
        self.animating = True
        self.cancelled = False
        threading.Thread(target=self._run_both_3peg_algos, args=(on_done,), daemon=True).start()
    
    def _run_both_3peg_algos(self, on_done):
        """Run recursive and iterative, save timing for both, animate one"""
        results = {}
        
        # Run recursive and measure time
        start = time.time()
        recursive_moves = algorithm.hanoi_recursive_3peg(self.disks, 'A', 'C', 'B')
        recursive_elapsed = time.time() - start
        results['recursive_3peg'] = (len(recursive_moves), recursive_elapsed)
        
        # Run iterative and measure time
        start = time.time()
        iterative_moves = algorithm.hanoi_iterative_3peg(self.disks, 'A', 'C', 'B')
        iterative_elapsed = time.time() - start
        results['iterative_3peg'] = (len(iterative_moves), iterative_elapsed)
        
        # Animate using recursive moves
        for frm, to in recursive_moves:
            if self.cancelled: break
            disk = self.towers[frm].pop()
            self.towers[to].append(disk)
            self.moves += 1
            self.move_history.append((frm, to))
            self.root.after(0, lambda m=self.moves: self.on_move(m))
            self.root.after(0, self.draw)
            if self.on_move_sequence:
                self.root.after(0, lambda h=list(self.move_history): self.on_move_sequence(h))
            time.sleep(max(0.05, 0.3 / self.disks))
        
        self.animating = False
        self.root.after(0, lambda: on_done(results))


class MainApp:
    """Main application with menu and game screens"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🎯 Tower of Hanoi")
        self.root.attributes('-fullscreen', True)
        self.root.configure(fg_color=C['bg_dark'])
        
        # Keyboard bindings
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen')))
        
        self.db = Database()
        self.game = None
        self.player = "Player"
        self.disks = 5
        self.pegs = 3
        
        self._show_menu()
    
    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()
    
    def _show_menu(self):
        """Display main menu"""
        self._clear()
        
        main_frame = ctk.CTkFrame(self.root, fg_color=C['bg_dark'])
        main_frame.pack(fill='both', expand=True)
        
        # Header
        hdr = ctk.CTkFrame(main_frame, fg_color=C['accent'], corner_radius=0, height=120)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        
        ctk.CTkLabel(hdr, text="🎯 TOWER OF HANOI", 
            font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold"), 
            text_color=C['text_primary']).pack(pady=30)
        
        ctk.CTkLabel(main_frame, text="Press ESC to exit fullscreen | F11 to toggle", 
            font=ctk.CTkFont(size=12), text_color=C['text_secondary']).pack(pady=10)
        
        # Menu buttons
        menu = ctk.CTkFrame(main_frame, fg_color="transparent")
        menu.pack(expand=True)
        
        btns = [
            ("🎮  PLAY GAME", self._start_game),
            ("📊  COMPARISON", self._show_comparison),
            ("🥇  LEADERBOARD", self._leaderboard),
            ("❌  EXIT", self._exit_game)
        ]
        
        for text, cmd in btns:
            btn = ctk.CTkButton(menu, text=text, 
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                fg_color=C['card_bg'], hover_color=C['accent'],
                text_color=C['text_primary'], width=320, height=55,
                corner_radius=12, command=cmd)
            btn.pack(pady=10)
    
    def _exit_game(self):
        """Properly exit the game and destroy window"""
        self.root.quit()
        self.root.destroy()
    
    def _start_game(self):
        """Show new game setup dialog"""
        self.disks = random.randint(5, 10)
        self.predicted_moves = None
        
        dlg = ctk.CTkToplevel(self.root)
        dlg.title("New Game")
        dlg.geometry("480x550")
        dlg.configure(fg_color=C['bg_dark'])
        dlg.transient(self.root)
        dlg.grab_set()
        
        # Center dialog
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() - 480) // 2
        y = (dlg.winfo_screenheight() - 550) // 2
        dlg.geometry(f'480x550+{x}+{y}')
        
        ctk.CTkLabel(dlg, text="🎮 New Game Setup", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), 
            text_color=C['accent']).pack(pady=25)
        
        # Player name
        name_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        name_frame.pack(pady=15, fill='x', padx=40)
        ctk.CTkLabel(name_frame, text="Player Name:", 
            font=ctk.CTkFont(size=14), text_color=C['text_primary']).pack(anchor='w')
        name_entry = ctk.CTkEntry(name_frame, font=ctk.CTkFont(size=14), 
            fg_color=C['card_bg'], text_color=C['text_primary'],
            border_color=C['accent'], width=380, height=45)
        name_entry.pack(fill='x', pady=8)
        name_entry.insert(0, "Player")
        name_entry.select_range(0, tk.END)
        name_entry.focus_set()
        
        ctk.CTkLabel(dlg, text=f"🎲 Challenge: {self.disks} disks!", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), 
            text_color=C['gold']).pack(pady=20)
        
        # Peg selection
        ctk.CTkLabel(dlg, text="Select number of pegs:", 
            font=ctk.CTkFont(size=14), text_color=C['text_primary']).pack(pady=8)
        
        pegs_var = tk.IntVar(value=3)
        peg_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        peg_frame.pack(pady=10)
        
        ctk.CTkRadioButton(peg_frame, text="3 Pegs (Classic)", variable=pegs_var, value=3, 
            font=ctk.CTkFont(size=14), fg_color=C['accent'], 
            text_color=C['text_primary']).pack(anchor='w', pady=6)
        ctk.CTkRadioButton(peg_frame, text="4 Pegs (Frame-Stewart)", variable=pegs_var, value=4,
            font=ctk.CTkFont(size=14), fg_color=C['accent'], 
            text_color=C['text_primary']).pack(anchor='w', pady=6)
        
        def start():
            name = name_entry.get().strip() or "Player"
            self.player = name
            self.pegs = pegs_var.get()
            dlg.destroy()
            self._show_game()
        
        dlg.bind('<Return>', lambda e: start())
        
        ctk.CTkButton(dlg, text="▶  START GAME", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), 
            fg_color=C['success'], hover_color='#16a34a',
            text_color='white', width=220, height=50, corner_radius=12,
            command=start).pack(pady=30)
    
    def _show_game(self):
        """Display game screen with towers and controls"""
        self._clear()
        
        main_container = ctk.CTkFrame(self.root, fg_color=C['bg_dark'])
        main_container.pack(fill='both', expand=True)
        
        # Left panel - move sequence and prediction
        left_panel = ctk.CTkFrame(main_container, fg_color=C['card_bg'], width=250, corner_radius=15)
        left_panel.pack(side='left', fill='y', padx=(20, 0), pady=20)
        left_panel.pack_propagate(False)
        
        ctk.CTkLabel(left_panel, text="🎯 Predict Moves", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), 
            text_color=C['gold']).pack(pady=(20, 10))
        
        ctk.CTkLabel(left_panel, text="Enter minimum moves:", 
            font=ctk.CTkFont(size=12), text_color=C['text_secondary']).pack()
        
        self.prediction_entry = ctk.CTkEntry(left_panel, font=ctk.CTkFont(size=16), 
            fg_color=C['bg_dark'], text_color=C['gold'],
            border_color=C['accent'], width=120, height=45, justify='center')
        self.prediction_entry.pack(pady=10)
        
        self.prediction_error = ctk.CTkLabel(left_panel, text="", 
            font=ctk.CTkFont(size=10), text_color=C['error'])
        self.prediction_error.pack()
        
        ctk.CTkFrame(left_panel, fg_color=C['accent'], height=2).pack(fill='x', pady=15, padx=15)
        
        ctk.CTkLabel(left_panel, text="📋 Move Sequence", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), 
            text_color=C['accent']).pack(pady=10)
        
        self.move_seq_text = ctk.CTkTextbox(left_panel, height=350, width=200, 
            font=ctk.CTkFont(family="Consolas", size=11), 
            fg_color=C['bg_dark'], text_color=C['text_primary'], corner_radius=10)
        self.move_seq_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Right panel - game area
        right_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        right_panel.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        
        # Top bar
        top = ctk.CTkFrame(right_panel, fg_color=C['card_bg'], corner_radius=15, height=80)
        top.pack(fill='x')
        top.pack_propagate(False)
        
        ctk.CTkLabel(top, text=f"🎮 {self.player}'s Game | {self.disks} Disks | {self.pegs} Pegs",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), 
            text_color=C['text_primary']).pack(side='left', padx=25, pady=25)
        
        self.move_lbl = ctk.CTkLabel(top, text="Moves: 0", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), 
            text_color=C['success'])
        self.move_lbl.pack(side='right', padx=25)
        
        self.info_lbl = ctk.CTkLabel(right_panel, text="Click a disk to select, then click a peg to move",
            font=ctk.CTkFont(size=13), text_color=C['text_secondary'])
        self.info_lbl.pack(pady=10)
        
        # Game canvas
        game_frame = ctk.CTkFrame(right_panel, fg_color=C['bg_dark'], corner_radius=15)
        game_frame.pack(expand=True)
        self.game = GameUI(game_frame, self.disks, self.pegs, self.player, self._on_win, self._on_move, self._on_move_sequence)
        
        # Control buttons
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        self.auto_btn = self._ctk_btn(btn_frame, "🤖 Auto-Play", self._auto, C['accent'])
        self.auto_btn.pack(side='left', padx=15)
        
        self.cancel_btn = self._ctk_btn(btn_frame, "⏹ Cancel", self._cancel, C['error'])
        self.cancel_btn.pack(side='left', padx=15)
        self.cancel_btn.configure(state='disabled')
        
        act_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        act_frame.pack(pady=10)
        
        self._ctk_btn(act_frame, "🔄 Reset", self._reset, C['warning']).pack(side='left', padx=8)
        self._ctk_btn(act_frame, "← Back to Menu", self._back_to_menu, C['accent_hover']).pack(side='left', padx=8)
    
    def _ctk_btn(self, parent, text, cmd, bg=None):
        """Create styled button"""
        bg = bg or C['accent']
        return ctk.CTkButton(parent, text=text, 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=bg, hover_color=C['accent_hover'],
            text_color='white', width=160, height=42, corner_radius=10, command=cmd)
    
    def _btn(self, parent, text, cmd, bg=None):
        return self._ctk_btn(parent, text, cmd, bg)
    
    def _on_move(self, moves):
        self.move_lbl.configure(text=f"Moves: {moves}")
    
    def _on_move_sequence(self, move_history):
        """Update move sequence display"""
        self.move_seq_text.delete("1.0", "end")
        for i, (frm, to) in enumerate(move_history, 1):
            self.move_seq_text.insert("end", f"{i}. {frm} → {to}\n")
        self.move_seq_text.see("end")
    
    def _get_prediction(self):
        """Validate and return prediction input"""
        prediction_text = self.prediction_entry.get().strip()
        if not prediction_text:
            self.prediction_error.configure(text="Enter your prediction!")
            return None
        try:
            prediction = int(prediction_text)
            if prediction <= 0:
                self.prediction_error.configure(text="Enter a positive number!")
                return None
            self.prediction_error.configure(text="")
            return prediction
        except ValueError:
            self.prediction_error.configure(text="Enter a valid number!")
            return None
    
    def _on_win(self):
        """Handle game completion"""
        if self.pegs == 3:
            min_m = len(algorithm.hanoi_recursive_3peg(self.disks))
        else:
            min_m = len(algorithm.hanoi_frame_stewart(self.disks))
        m = self.game.moves
        
        self.predicted_moves = self._get_prediction()
        if self.predicted_moves is None:
            messagebox.showwarning("Prediction Required", "Please enter your predicted number of moves before completing!")
            return
        
        is_correct_prediction = self.predicted_moves == min_m
        
        if is_correct_prediction:
            msg = f"🎉 YOU WIN!\n\nYour prediction: {self.predicted_moves}\nActual minimum moves: {min_m}\n\n⭐ You correctly predicted the minimum moves!"
            self.db.save_game(self.player, self.disks, self.pegs, m, min_m, self.predicted_moves, True, None, 0)
            messagebox.showinfo("🏆 Victory!", msg)
        else:
            msg = f"😔 YOU LOSE!\n\nYour prediction: {self.predicted_moves}\nActual minimum moves: {min_m}\n\nBetter luck next time!"
            self.db.save_game(self.player, self.disks, self.pegs, m, min_m, self.predicted_moves, False, None, 0)
            messagebox.showinfo("Game Over", msg)
        
        self._show_menu()
    
    def _back_to_menu(self):
        if messagebox.askyesno("Quit Game", "Return to main menu?\nYour progress will be lost."):
            self._show_menu()
    
    def _reset(self):
        if messagebox.askyesno("Reset", "Reset the game?"):
            self.game.reset()
            self._on_move(0)
            self.prediction_entry.delete(0, tk.END)
    
    def _auto(self):
        """Start auto-play mode"""
        self.predicted_moves = self._get_prediction()
        if self.predicted_moves is None:
            messagebox.showwarning("Prediction Required", "Please enter your predicted number of moves before auto-play!")
            return
        
        if not messagebox.askyesno("Auto-Play", "Run auto-play?\nThis will reset the game."): return
        self.info_lbl.configure(text="Running auto-play...", text_color=C['gold'])
        
        self.move_seq_text.delete("1.0", "end")
        self.cancel_btn.configure(state='normal')
        self.auto_btn.configure(state='disabled')
        
        if self.pegs == 3:
            self.game.auto_play_3peg_both(self._auto_done_3peg_both)
        else:
            self.game.auto_play('frame_stewart', self._auto_done)
    
    def _cancel(self):
        self.game.cancel()
        self.info_lbl.configure(text="Cancelled", text_color=C['error'])
        self.cancel_btn.configure(state='disabled')
        self.auto_btn.configure(state='normal')
    
    def _auto_done(self, algo, moves, elapsed):
        """Handle 4-peg auto-play completion"""
        self.cancel_btn.configure(state='disabled')
        self.auto_btn.configure(state='normal')
        
        elapsed_ms = elapsed * 1000
        self.info_lbl.configure(text=f"✅ {moves} moves in {elapsed_ms:.1f}ms", text_color=C['success'])
        min_m = len(algorithm.hanoi_frame_stewart(self.disks))
        
        is_correct_prediction = self.predicted_moves == min_m
        self.db.save_algo_perf(algo, self.disks, self.pegs, moves, elapsed_ms)
        
        self.root.after(500, lambda: self._show_auto_result(algo, moves, min_m, elapsed_ms, is_correct_prediction))
    
    def _auto_done_3peg_both(self, results):
        """Handle 3-peg both algorithms completion"""
        self.cancel_btn.configure(state='disabled')
        self.auto_btn.configure(state='normal')
        
        recursive_moves, recursive_elapsed = results['recursive_3peg']
        iterative_moves, iterative_elapsed = results['iterative_3peg']
        
        recursive_ms = recursive_elapsed * 1000
        iterative_ms = iterative_elapsed * 1000
        
        self.info_lbl.configure(text=f"✅ Recursive: {recursive_ms:.1f}ms | Iterative: {iterative_ms:.1f}ms", text_color=C['success'])
        
        min_m = len(algorithm.hanoi_recursive_3peg(self.disks))
        is_correct_prediction = self.predicted_moves == min_m
        
        self.db.save_algo_perf('recursive_3peg', self.disks, self.pegs, recursive_moves, recursive_ms)
        self.db.save_algo_perf('iterative_3peg', self.disks, self.pegs, iterative_moves, iterative_ms)
        
        self.root.after(500, lambda: self._show_auto_result_3peg_both(
            recursive_moves, min_m, recursive_ms, iterative_ms, is_correct_prediction))
    
    def _show_auto_result_3peg_both(self, moves, min_m, recursive_ms, iterative_ms, is_correct):
        """Show result after 3-peg auto-play"""
        if is_correct:
            msg = f"🎉 YOU WIN!\n\nYour prediction: {self.predicted_moves}\nActual minimum moves: {min_m}\n\n⭐ You correctly predicted the minimum moves!\n\nRecursive: {recursive_ms:.2f}ms\nIterative: {iterative_ms:.2f}ms"
            self.db.save_game(self.player, self.disks, self.pegs, moves, min_m, self.predicted_moves, True, 'recursive_3peg', recursive_ms)
            self.db.save_game(self.player, self.disks, self.pegs, moves, min_m, self.predicted_moves, True, 'iterative_3peg', iterative_ms)
            self.db.save_winner(self.player, self.disks, self.pegs, moves, min_m, self.predicted_moves, 'recursive_3peg', recursive_ms)
            self.db.save_winner(self.player, self.disks, self.pegs, moves, min_m, self.predicted_moves, 'iterative_3peg', iterative_ms)
            messagebox.showinfo("🏆 Victory!", msg)
        else:
            msg = f"😔 YOU LOSE!\n\nYour prediction: {self.predicted_moves}\nActual minimum moves: {min_m}\n\nBetter luck next time!\n\nRecursive: {recursive_ms:.2f}ms\nIterative: {iterative_ms:.2f}ms"
            self.db.save_game(self.player, self.disks, self.pegs, moves, min_m, self.predicted_moves, False, 'recursive_3peg', recursive_ms)
            self.db.save_game(self.player, self.disks, self.pegs, moves, min_m, self.predicted_moves, False, 'iterative_3peg', iterative_ms)
            messagebox.showinfo("Game Over", msg)
        
        self._show_menu()
    
    def _show_auto_result(self, algo, moves, min_m, elapsed_ms, is_correct):
        """Show result after 4-peg auto-play"""
        if is_correct:
            msg = f"🎉 YOU WIN!\n\nYour prediction: {self.predicted_moves}\nActual minimum moves: {min_m}\n\n⭐ You correctly predicted the minimum moves!\n\n{algo}: {elapsed_ms:.2f}ms"
            self.db.save_game(self.player, self.disks, self.pegs, moves, min_m, self.predicted_moves, True, algo, elapsed_ms)
            self.db.save_winner(self.player, self.disks, self.pegs, moves, min_m, self.predicted_moves, algo, elapsed_ms)
            messagebox.showinfo("🏆 Victory!", msg)
        else:
            msg = f"😔 YOU LOSE!\n\nYour prediction: {self.predicted_moves}\nActual minimum moves: {min_m}\n\nBetter luck next time!\n\n{algo}: {elapsed_ms:.2f}ms"
            self.db.save_game(self.player, self.disks, self.pegs, moves, min_m, self.predicted_moves, False, algo, elapsed_ms)
            messagebox.showinfo("Game Over", msg)
        
        self._show_menu()
    
    def _show_comparison(self):
        """Display 3-peg vs 4-peg comparison table"""
        self._clear()
        
        main_frame = ctk.CTkFrame(self.root, fg_color=C['bg_dark'])
        main_frame.pack(fill='both', expand=True)
        
        # Header
        hdr = ctk.CTkFrame(main_frame, fg_color=C['accent'], corner_radius=0, height=80)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="📊 3-Peg vs 4-Peg Comparison", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), 
            text_color=C['text_primary']).pack(pady=20)
        
        ctk.CTkLabel(main_frame, text="Comparing 3-Peg (Recursive) vs 4-Peg (Frame-Stewart) from played games", 
            font=ctk.CTkFont(size=13), text_color=C['text_secondary']).pack(pady=15)
        
        center_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_container.pack(expand=True)
        
        comparison_data = self._build_comparison_data()
        
        if not comparison_data:
            # No data message
            no_data_frame = ctk.CTkFrame(center_container, fg_color=C['card_bg'], corner_radius=15)
            no_data_frame.pack(pady=50, padx=50)
            ctk.CTkLabel(no_data_frame, text="📭 No comparison data available", 
                font=ctk.CTkFont(size=18, weight="bold"), 
                text_color=C['warning']).pack(pady=30, padx=50)
            ctk.CTkLabel(no_data_frame, text="Play games with both 3-peg and 4-peg modes\nusing the same number of disks to see comparisons.", 
                font=ctk.CTkFont(size=13), text_color=C['text_secondary']).pack(pady=(0, 30), padx=50)
        else:
            # Build comparison table
            table_container = ctk.CTkFrame(center_container, fg_color=C['card_bg'], corner_radius=15)
            table_container.pack(pady=20, padx=40)
            
            # Table header
            header_frame = ctk.CTkFrame(table_container, fg_color=C['accent'], corner_radius=10)
            header_frame.pack(fill='x', padx=10, pady=(10, 5))
            
            headers = ["Disks", "3-Peg Moves", "4-Peg Moves", "Saved Moves", 
                       "3-Peg Time", "4-Peg Time", "Saved Time"]
            col_widths = [80, 120, 120, 120, 120, 120, 120]
            
            header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_inner.pack(pady=12, padx=10)
            
            for i, (header, width) in enumerate(zip(headers, col_widths)):
                ctk.CTkLabel(header_inner, text=header, 
                    font=ctk.CTkFont(size=12, weight="bold"), 
                    text_color=C['text_primary'], width=width).grid(row=0, column=i, padx=5)
            
            # Table rows
            for row_idx, row_data in enumerate(comparison_data):
                disks, moves_3peg, moves_4peg, time_3peg, time_4peg = row_data
                
                saved_moves = moves_3peg - moves_4peg
                saved_moves_pct = (saved_moves / moves_3peg * 100) if moves_3peg > 0 else 0
                saved_time = time_3peg - time_4peg
                saved_time_pct = (saved_time / time_3peg * 100) if time_3peg > 0 else 0
                
                # Alternating row colors
                row_bg = C['bg_dark'] if row_idx % 2 == 0 else '#1a1f3d'
                
                row_frame = ctk.CTkFrame(table_container, fg_color=row_bg, corner_radius=8)
                row_frame.pack(fill='x', padx=10, pady=2)
                
                row_inner = ctk.CTkFrame(row_frame, fg_color="transparent")
                row_inner.pack(pady=10, padx=10)
                
                ctk.CTkLabel(row_inner, text=str(disks), 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=C['gold'], width=col_widths[0]).grid(row=0, column=0, padx=5)
                
                ctk.CTkLabel(row_inner, text=f"{moves_3peg:,}", 
                    font=ctk.CTkFont(size=13), 
                    text_color=C['text_primary'], width=col_widths[1]).grid(row=0, column=1, padx=5)
                
                ctk.CTkLabel(row_inner, text=f"{moves_4peg:,}", 
                    font=ctk.CTkFont(size=13), 
                    text_color=C['text_primary'], width=col_widths[2]).grid(row=0, column=2, padx=5)
                
                ctk.CTkLabel(row_inner, text=f"{saved_moves:,} ({saved_moves_pct:.1f}%)", 
                    font=ctk.CTkFont(size=13, weight="bold"), 
                    text_color=C['success'], width=col_widths[3]).grid(row=0, column=3, padx=5)
                
                ctk.CTkLabel(row_inner, text=f"{time_3peg:.3f}ms", 
                    font=ctk.CTkFont(size=13), 
                    text_color=C['text_primary'], width=col_widths[4]).grid(row=0, column=4, padx=5)
                
                ctk.CTkLabel(row_inner, text=f"{time_4peg:.3f}ms", 
                    font=ctk.CTkFont(size=13), 
                    text_color=C['text_primary'], width=col_widths[5]).grid(row=0, column=5, padx=5)
                
                time_color = C['success'] if saved_time > 0 else C['error']
                ctk.CTkLabel(row_inner, text=f"{saved_time:.3f}ms ({saved_time_pct:.1f}%)", 
                    font=ctk.CTkFont(size=13, weight="bold"), 
                    text_color=time_color, width=col_widths[6]).grid(row=0, column=6, padx=5)
            
            # Summary
            if len(comparison_data) > 0:
                summary_frame = ctk.CTkFrame(table_container, fg_color=C['accent'], corner_radius=10)
                summary_frame.pack(fill='x', padx=10, pady=(10, 10))
                
                total_moves_3peg = sum(row[1] for row in comparison_data)
                total_moves_4peg = sum(row[2] for row in comparison_data)
                total_saved_moves = total_moves_3peg - total_moves_4peg
                avg_saved_pct = (total_saved_moves / total_moves_3peg * 100) if total_moves_3peg > 0 else 0
                
                summary_text = f"📈 Total: 3-Peg used {total_moves_3peg:,} moves | 4-Peg used {total_moves_4peg:,} moves | Saved {total_saved_moves:,} moves ({avg_saved_pct:.1f}%)"
                
                ctk.CTkLabel(summary_frame, text=summary_text, 
                    font=ctk.CTkFont(size=13, weight="bold"), 
                    text_color=C['text_primary']).pack(pady=12)
        
        self._ctk_btn(main_frame, "← Back to Menu", self._show_menu, C['accent_hover']).pack(pady=25)
    
    def _build_comparison_data(self):
        """Build comparison data from played games"""
        comparison_data = self.db.get_comparison_data()
        
        if comparison_data:
            return comparison_data
        
        all_games = self.db.get_all_played_games_for_comparison()
        
        if not all_games:
            return []
        
        # Group by disks and pegs
        data_3peg = {}
        data_4peg = {}
        
        for disks, pegs, algorithm, moves, time_ms in all_games:
            if pegs == 3:
                if disks not in data_3peg or moves < data_3peg[disks][0]:
                    data_3peg[disks] = (moves, time_ms)
            elif pegs == 4:
                if disks not in data_4peg or moves < data_4peg[disks][0]:
                    data_4peg[disks] = (moves, time_ms)
        
        # Find matching disk counts
        result = []
        common_disks = set(data_3peg.keys()) & set(data_4peg.keys())
        
        for disks in sorted(common_disks):
            moves_3peg, time_3peg = data_3peg[disks]
            moves_4peg, time_4peg = data_4peg[disks]
            result.append((disks, moves_3peg, moves_4peg, time_3peg, time_4peg))
        
        return result

    def _leaderboard(self):
        """Display leaderboard screen"""
        self._clear()
        
        main_frame = ctk.CTkFrame(self.root, fg_color=C['bg_dark'])
        main_frame.pack(fill='both', expand=True)
        
        # Header
        hdr = ctk.CTkFrame(main_frame, fg_color=C['gold'], corner_radius=0, height=80)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🏆 Leaderboard", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), 
            text_color=C['bg_dark']).pack(pady=20)
        
        lb = ctk.CTkFrame(main_frame, fg_color="transparent")
        lb.pack(expand=True, pady=30)
        
        data = self.db.get_leaderboard()
        medals = [C['gold'], C['silver'], C['bronze']]
        
        for i, (player, games, correct_predictions) in enumerate(data):
            frm = ctk.CTkFrame(lb, fg_color=C['card_bg'], corner_radius=15)
            frm.pack(fill='x', pady=8, padx=80)
            
            inner = ctk.CTkFrame(frm, fg_color="transparent")
            inner.pack(fill='x', padx=25, pady=15)
            
            medal_color = medals[i] if i < 3 else C['text_secondary']
            rank = ['🥇', '🥈', '🥉'][i] if i < 3 else f"#{i+1}"
            
            ctk.CTkLabel(inner, text=rank, font=ctk.CTkFont(size=20, weight="bold"), 
                text_color=medal_color).pack(side='left')
            ctk.CTkLabel(inner, text=player, font=ctk.CTkFont(size=16, weight="bold"), 
                text_color=C['text_primary']).pack(side='left', padx=25)
            ctk.CTkLabel(inner, text=f"Games: {games}", font=ctk.CTkFont(size=13), 
                text_color=C['text_secondary']).pack(side='left', padx=15)
            ctk.CTkLabel(inner, text=f"Wins: {correct_predictions}", font=ctk.CTkFont(size=13), 
                text_color=C['success']).pack(side='left', padx=15)
            rate = (correct_predictions/games*100) if games > 0 else 0
            ctk.CTkLabel(inner, text=f"{rate:.0f}%", font=ctk.CTkFont(size=14, weight="bold"), 
                text_color=C['gold']).pack(side='right')
        
        self._ctk_btn(main_frame, "← Back", self._show_menu, C['accent_hover']).pack(pady=25)
    
    def run(self):
        self.root.mainloop()


def start_gui(disks, pegs, player):
    """Standalone game GUI launcher"""
    root = ctk.CTk()
    root.title(f"🎯 Tower of Hanoi - {player}")
    root.attributes('-fullscreen', True)
    root.configure(fg_color=C['bg_dark'])
    root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))
    
    frame = ctk.CTkFrame(root, fg_color=C['bg_dark'])
    frame.pack(expand=True)
    
    db = Database()
    
    def on_win():
        if pegs == 3:
            min_m = len(algorithm.hanoi_recursive_3peg(disks))
        else:
            min_m = len(algorithm.hanoi_frame_stewart(disks))
        db.save_game(player, disks, pegs, game.moves, min_m, True)
        messagebox.showinfo("Win!", f"🎉 Solved in {game.moves} moves!\nMinimum: {min_m}")
    
    def on_move(m):
        lbl.configure(text=f"Moves: {m}")
    
    lbl = ctk.CTkLabel(root, text="Moves: 0", 
        font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), 
        text_color=C['success'])
    lbl.pack()
    
    game = GameUI(frame, disks, pegs, player, on_win, on_move)
    root.mainloop()


def launch_game():
    """Entry point function called from main menu"""
    app = MainApp()
    app.run()
