import customtkinter as ctk
import math
import random
import time
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .game import Game
from .data import init_database, create_round, save_algorithm_times, save_player_win

def spring_layout(cities: list[str], distance_matrix: list[list[int]], iterations: int = 100) -> dict[str, tuple[float, float]]:
	n = len(cities)
	
	all_distances = []
	for i in range(n):
		for j in range(i + 1, n):
			all_distances.append(distance_matrix[i][j])
	min_dist = min(all_distances) if all_distances else 50
	max_dist = max(all_distances) if all_distances else 100
	
	canvas_range = 0.8
	scale = canvas_range / max_dist if max_dist > 0 else 0.01
	
	# Initialize positions randomly or in a circle
	positions = {}
	center_x, center_y = 0.5, 0.5
	for i, city in enumerate(cities):
		# Start with circular layout as initial guess
		angle = 2 * math.pi * i / n - math.pi / 2
		radius_init = 0.3
		positions[city] = (
			center_x + radius_init * math.cos(angle) + random.uniform(-0.1, 0.1),
			center_y + radius_init * math.sin(angle) + random.uniform(-0.1, 0.1)
		)
	
	# Spring layout iterations
	dt = 0.1  # Time step
	damping = 0.8  # Damping factor
	
	for iteration in range(iterations):
		forces = {city: [0.0, 0.0] for city in cities}
		
		for i in range(n):
			for j in range(i + 1, n):
				city1 = cities[i]
				city2 = cities[j]
				
				x1, y1 = positions[city1]
				x2, y2 = positions[city2]
				
				# Current distance between nodes
				dx = x2 - x1
				dy = y2 - y1
				current_dist = math.sqrt(dx*dx + dy*dy) if (dx*dx + dy*dy) > 0 else 0.001
				
				# Desired distance (normalized from distance matrix)
				desired_dist = distance_matrix[i][j] * scale
				
				# Spring force (proportional to difference)
				force_magnitude = (current_dist - desired_dist) * 0.1
				
				# Direction vector
				force_x = (dx / current_dist) * force_magnitude
				force_y = (dy / current_dist) * force_magnitude
				
				# Apply forces (opposite directions)
				forces[city1][0] += force_x
				forces[city1][1] += force_y
				forces[city2][0] -= force_x
				forces[city2][1] -= force_y
		
		# Update positions based on forces
		for city in cities:
			fx, fy = forces[city]
			x, y = positions[city]
			
			# Update with damping
			x += fx * dt * damping
			y += fy * dt * damping
			
			# Keep within bounds
			x = max(0.1, min(0.9, x))
			y = max(0.1, min(0.9, y))
			
			positions[city] = (x, y)
	
	return positions

def draw_graph(ax, cities: list[str], distance_matrix: list[list[int]], main_city: str, 
			   bg_color: str, card_bg: str, accent: str, accent_hover: str, 
			   text_color: str, text_secondary: str) -> None:
	n = len(cities)
	
	# Calculate node positions using spring layout (edge lengths based on distances)
	node_positions = spring_layout(cities, distance_matrix, iterations=150)
	
	# Uniform edge thickness (not based on distance)
	edge_linewidth = 1.5
	
	# Draw edges (connections between all cities)
	for i in range(n):
		for j in range(i + 1, n):
			city1 = cities[i]
			city2 = cities[j]
			x1, y1 = node_positions[city1]
			x2, y2 = node_positions[city2]
			distance = distance_matrix[i][j]
			
			ax.plot([x1, x2], [y1, y2], 'o-', color=text_secondary, linewidth=edge_linewidth, 
				   markersize=0, alpha=0.5, zorder=1)
			
			# Draw distance label at midpoint
			mid_x = (x1 + x2) / 2
			mid_y = (y1 + y2) / 2
			ax.text(mid_x, mid_y, str(distance), fontsize=10, 
				   ha='center', va='center', 
				   bbox=dict(boxstyle='round,pad=0.4', facecolor=card_bg,
							edgecolor=text_secondary, alpha=0.9, linewidth=1),
				   color=text_color, zorder=3)
	
	# Draw nodes
	for city in cities:
		x, y = node_positions[city]
		
		if city == main_city:
			node_color = accent
			edge_color = accent_hover
			edge_width = 3
		else:
			node_color = text_secondary
			edge_color = card_bg
			edge_width = 2
		
		circle = plt.Circle((x, y), 0.045, color=node_color, 
						   edgecolor=edge_color, linewidth=edge_width, zorder=4)
		ax.add_patch(circle)
		
		# Draw city label inside the node
		ax.text(x, y, city, fontsize=14, fontweight='bold',
			   ha='center', va='center', color=text_color, zorder=5)
	
	# Set axis properties
	ax.set_xlim(0, 1)
	ax.set_ylim(0, 1)
	ax.set_aspect('equal')
	ax.axis('off')
	ax.set_title('City Graph with Distances', fontsize=14, color=text_color, pad=10)

def get_player_name() -> Optional[str]:
	"""
	Show a popup to get the player's name before starting the game.
	Returns the player name or None if cancelled.
	"""
	# Create a temporary root window for the popup
	temp_root = ctk.CTk()
	temp_root.withdraw()  # Hide the root window
	
	popup = ctk.CTkToplevel(temp_root)
	popup.title("Enter Player Name")
	popup.geometry("400x200")
	popup.configure(fg_color="#0a0e27")
	popup.resizable(False, False)
	popup.grab_set()  # Make it modal
	
	# Center the popup
	popup.update_idletasks()
	x = (popup.winfo_screenwidth() // 2) - (400 // 2)
	y = (popup.winfo_screenheight() // 2) - (200 // 2)
	popup.geometry(f"400x200+{x}+{y}")
	
	player_name = [None]  # Use list to allow modification in nested function
	
	def on_submit():
		name = name_entry.get().strip()
		if name:
			player_name[0] = name
		popup.destroy()
	
	def on_cancel():
		popup.destroy()
	
	ctk.CTkLabel(
		popup, 
		text="Enter your name:", 
		font=("SF Pro Display", 16)
	).pack(pady=(30, 10))
	
	name_entry = ctk.CTkEntry(popup, width=300, font=("SF Pro Display", 14))
	name_entry.pack(pady=10)
	name_entry.focus()
	
	button_frame = ctk.CTkFrame(popup, fg_color="transparent")
	button_frame.pack(pady=20)
	
	ctk.CTkButton(button_frame, text="Start", command=on_submit, width=120).pack(side="left", padx=10)
	ctk.CTkButton(button_frame, text="Cancel", command=on_cancel, width=120).pack(side="left", padx=10)
	
	# Handle Enter key
	name_entry.bind("<Return>", lambda e: on_submit())
	
	# Wait for the popup to be destroyed
	popup.wait_window()
	
	# Safely destroy temp_root if it still exists
	try:
		if temp_root.winfo_exists():
			temp_root.quit()
			temp_root.destroy()
	except Exception:
		pass  # Window already destroyed or error occurred
	
	return player_name[0]


def draw_ui(game: Game) -> None:
	# Initialize database
	init_database()
	
	# Get player name before starting
	player_name = get_player_name()
	if not player_name:
		# User cancelled, exit
		return
	
	window = ctk.CTk()
	window.title("Traveling Salesman Problem")
	window.geometry("1280x720")

	bg_dark = "#0a0e27"
	card_bg = "#151932"
	accent = "#6366f1"
	accent_hover = "#4f46e5"
	text_primary = "#f8fafc"
	text_secondary = "#94a3b8"

	window.configure(fg_color=bg_dark)
	
	# Track current round ID for database
	current_round_id = [None]

	# --- Main layout split (Left + Right) ---
	main_frame = ctk.CTkFrame(window, fg_color="transparent")
	main_frame.pack(fill="both", expand=True, padx=20, pady=20)

	# Right side (game interaction)
	right_frame = ctk.CTkFrame(main_frame, width=350, fg_color="transparent")
	right_frame.pack(side="right", fill="y", expand=False, padx=10)

	# Left side (Graph only)
	left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
	left_frame.pack(side="left", fill="both", expand=True, padx=10)

	graph_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
	graph_frame.pack(fill="both", expand=True)
	
	# Create matplotlib figure for graph visualization
	fig = Figure(figsize=(12, 7), facecolor=card_bg)
	ax = fig.add_subplot(111, facecolor=card_bg)
	ax.set_facecolor(card_bg)
	
	# Draw the graph
	draw_graph(ax, game.cities, game.distance_matrix, game.main_city, 
			   bg_dark, card_bg, accent, accent_hover, text_primary, text_secondary)
	
	# Embed matplotlib figure in customtkinter
	canvas = FigureCanvasTkAgg(fig, graph_frame)
	canvas.draw()
	canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

	title = ctk.CTkLabel(right_frame, text="Traveling Salesman", font=("SF Pro Display", 20))
	title.pack(pady=20)

	main_city_label = ctk.CTkLabel(right_frame, text=f"Main city: {game.main_city}", font=("SF Pro Display", 16))
	main_city_label.pack(pady=10)

	select_label = ctk.CTkLabel(right_frame, text="Select cities", font=("SF Pro Display", 16))
	select_label.pack(pady=10)

	# list of cities
	city_frame = ctk.CTkFrame(right_frame, fg_color=card_bg)
	city_frame.pack(pady=5)

	row1 = ctk.CTkFrame(city_frame, fg_color="transparent")
	row1.pack(pady=(10, 5))
	row2 = ctk.CTkFrame(city_frame, fg_color="transparent")
	row2.pack(pady=(5, 10))

	cities = "ABCDEFGHIJ"
	
	# Store checkbox references
	checkbox_dict = {}

	for c in cities[:5]:
		# Disable and style the main city checkbox
		if c == game.main_city:
			btn = ctk.CTkCheckBox(row1, text=c, state="disabled")
			# Visual cue: grayed out text and checkbox
			btn.configure(text_color=text_secondary, fg_color=card_bg, 
						 hover_color=card_bg, checkmark_color=text_secondary)
		else:
			btn = ctk.CTkCheckBox(row1, text=c)
		btn.pack(side="left", padx=3)
		checkbox_dict[c] = btn

	for c in cities[5:]:
		# Disable and style the main city checkbox
		if c == game.main_city:
			btn = ctk.CTkCheckBox(row2, text=c, state="disabled")
			# Visual cue: grayed out text and checkbox
			btn.configure(text_color=text_secondary, fg_color=card_bg, 
						 hover_color=card_bg, checkmark_color=text_secondary)
		else:
			btn = ctk.CTkCheckBox(row2, text=c)
		btn.pack(side="left", padx=3)
		checkbox_dict[c] = btn

	guess_label = ctk.CTkLabel(right_frame, text="Guess path", font=("SF Pro Display", 16))
	guess_label.pack(pady=(20, 5))

	guess_entry = ctk.CTkEntry(right_frame, width=200)
	guess_entry.pack(pady=5)

	# Algorithm logs frame
	logs_frame = ctk.CTkFrame(right_frame, fg_color=card_bg)
	logs_frame.pack(fill="both", expand=True, pady=(10, 0))
	
	# Logs title
	ctk.CTkLabel(logs_frame, text="Algorithm running logs", font=("SF Pro Display", 16)).pack(pady=(10, 5))
	
	# Scrollable text area for logs
	logs_text = ctk.CTkTextbox(logs_frame, width=320, height=150, 
							  fg_color=bg_dark, text_color=text_primary,
							  font=("Consolas", 11), wrap="word")
	logs_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
	
	status_green = "#10b981"

	def show_validation_error():
		popup = ctk.CTkToplevel(window)
		popup.title("Validation Error")
		popup.geometry("300x150")
		popup.configure(fg_color=bg_dark)

		ctk.CTkLabel(
			popup, 
			text="Minimum cities 2 and maximum cities 7", 
			font=("SF Pro Display", 16)
		).pack(pady=30)
		ctk.CTkButton(popup, text="OK", command=popup.destroy).pack(pady=10)

	def on_check_button_click():
		# Collect all selected cities from checkboxes
		selected_cities = []
		for city, checkbox in checkbox_dict.items():
			if checkbox.get():  # get() returns True if checkbox is checked
				selected_cities.append(city)
		
		# Remove main city if somehow included (shouldn't happen but safety check)
		selected_cities = [city for city in selected_cities if city != game.main_city]
		
		# Validate: minimum 2, maximum 7 cities
		if len(selected_cities) < 2 or len(selected_cities) > 7:
			show_validation_error()
			return
		
		# Update player_selected_cities in game object
		game.player_selected_cities = selected_cities
		
		# Get player guess from entry field
		guess_text = guess_entry.get().strip()
		if not guess_text:
			show_validation_error()
			return
		
		# Parse player guess (assuming space-separated cities)
		player_guess = guess_text.split()
		
		# Create a new round in the database
		try:
			round_id = create_round(player_name, game.main_city)
			current_round_id[0] = round_id
		except Exception as e:
			# If database save fails, continue anyway (don't block gameplay)
			print(f"Warning: Failed to create round in database: {e}")
		
		# Clear previous logs
		logs_text.delete("1.0", "end")
		
		# Function to add log message
		tag_counter = [0]
		def add_log(message: str, color: str = text_primary):
			# Get position before inserting
			start_index = logs_text.index("end")
			logs_text.insert("end", message + "\n")
			# Get position after inserting (before the newline)
			end_index = logs_text.index("end-1c")
			
			# Apply color tag if not default color
			if color != text_primary:
				tag_counter[0] += 1
				tag_name = f"colored_{tag_counter[0]}"
				# Apply tag to the inserted text
				logs_text.tag_add(tag_name, start_index, end_index)
				logs_text.tag_config(tag_name, foreground=color)
			logs_text.see("end")
			window.update()
		
		# Track algorithm execution with timing
		add_log("Starting algorithms...", text_secondary)
		total_start = time.time()
		
		# Log each algorithm start
		add_log("▶ Brute Force: Starting...", status_green)
		add_log("▶ Held-Karp DP: Starting...", status_green)
		add_log("▶ Nearest Neighbor 2-Opt: Starting...", status_green)
		window.update()
		
		# Run algorithms with multiprocessing and compare results
		is_won, best_path = game.run_algorithms(player_guess)
		
		# Get timing information from game object
		total_time = time.time() - total_start
		
		# Log completion with individual times
		if hasattr(game, 'algorithm_times') and game.algorithm_times:
			bf_time = game.algorithm_times.get("Brute Force", 0.0)
			hk_time = game.algorithm_times.get("Held-Karp", 0.0)
			nn_time = game.algorithm_times.get("Nearest Neighbor 2-Opt", 0.0)
			
			# Format time display - use appropriate precision for small values
			def format_time(t: float) -> str:
				if t >= 0.001:
					return f"{t:.4f}s"
				elif t >= 0.0001:
					return f"{t:.6f}s"
				else:
					# For very small times (microseconds), show 8 decimal places
					return f"{t:.8f}s"
			
			# Display times with appropriate precision
			add_log(f"✓ Brute Force: Finished in {format_time(bf_time)}", status_green)
			add_log(f"✓ Held-Karp DP: Finished in {format_time(hk_time)}", status_green)
			add_log(f"✓ Nearest Neighbor 2-Opt: Finished in {format_time(nn_time)}", status_green)
		else:
			add_log("✓ All algorithms finished", status_green)
		
		add_log(f"\nTotal execution time: {total_time:.3f}s", text_secondary)
		
		# Save algorithm times to database
		if current_round_id[0] and hasattr(game, 'algorithm_times') and game.algorithm_times:
			try:
				save_algorithm_times(current_round_id[0], game.algorithm_times)
			except Exception as e:
				# If database save fails, continue anyway
				print(f"Warning: Failed to save algorithm times: {e}")
		
		# Save player win if they won
		if is_won and current_round_id[0]:
			try:
				save_player_win(
					current_round_id[0],
					player_name,
					game.main_city,
					game.player_selected_cities,
					best_path
				)
			except Exception as e:
				# If database save fails, continue anyway
				print(f"Warning: Failed to save player win: {e}")
		
		# Function to refresh the game for a new round
		def refresh_game():
			# Reset the game (new distance matrix and main city)
			old_main_city = game.main_city
			game.reset_game()
			
			# Reset round ID for next round
			current_round_id[0] = None
			
			# Clear guess entry
			guess_entry.delete(0, "end")
			
			# Clear logs
			logs_text.delete("1.0", "end")
			
			# Uncheck all checkboxes
			for checkbox in checkbox_dict.values():
				checkbox.deselect()
			
			# Update main city label
			main_city_label.configure(text=f"Main city: {game.main_city}")
			
			# Enable old main city, disable new main city
			if old_main_city in checkbox_dict:
				old_checkbox = checkbox_dict[old_main_city]
				old_checkbox.configure(state="normal")
				old_checkbox.configure(
					text_color=text_primary,
					fg_color=accent,
					hover_color=accent_hover,
					checkmark_color=text_primary
				)
			
			if game.main_city in checkbox_dict:
				new_checkbox = checkbox_dict[game.main_city]
				new_checkbox.configure(state="disabled", text_color=text_secondary, 
									  fg_color=card_bg, hover_color=card_bg, 
									  checkmark_color=text_secondary)
			
			# Clear and redraw the graph
			ax.clear()
			ax.set_facecolor(card_bg)
			draw_graph(ax, game.cities, game.distance_matrix, game.main_city, 
					   bg_dark, card_bg, accent, accent_hover, text_primary, text_secondary)
			canvas.draw()
		
		# Show result popup with refresh callback
		if is_won:
			show_win(refresh_game)
		else:
			show_lose(" -> ".join(best_path), refresh_game)

	check_button = ctk.CTkButton(right_frame, text="Check", command=on_check_button_click)
	check_button.pack(pady=20)

	window.mainloop()

def show_win(refresh_callback) -> None:
	popup = ctk.CTkToplevel()
	popup.title("Result")
	popup.geometry("250x150")
	popup.configure(fg_color="#0a0e27")

	def on_ok():
		refresh_callback()
		popup.destroy()

	ctk.CTkLabel(popup, text="You won!", font=("SF Pro Display", 18)).pack(pady=20)
	ctk.CTkButton(popup, text="OK", command=on_ok).pack(pady=10)

def show_lose(correct_path: str, refresh_callback) -> None:
	popup = ctk.CTkToplevel()
	popup.title("Result")
	popup.geometry("300x180")
	popup.configure(fg_color="#0a0e27")

	def on_ok():
		refresh_callback()
		popup.destroy()

	ctk.CTkLabel(popup, text="You lose!", font=("SF Pro Display", 18)).pack(pady=20)
	ctk.CTkLabel(popup, text=f"Correct Path:\n{correct_path}", font=("Arial", 14)).pack(pady=10)
	ctk.CTkButton(popup, text="OK", command=on_ok).pack(pady=10)
