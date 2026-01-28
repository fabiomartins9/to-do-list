import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class EisenhowerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matriz de Eisenhower - To-Do List")
        self.root.geometry("1000x750") # Aumentei um pouco a altura total

        # --- Configuração do Banco de Dados ---
        self.conn = sqlite3.connect("tarefas.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        self.editing_task_id = None 

        # --- Área de Cadastro (Topo) ---
        # Aumentei o padding vertical para acomodar a caixa maior
        self.frame_input = tk.Frame(self.root, pady=15, padx=10, bg="#f0f0f0")
        self.frame_input.pack(fill="x")

        # Container para o label e a caixa de texto ficarem alinhados
        frame_text_area = tk.Frame(self.frame_input, bg="#f0f0f0")
        frame_text_area.pack(side="left", padx=5)

        tk.Label(frame_text_area, text="Descrição da Tarefa:", bg="#f0f0f0", anchor="w").pack(fill="x")
        
        # MUDANÇA AQUI: Entry -> Text
        self.text_task = tk.Text(frame_text_area, height=3, width=40, wrap="word", font=("Arial", 10))
        self.text_task.pack()

        # Container para os botões e checkboxes ficarem ao lado ou abaixo (dependendo do espaço)
        frame_controls = tk.Frame(self.frame_input, bg="#f0f0f0")
        frame_controls.pack(side="left", padx=20, fill="y")

        self.var_urgent = tk.BooleanVar()
        self.check_urgent = tk.Checkbutton(frame_controls, text="Urgente", variable=self.var_urgent, bg="#f0f0f0")
        self.check_urgent.pack(anchor="w", pady=2)

        self.var_important = tk.BooleanVar()
        self.check_important = tk.Checkbutton(frame_controls, text="Importante", variable=self.var_important, bg="#f0f0f0")
        self.check_important.pack(anchor="w", pady=2)

        self.btn_save = tk.Button(frame_controls, text="Adicionar Tarefa", command=self.save_task, bg="#4CAF50", fg="white", height=2)
        self.btn_save.pack(fill="x", pady=5)
        
        self.btn_cancel = tk.Button(frame_controls, text="Cancelar Edição", command=self.cancel_edit, bg="#FF5722", fg="white")
        
        # --- Área da Matriz (Centro) ---
        self.frame_matrix = tk.Frame(self.root)
        self.frame_matrix.pack(fill="both", expand=True, padx=10, pady=10)

        self.frame_matrix.columnconfigure(0, weight=1)
        self.frame_matrix.columnconfigure(1, weight=1)
        self.frame_matrix.rowconfigure(0, weight=1)
        self.frame_matrix.rowconfigure(1, weight=1)

        self.q1_frame = self.create_quadrant(0, 0, "1. FAÇA AGORA (Urgente & Importante)", "#ffcccc")
        self.q2_frame = self.create_quadrant(0, 1, "2. AGENDE (Não Urgente & Importante)", "#ccffff")
        self.q3_frame = self.create_quadrant(1, 0, "3. DELEGUE (Urgente & Não Importante)", "#ffffcc")
        self.q4_frame = self.create_quadrant(1, 1, "4. ELIMINE (Nem Urgente & Nem Importante)", "#e0e0e0")

        self.refresh_ui()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                urgent INTEGER,
                important INTEGER
            )
        """)
        self.conn.commit()

    def create_quadrant(self, row, col, title, bg_color):
        frame = tk.LabelFrame(self.frame_matrix, text=title, bg=bg_color, font=("Arial", 10, "bold"))
        frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        canvas = tk.Canvas(frame, bg=bg_color)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth()) # Ajuste de largura
        
        # Correção para o scroll funcionar com a roda do mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Resize do frame interno quando o canvas muda de tamanho
        def on_canvas_configure(event):
            canvas.itemconfig(canvas.create_window((0,0), window=scrollable_frame, anchor="nw"), width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        return scrollable_frame

    def save_task(self):
        # MUDANÇA: Pegar texto do widget Text
        # "1.0" = Linha 1, Coluna 0
        # "end-1c" = Final menos 1 char (remove o \n automático)
        title = self.text_task.get("1.0", "end-1c").strip()
        
        if not title:
            messagebox.showwarning("Aviso", "A tarefa precisa de uma descrição!")
            return

        is_urgent = 1 if self.var_urgent.get() else 0
        is_important = 1 if self.var_important.get() else 0

        if self.editing_task_id is not None:
            self.cursor.execute("""
                UPDATE tasks 
                SET title = ?, urgent = ?, important = ? 
                WHERE id = ?
            """, (title, is_urgent, is_important, self.editing_task_id))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Tarefa atualizada!")
            self.cancel_edit()
        else:
            self.cursor.execute("""
                INSERT INTO tasks (title, urgent, important) 
                VALUES (?, ?, ?)
            """, (title, is_urgent, is_important))
            self.conn.commit()

        # MUDANÇA: Limpar widget Text
        self.text_task.delete("1.0", tk.END)
        self.var_urgent.set(False)
        self.var_important.set(False)
        self.refresh_ui()

    def edit_task(self, id, title, urgent, important):
        # MUDANÇA: Inserir no widget Text
        self.text_task.delete("1.0", tk.END)
        self.text_task.insert("1.0", title)
        
        self.var_urgent.set(bool(urgent))
        self.var_important.set(bool(important))
        
        self.editing_task_id = id
        self.btn_save.config(text="Atualizar", bg="#2196F3")
        self.btn_cancel.pack(pady=5, fill="x")

    def cancel_edit(self):
        self.editing_task_id = None
        self.text_task.delete("1.0", tk.END)
        self.var_urgent.set(False)
        self.var_important.set(False)
        self.btn_save.config(text="Adicionar Tarefa", bg="#4CAF50")
        self.btn_cancel.pack_forget()

    def delete_task(self, task_id):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta tarefa?"):
            self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()
            if self.editing_task_id == task_id:
                self.cancel_edit()
            self.refresh_ui()

    def refresh_ui(self):
        for widget in self.q1_frame.winfo_children(): widget.destroy()
        for widget in self.q2_frame.winfo_children(): widget.destroy()
        for widget in self.q3_frame.winfo_children(): widget.destroy()
        for widget in self.q4_frame.winfo_children(): widget.destroy()

        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()

        for row in rows:
            task_id, title, urgent, important = row
            target_frame = None
            if urgent and important: target_frame = self.q1_frame
            elif not urgent and important: target_frame = self.q2_frame
            elif urgent and not important: target_frame = self.q3_frame
            else: target_frame = self.q4_frame

            self.draw_task_card(target_frame, task_id, title, urgent, important)

    def draw_task_card(self, parent, task_id, title, urgent, important):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid")
        card.pack(fill="x", pady=2, padx=2)

        # MUDANÇA: Label agora aceita multiplas linhas (justify left)
        lbl = tk.Label(card, text=title, bg="white", anchor="w", justify="left", wraplength=200)
        lbl.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        frame_btns = tk.Frame(card, bg="white")
        frame_btns.pack(side="right", fill="y")

        btn_edit = tk.Button(frame_btns, text="✎", font=("Arial", 8), 
                             command=lambda: self.edit_task(task_id, title, urgent, important))
        btn_edit.pack(side="top", padx=2, pady=1)

        btn_del = tk.Button(frame_btns, text="✕", font=("Arial", 8), fg="red", 
                            command=lambda: self.delete_task(task_id))
        btn_del.pack(side="bottom", padx=2, pady=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = EisenhowerApp(root)
    root.mainloop()