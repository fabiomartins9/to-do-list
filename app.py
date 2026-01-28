import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class EisenhowerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matriz de Eisenhower - To-Do List (Banco de Dados)")
        self.root.geometry("1000x700")

        # --- Configuração do Banco de Dados ---
        self.conn = sqlite3.connect("tarefas.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        self.editing_task_id = None 

        # --- Área de Cadastro (Topo) ---
        self.frame_input = tk.Frame(self.root, pady=10, padx=10, bg="#f0f0f0")
        self.frame_input.pack(fill="x")

        tk.Label(self.frame_input, text="Tarefa:", bg="#f0f0f0").pack(side="left")
        self.entry_task = tk.Entry(self.frame_input, width=30)
        self.entry_task.pack(side="left", padx=5)

        self.var_urgent = tk.BooleanVar()
        self.check_urgent = tk.Checkbutton(self.frame_input, text="Urgente", variable=self.var_urgent, bg="#f0f0f0")
        self.check_urgent.pack(side="left", padx=5)

        self.var_important = tk.BooleanVar()
        self.check_important = tk.Checkbutton(self.frame_input, text="Importante", variable=self.var_important, bg="#f0f0f0")
        self.check_important.pack(side="left", padx=5)

        self.btn_save = tk.Button(self.frame_input, text="Adicionar Tarefa", command=self.save_task, bg="#4CAF50", fg="white")
        self.btn_save.pack(side="left", padx=10)
        
        self.btn_cancel = tk.Button(self.frame_input, text="Cancelar Edição", command=self.cancel_edit, bg="#FF5722", fg="white")
        
        # --- Área da Matriz (Centro) ---
        self.frame_matrix = tk.Frame(self.root)
        self.frame_matrix.pack(fill="both", expand=True, padx=10, pady=10)

        self.frame_matrix.columnconfigure(0, weight=1)
        self.frame_matrix.columnconfigure(1, weight=1)
        self.frame_matrix.rowconfigure(0, weight=1)
        self.frame_matrix.rowconfigure(1, weight=1)

        # Criação dos 4 Quadrantes
        self.q1_frame = self.create_quadrant(0, 0, "1. FAÇA AGORA (Urgente & Importante)", "#ffcccc")
        self.q2_frame = self.create_quadrant(0, 1, "2. AGENDE (Não Urgente & Importante)", "#ccffff")
        self.q3_frame = self.create_quadrant(1, 0, "3. DELEGUE (Urgente & Não Importante)", "#ffffcc")
        self.q4_frame = self.create_quadrant(1, 1, "4. ELIMINE (Nem Urgente & Nem Importante)", "#e0e0e0")

        # Carregar tarefas do banco ao iniciar
        self.refresh_ui()

    def create_table(self):
        """Cria a tabela se ela não existir"""
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

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return scrollable_frame

    def save_task(self):
        title = self.entry_task.get()
        if not title:
            messagebox.showwarning("Aviso", "A tarefa precisa de um nome!")
            return

        # Converter Booleanos para Inteiros (0 ou 1) para o SQLite
        is_urgent = 1 if self.var_urgent.get() else 0
        is_important = 1 if self.var_important.get() else 0

        if self.editing_task_id is not None:
            # UPDATE no Banco
            self.cursor.execute("""
                UPDATE tasks 
                SET title = ?, urgent = ?, important = ? 
                WHERE id = ?
            """, (title, is_urgent, is_important, self.editing_task_id))
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Tarefa atualizada!")
            self.cancel_edit()
        else:
            # INSERT no Banco
            self.cursor.execute("""
                INSERT INTO tasks (title, urgent, important) 
                VALUES (?, ?, ?)
            """, (title, is_urgent, is_important))
            self.conn.commit()

        self.entry_task.delete(0, tk.END)
        self.var_urgent.set(False)
        self.var_important.set(False)
        self.refresh_ui()

    def edit_task(self, id, title, urgent, important):
        """Carrega os dados para edição"""
        self.entry_task.delete(0, tk.END)
        self.entry_task.insert(0, title)
        self.var_urgent.set(bool(urgent))
        self.var_important.set(bool(important))
        
        self.editing_task_id = id
        self.btn_save.config(text="Atualizar Tarefa", bg="#2196F3")
        self.btn_cancel.pack(side="left", padx=5)

    def cancel_edit(self):
        self.editing_task_id = None
        self.entry_task.delete(0, tk.END)
        self.var_urgent.set(False)
        self.var_important.set(False)
        self.btn_save.config(text="Adicionar Tarefa", bg="#4CAF50")
        self.btn_cancel.pack_forget()

    def delete_task(self, task_id):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta tarefa?"):
            # DELETE no Banco
            self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()
            
            if self.editing_task_id == task_id:
                self.cancel_edit()
            self.refresh_ui()

    def refresh_ui(self):
        # Limpar UI
        for widget in self.q1_frame.winfo_children(): widget.destroy()
        for widget in self.q2_frame.winfo_children(): widget.destroy()
        for widget in self.q3_frame.winfo_children(): widget.destroy()
        for widget in self.q4_frame.winfo_children(): widget.destroy()

        # SELECT no Banco (Buscar tudo)
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()

        for row in rows:
            # row é uma tupla: (id, title, urgent, important)
            task_id, title, urgent, important = row
            
            target_frame = None
            if urgent and important:
                target_frame = self.q1_frame
            elif not urgent and important:
                target_frame = self.q2_frame
            elif urgent and not important:
                target_frame = self.q3_frame
            else:
                target_frame = self.q4_frame

            self.draw_task_card(target_frame, task_id, title, urgent, important)

    def draw_task_card(self, parent, task_id, title, urgent, important):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid")
        card.pack(fill="x", pady=2, padx=2)

        lbl = tk.Label(card, text=title, bg="white", anchor="w")
        lbl.pack(side="left", fill="x", expand=True, padx=5)

        # Passamos os argumentos para a função edit_task
        btn_edit = tk.Button(card, text="✎", font=("Arial", 8), 
                             command=lambda: self.edit_task(task_id, title, urgent, important))
        btn_edit.pack(side="right", padx=2)

        btn_del = tk.Button(card, text="✕", font=("Arial", 8), fg="red", 
                            command=lambda: self.delete_task(task_id))
        btn_del.pack(side="right", padx=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = EisenhowerApp(root)
    root.mainloop()