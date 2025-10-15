import tkinter as tk
from tkinter import ttk
import random

class RainDrop:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height

        self.depth = random.uniform(0.2, 1.0)

        self.size = max(2, int(10 * (1 - self.depth * 0.8)))
        self.speed = max(1, int(8 * (1 - self.depth * 0.5)))

        self.x = random.randint(0, width)
        self.y = random.randint(-100, 0)

        color_intensity = int(150 + 100 * (1 - self.depth))
        self.color = f'#{color_intensity:02x}00{color_intensity:02x}'

        self.id = canvas.create_oval(
            self.x, self.y,
            self.x + self.size,
            self.y + self.size * 1.5,
            fill=self.color, outline=""
        )

    def move(self):
        self.y += self.speed
        self.canvas.move(self.id, 0, self.speed)

        if self.y > self.height:
            self.reset()

    def reset(self):
        self.y = random.randint(-100, -20)
        self.x = random.randint(0, self.width)
        self.canvas.coords(
            self.id,
            self.x, self.y,
            self.x + self.size,
            self.y + self.size * 1.5
        )

class RainAnimation:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Капли с регулируемой плотностью")

       
        self.width = 800
        self.height = 600

        self.drop_density = 100

        self.canvas = tk.Canvas(
            root,
            width=self.width,
            height=self.height,
            bg='black'
        )
        self.canvas.pack()

        self.create_density_slider()

        self.drops = []
        self.create_drops()

        self.animate()

    def create_density_slider(self):
        slider_frame = tk.Frame(self.root)
        slider_frame.pack(pady=10)

        tk.Label(slider_frame, text="Плотность капель:").pack(side=tk.LEFT)

        self.density_var = tk.IntVar(value=self.drop_density)
        self.density_slider = ttk.Scale(
            slider_frame,
            from_=20,
            to=800,
            orient=tk.HORIZONTAL,
            variable=self.density_var,
            command=self.on_density_change,
            length=300
        )
        self.density_slider.pack(side=tk.LEFT, padx=10)

        self.density_label = tk.Label(slider_frame, text=str(self.drop_density))
        self.density_label.pack(side=tk.LEFT)

    def on_density_change(self, event=None):
        """Обработчик изменения ползунка плотности"""
        new_density = int(self.density_var.get())
        self.density_label.config(text=str(new_density))

        self.drop_density = new_density

    def create_drops(self):
        for _ in range(self.drop_density):
            self.drops.append(RainDrop(self.canvas, self.width, self.height))

    def update_drops_count(self):
        current_count = len(self.drops)

        if current_count < self.drop_density:
            for _ in range(self.drop_density - current_count):
                self.drops.append(RainDrop(self.canvas, self.width, self.height))

        elif current_count > self.drop_density:
            for _ in range(current_count - self.drop_density):
                if self.drops:  
                    drop = self.drops.pop()  
                    self.canvas.delete(drop.id)  

    def animate(self):
        self.update_drops_count()

        for drop in self.drops:
            drop.move()

        self.root.after(16, self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    app = RainAnimation(root)
    root.mainloop()
