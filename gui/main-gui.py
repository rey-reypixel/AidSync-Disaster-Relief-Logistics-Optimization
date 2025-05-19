import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Disaster Relief Logistics Optimization")
root.geometry("1024x768")

# Left Side: Input Form
form_frame = tk.Frame(root)
form_frame.place(x=20, y=60)

tk.Label(form_frame, text="Area Name:").grid(row=0, column=0, sticky='w')
area_entry = tk.Entry(form_frame, width=30)
area_entry.grid(row=0, column=1, pady=5)

tk.Label(form_frame, text="Urgency Level (1-5):").grid(row=1, column=0, sticky='w')
urgency_entry = tk.Entry(form_frame, width=30)
urgency_entry.grid(row=1, column=1, pady=5)

tk.Label(form_frame, text="Supply Stock Needed:").grid(row=2, column=0, sticky='w')
stock_entry = tk.Entry(form_frame, width=30)
stock_entry.grid(row=2, column=1, pady=5)

# Run Optimization Button
def run_optimization():
    area = area_entry.get()
    urgency = urgency_entry.get()
    stock = stock_entry.get()
    result_text.insert(tk.END, f"Route optimized for {area} with urgency {urgency}\n")

run_button = tk.Button(root, text="Run Optimization", width=20, command=run_optimization)
run_button.place(x=100, y=230)

# Right Side: Grid Canvas
canvas = tk.Canvas(root, width=480, height=400, bg='white')
canvas.place(x=500, y=60)

# Draw grid (10x8 cells)
cell_size = 48
for i in range(0, 480, cell_size):
    canvas.create_line([(i, 0), (i, 400)], fill='gray')
for j in range(0, 400, cell_size):
    canvas.create_line([(0, j), (480, j)], fill='gray')

# Simulate a route with a red line
canvas.create_line(24, 24, 120, 72, 240, 120, fill="red", width=3, smooth=True)

# Bottom: Result Display
result_text = tk.Text(root, height=8, width=120)
result_text.place(x=40, y=500)
result_text.insert(tk.END, "Optimization Results:\n")

# Start the GUI loop
root.mainloop()
