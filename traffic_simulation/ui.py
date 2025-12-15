# ui.py
import customtkinter as ctk
import tkinter as tk
from .graph import new_random_graph, NODES, EDGES
from .max_flow_algorithms import edmonds_karp, ford_fulkerson
from .database import insert_correct_result, insert_all_result, validate_player_name, init_db, DatabaseError
from .utils import validate_int, time_function
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Predefined node positions for a professional layout
NODE_POS = {
    "A": (120, 220),
    "B": (320, 100),
    "C": (320, 220),
    "D": (320, 340),
    "E": (520, 140),
    "F": (520, 300),
    "G": (720, 140),
    "H": (720, 300),
    "T": (920, 220)
}

class TrafficGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Flow Master - The Ultimate Challenge")
        
        # Set fullscreen mode
        self.root.attributes('-fullscreen', True)
        
        # Allow Escape key to exit fullscreen (optional)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        
        # Initialize database with error handling
        try:
            init_db()
        except DatabaseError as e:
            logger.critical(f"Database initialization failed: {e}")
            raise
        
        # Color theme
        self.bg_dark = "#0a0e27"
        self.card_bg = "#151932"
        self.accent = "#6366f1"
        self.accent_hover = "#4f46e5"
        self.text_primary = "#f8fafc"
        self.text_secondary = "#94a3b8"
        
        # Store player name in memory (persists across rounds)
        self.player_name = None
        
        # Main container
        self.main_container = ctk.CTkFrame(self.root, fg_color=self.bg_dark)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Show welcome page first
        self.show_welcome_page()

    def show_welcome_page(self):
        """Display the welcome/login page"""
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Welcome page frame
        welcome_frame = ctk.CTkFrame(self.main_container, fg_color=self.bg_dark)
        welcome_frame.pack(fill=tk.BOTH, expand=True)
        
        # Close button for username page
        close_btn = ctk.CTkButton(
            welcome_frame,
            text="✕",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20, weight="bold"),
            corner_radius=20,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.root.destroy
        )
        close_btn.place(x=20, y=20)
        
        # Title section
        title_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        title_frame.pack(pady=(80, 40))
        
        # Game title
        title1 = ctk.CTkLabel(
            title_frame,
            text="🚗 TRAFFIC FLOW MASTER 🚗",
            font=ctk.CTkFont(family="Segoe UI", size=48, weight="bold"),
            text_color=self.accent
        )
        title1.pack(pady=(0, 10))
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="The Ultimate Maximum Flow Challenge",
            font=ctk.CTkFont(family="Segoe UI", size=20),
            text_color=self.text_secondary
        )
        subtitle.pack()
        
        # Input section
        input_frame = ctk.CTkFrame(welcome_frame, fg_color=self.card_bg, corner_radius=20, border_width=2, border_color=self.accent)
        input_frame.pack(pady=40, padx=100)
        
        # Welcome message
        welcome_msg = ctk.CTkLabel(
            input_frame,
            text="Enter Your Name to Begin",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.text_primary
        )
        welcome_msg.pack(pady=(40, 30))
        
        # Name entry
        self.welcome_name_entry = ctk.CTkEntry(
            input_frame,
            width=400,
            height=50,
            placeholder_text="Type your player name here...",
            font=ctk.CTkFont(size=16),
            corner_radius=10,
            border_width=2,
            border_color=self.accent
        )
        self.welcome_name_entry.pack(pady=20, padx=40)
        self.welcome_name_entry.bind("<Return>", lambda e: self.start_game())
        
        # Start button
        start_btn = ctk.CTkButton(
            input_frame,
            text="START GAME",
            width=400,
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=10,
            fg_color="#10b981",
            hover_color="#059669",
            command=self.start_game
        )
        start_btn.pack(pady=(10, 40), padx=40)
        
        # Error label
        self.welcome_error_label = ctk.CTkLabel(
            input_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#ef4444"
        )
        self.welcome_error_label.pack(pady=(0, 20))
        
        # Instructions
        instructions_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        instructions_frame.pack(pady=20)
        
        instructions = [
            "🎯 Find the maximum traffic flow from A to T",
            "🧠 Compete against advanced algorithms",
            "💾 Your correct answers will be saved",
            "⏱️ Algorithm times are recorded"
        ]
        
        for instruction in instructions:
            ctk.CTkLabel(
                instructions_frame,
                text=instruction,
                font=ctk.CTkFont(size=14),
                text_color=self.text_secondary
            ).pack(pady=5)

    def start_game(self):
        """Validate name and start the game"""
        name = self.welcome_name_entry.get().strip()
        is_valid, error_msg = validate_player_name(name)
        
        if not is_valid:
            self.welcome_error_label.configure(text=error_msg)
            return
        
        # Store name in memory
        self.player_name = name
        logger.info(f"Player {self.player_name} started the game")
        
        # Show game page
        self.show_game_page()

    def show_game_page(self):
        """Display the main game page"""
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Game page layout
        game_frame = ctk.CTkFrame(self.main_container, fg_color=self.bg_dark)
        game_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top bar - More compact
        top_bar = ctk.CTkFrame(game_frame, height=50, fg_color=self.card_bg, corner_radius=0)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        
        # Player info in top bar
        player_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        player_frame.pack(side=tk.LEFT, padx=15, pady=5)
        
        ctk.CTkLabel(
            player_frame,
            text=f"👤 Player:",
            font=ctk.CTkFont(size=14),
            text_color=self.text_secondary
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ctk.CTkLabel(
            player_frame,
            text=self.player_name,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.accent
        ).pack(side=tk.LEFT)
        
        # Title in top bar
        ctk.CTkLabel(
            top_bar,
            text="🚦 TRAFFIC FLOW CHALLENGE 🚦",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.accent
        ).pack(side=tk.LEFT, expand=True)
        
        # Close button for game page
        close_game_btn = ctk.CTkButton(
            top_bar,
            text="✕",
            width=40,
            height=40,
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=20,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.root.destroy
        )
        close_game_btn.pack(side=tk.RIGHT, padx=10)
        
        # Change player button
        change_btn = ctk.CTkButton(
            top_bar,
            text="Change Player",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=8,
            command=self.show_welcome_page
        )
        change_btn.pack(side=tk.RIGHT, padx=10)
        
        # Main content area
        content_frame = ctk.CTkFrame(game_frame, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas area (left side) - Enhanced
        canvas_frame = ctk.CTkFrame(content_frame, fg_color=self.card_bg, corner_radius=15, border_width=3, border_color=self.accent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))
        
        # Canvas header with styling - More compact
        canvas_header = ctk.CTkFrame(canvas_frame, fg_color=self.bg_dark, corner_radius=10, height=45)
        canvas_header.pack(fill=tk.X, padx=8, pady=5)
        canvas_header.pack_propagate(False)
        
        canvas_title = ctk.CTkLabel(
            canvas_header,
            text="🗺️ TRAFFIC NETWORK MAP",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.accent
        )
        canvas_title.pack(pady=10)
        
        # Legend section
        legend_frame = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        legend_frame.pack(fill=tk.X, padx=10, pady=(0, 3))
        
        legend_items_frame = ctk.CTkFrame(legend_frame, fg_color=self.bg_dark, corner_radius=8)
        legend_items_frame.pack()
        
        ctk.CTkLabel(
            legend_items_frame,
            text="🔵 Nodes  •  🟡 Capacity  •  ➡️ Traffic Flow Direction",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.text_secondary
        ).pack(padx=15, pady=6)
        
        self.canvas = tk.Canvas(canvas_frame, bg=self.bg_dark, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Right side panel
        self.panel = ctk.CTkFrame(content_frame, fg_color=self.card_bg, width=380, corner_radius=15, border_width=2, border_color=self.accent)
        self.panel.pack(fill=tk.Y, side=tk.RIGHT)
        self.panel.pack_propagate(False)
        
        # Panel title
        panel_title = ctk.CTkLabel(
            self.panel,
            text="🎮 GAME CONTROL",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.text_primary
        )
        panel_title.pack(pady=(25, 20))
        
        # Instructions box
        instructions_box = ctk.CTkFrame(self.panel, fg_color=self.bg_dark, corner_radius=10)
        instructions_box.pack(pady=10, padx=20, fill=tk.X)
        
        ctk.CTkLabel(
            instructions_box,
            text="📋 Mission:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#10b981"
        ).pack(pady=(10, 5), anchor="w", padx=15)
        
        ctk.CTkLabel(
            instructions_box,
            text="Calculate the maximum vehicle flow\nfrom source A to destination T",
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary,
            justify="left"
        ).pack(pady=(0, 10), anchor="w", padx=15)
        
        # Guess input section
        guess_frame = ctk.CTkFrame(self.panel, fg_color="transparent")
        guess_frame.pack(pady=20, padx=20, fill=tk.X)
        
        ctk.CTkLabel(
            guess_frame,
            text="Your Answer (A → T):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.text_primary
        ).pack(pady=(0, 10))
        
        self.guess_entry = ctk.CTkEntry(
            guess_frame,
            width=340,
            height=45,
            placeholder_text="Enter maximum flow value...",
            font=ctk.CTkFont(size=16),
            corner_radius=10,
            border_width=2,
            border_color=self.accent
        )
        self.guess_entry.pack()
        self.guess_entry.bind("<Return>", lambda e: self.submit())
        
        # Buttons
        button_frame = ctk.CTkFrame(self.panel, fg_color="transparent")
        button_frame.pack(pady=20, padx=20, fill=tk.X)
        
        self.submit_btn = ctk.CTkButton(
            button_frame,
            text="✓ SUBMIT ANSWER",
            width=340,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10,
            fg_color="#10b981",
            hover_color="#059669",
            command=self.submit
        )
        self.submit_btn.pack(pady=(0, 10))
        
        new_btn = ctk.CTkButton(
            button_frame,
            text="🔄 NEW ROUND",
            width=340,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            fg_color=self.accent,
            hover_color=self.accent_hover,
            command=self.new_round
        )
        new_btn.pack()
        
        # Result display
        result_frame = ctk.CTkFrame(self.panel, fg_color=self.bg_dark, corner_radius=10)
        result_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        self.result_label = ctk.CTkLabel(
            result_frame,
            text="Ready to play! Enter your answer above.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.text_secondary,
            wraplength=320
        )
        self.result_label.pack(pady=20, padx=15)
        
        # Initialize first round
        self.new_round()

    def new_round(self):
        """Generate a new round with exception handling"""
        try:
            # generate graph
            self.nodes, self.edges, self.edge_caps, self.capacity_mat = new_random_graph()
            # Convert to matrix is already returned, but ensure compatible with algorithm helper
            # compute correct flows using both algorithms (matrix + indices)
            source_idx = self.nodes.index("A")
            sink_idx = self.nodes.index("T")

            self.correct_answer, ek_time = time_function(edmonds_karp, self.capacity_mat, source_idx, sink_idx)
            # Ford-Fulkerson may modify internal residual; compute on fresh copy
            import copy
            mat_copy = [row[:] for row in self.capacity_mat]
            # Use pure ford_fulkerson
            ff_result, ff_time = time_function(ford_fulkerson, mat_copy, source_idx, sink_idx)

            if ff_result != self.correct_answer:
                logger.warning("Warning: Algorithms mismatch!")
                print("Warning: Algorithms mismatch!")
            # store
            self.ek_time = ek_time
            self.ff_time = ff_time
            # For safety we pick the smaller or confirm they match; prefer ek result
            # (in correct implementations they must match)
            self.correct_answer = int(self.correct_answer)  # ensure int

            self.result_label.configure(text="🎯 New round generated!\nCalculate the maximum flow from A → T", text_color=self.text_secondary)

            self.draw_graph()
            
            # Clear input field for new round
            self.guess_entry.delete(0, tk.END)
            
        except Exception as e:
            logger.error(f"Error generating new round: {e}")
            self.result_label.configure(text=f"❌ Error: Failed to generate new round.\nPlease try again.", text_color="#ef4444")

    def draw_graph(self):
        self.canvas.delete("all")

        # draw edges (with arrows simulated) - Enhanced
        for (u,v) in self.edges:
            x1,y1 = NODE_POS[u]
            x2,y2 = NODE_POS[v]
            
            # Shadow/glow effect for road
            self.canvas.create_line(x1, y1, x2, y2, width=10, fill="#1e293b", smooth=True)
            # Main road line - thicker and brighter
            self.canvas.create_line(x1, y1, x2, y2, width=6, fill=self.accent, smooth=True)
            
            # draw a larger arrow head
            ax = x1 + 0.85*(x2-x1)
            ay = y1 + 0.85*(y2-y1)
            dx = x2-x1
            dy = y2-y1
            # normalized perpendicular
            perp_x = -dy
            perp_y = dx
            length = (perp_x*perp_x + perp_y*perp_y)**0.5
            if length != 0:
                perp_x /= length
                perp_y /= length
            s = 10  # Increased arrow size
            self.canvas.create_polygon(
                ax, ay,
                ax - dx*0.04 + perp_x*s, ay - dy*0.04 + perp_y*s,
                ax - dx*0.04 - perp_x*s, ay - dy*0.04 - perp_y*s,
                fill="#fbbf24", outline=""
            )

            # capacity display with background badge
            midx = (x1 + x2) / 2
            midy = (y1 + y2) / 2
            cap = self.edge_caps.get((u,v), 0)
            
            # Background badge for capacity - Smaller
            self.canvas.create_oval(
                midx-20, midy-20, midx+20, midy+20,
                fill="#1e293b", outline="#fbbf24", width=2
            )
            # Capacity number
            self.canvas.create_text(
                midx, midy, 
                text=str(cap), 
                fill="#fbbf24", 
                font=("Helvetica", 18, "bold")
            )

        # draw nodes - Enhanced with larger size
        for n in self.nodes:
            x,y = NODE_POS[n]
            
            # Special styling for source (A) and sink (T)
            if n == "A":
                node_color = "#10b981"  # Green for source
                outer_color = "#10b981"
                label_color = "#ffffff"
            elif n == "T":
                node_color = "#ef4444"  # Red for sink
                outer_color = "#ef4444"
                label_color = "#ffffff"
            else:
                node_color = self.accent
                outer_color = self.accent
                label_color = self.text_primary
            
            # Shadow effect
            self.canvas.create_oval(x-38, y-38, x+38, y+38, fill="#0f172a", outline="")
            # Outer ring - larger
            self.canvas.create_oval(x-35, y-35, x+35, y+35, fill=self.card_bg, outline=outer_color, width=4)
            # Inner circle - larger
            self.canvas.create_oval(x-26, y-26, x+26, y+26, fill=node_color, outline="")
            # Node label - larger
            self.canvas.create_text(x, y, text=n, fill=label_color, font=("Helvetica", 16, "bold"))

    def submit(self):
        """Handle answer submission with comprehensive validation and exception handling"""
        try:
            # Use stored player name
            name = self.player_name
            
            # Validate guess
            guess_text = self.guess_entry.get().strip()
            if not guess_text:
                self.result_label.configure(text="⚠️ Please enter your guess.", text_color="#f59e0b")
                return
                
            ok, val = validate_int(guess_text)
            if not ok:
                self.result_label.configure(text="❌ Enter a valid integer guess.", text_color="#ef4444")
                return
            
            guess = int(val)
            
            # Additional validation for guess value
            if guess < 0:
                self.result_label.configure(text="❌ Guess must be non-negative.", text_color="#ef4444")
                return
            
            if guess > 10000:  # Reasonable upper limit
                self.result_label.configure(text="❌ Guess seems unreasonably large.", text_color="#ef4444")
                return

            # Check if answer is correct
            if guess == self.correct_answer:
                # Save ONLY correct answers to win_results table
                try:
                    success, message = insert_correct_result(
                        name, 
                        guess,
                        self.correct_answer, 
                        self.ek_time, 
                        self.ff_time
                    )
                    
                    # Save ALL results (pass and fail) to all_game_results table
                    insert_all_result(
                        name,
                        guess,
                        self.correct_answer,
                        self.ek_time,
                        self.ff_time
                    )
                    
                    if success:
                        logger.info(f"Saved correct answer for {name}: {self.correct_answer}")
                        self.result_label.configure(
                            text=f"🎉 CORRECT!\n{name}, your answer ({self.correct_answer}) is saved!\n\n✨ Starting new round...", 
                            text_color="#10b981"
                        )
                    else:
                        logger.warning(f"Failed to save result: {message}")
                        self.result_label.configure(
                            text=f"✓ Correct!\nBut save failed: {message}.\n\nStarting new round...", 
                            text_color="#f59e0b"
                        )
                    
                    # Auto-start new round after a short delay
                    self.root.after(2500, self.new_round)  # 2.5 second delay
                        
                except Exception as e:
                    logger.error(f"Exception while saving correct result: {e}")
                    self.result_label.configure(
                        text=f"✓ Correct!\nBut error saving: {str(e)[:30]}...\n\nStarting new round...", 
                        text_color="#f59e0b"
                    )
                    # Auto-start new round after a short delay
                    self.root.after(2500, self.new_round)  # 2.5 second delay
                    
            elif guess < self.correct_answer:
                # Save ALL results (pass and fail) to all_game_results table
                insert_all_result(
                    name,
                    guess,
                    self.correct_answer,
                    self.ek_time,
                    self.ff_time
                )
                
                self.result_label.configure(
                    text=f"📉 Too Low!\nYour guess: {guess}\nCorrect answer: {self.correct_answer}\n\n🔄 Starting new round...", 
                    text_color="#f59e0b"
                )
                # Auto-start new round after a short delay
                self.root.after(2500, self.new_round)  # 2.5 second delay
            else:
                # Save ALL results (pass and fail) to all_game_results table
                insert_all_result(
                    name,
                    guess,
                    self.correct_answer,
                    self.ek_time,
                    self.ff_time
                )
                
                self.result_label.configure(
                    text=f"📈 Too High!\nYour guess: {guess}\nCorrect answer: {self.correct_answer}\n\n🔄 Starting new round...", 
                    text_color="#ef4444"
                )
                # Auto-start new round after a short delay
                self.root.after(2500, self.new_round)  # 2.5 second delay
                
        except ValueError as e:
            logger.error(f"Value error in submit: {e}")
            self.result_label.configure(text=f"❌ Invalid input values:\n{str(e)[:30]}...", text_color="#ef4444")
        except Exception as e:
            logger.error(f"Unexpected error in submit: {e}")
            self.result_label.configure(text=f"❌ Error occurred:\n{str(e)[:40]}...", text_color="#ef4444")


def launch_game():
    root = ctk.CTk()
    app = TrafficGameUI(root)
    root.mainloop()
