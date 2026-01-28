import tkinter as tk
from tkinter import ttk, messagebox

class EisenhowerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matriz de Eisenhower - To-Do List")
        self.root.geometry("1000x700")

        # Dados das tarefas (Lista de dicionários)
        self.tasks = []
        self.editing_task_id = None  # Para controlar qual tarefa está sendo editada

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
        # O botão cancelar começa escondido
        
        # --- Área da Matriz (Centro) ---
        self.frame_matrix = tk.Frame(self.root)
        self.frame_matrix.pack(fill="both", expand=True, padx=10, pady=10)

        # Configuração do Grid 2x2
        self.frame_matrix.columnconfigure(0, weight=1)
        self.frame_matrix.columnconfigure(1, weight=1)
        self.frame_matrix.rowconfigure(0, weight=1)
        self.frame_matrix.rowconfigure(1, weight=1)

        # Criação dos 4 Quadrantes
        # Q1: Urgente & Importante (Faça Agora) - Vermelho claro
        self.q1_frame = self.create_quadrant(0, 0, "1. FAÇA AGORA (Urgente & Importante)", "#ffcccc")
        
        # Q2: Não Urgente & Importante (Agende) - Azul claro
        self.q2_frame = self.create_quadrant(0, 1, "2. AGENDE (Não Urgente & Importante)", "#ccffff")
        
        # Q3: Urgente & Não Importante (Delegue) - Amarelo claro
        self.q3_frame = self.create_quadrant(1, 0, "3. DELEGUE (Urgente & Não Importante)", "#ffffcc")
        
        # Q4: Não Urgente & Não Importante (Elimine) - Cinza claro
        self.q4_frame = self.create_quadrant(1, 1, "4. ELIMINE (Nem Urgente & Nem Importante)", "#e0e0e0")

    def create_quadrant(self, row, col, title, bg_color):
        """Cria um frame para o quadrante e retorna o container interno para as tarefas"""
        frame = tk.LabelFrame(self.frame_matrix, text=title, bg=bg_color, font=("Arial", 10, "bold"))
        frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        # Canvas e Scrollbar para permitir rolagem se houver muitas tarefas
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

        is_urgent = self.var_urgent.get()
        is_important = self.var_important.get()

        if self.editing_task_id is not None:
            # Atualizar tarefa existente
            for task in self.tasks:
                if task['id'] == self.editing_task_id:
                    task['title'] = title
                    task['urgent'] = is_urgent
                    task['important'] = is_important
                    break
            self.cancel_edit() # Reseta o estado de edição
            messagebox.showinfo("Sucesso", "Tarefa atualizada!")
        else:
            # Criar nova tarefa
            new_id = len(self.tasks) + 1 if not self.tasks else max(t['id'] for t in self.tasks) + 1
            self.tasks.append({
                'id': new_id,
                'title': title,
                'urgent': is_urgent,
                'important': is_important
            })

        self.entry_task.delete(0, tk.END)
        self.var_urgent.set(False)
        self.var_important.set(False)
        self.refresh_ui()

    def edit_task(self, task):
        """Carrega os dados da tarefa nos campos de input"""
        self.entry_task.delete(0, tk.END)
        self.entry_task.insert(0, task['title'])
        self.var_urgent.set(task['urgent'])
        self.var_important.set(task['important'])
        
        self.editing_task_id = task['id']
        self.btn_save.config(text="Atualizar Tarefa", bg="#2196F3")
        self.btn_cancel.pack(side="left", padx=5)

    def cancel_edit(self):
        """Cancela o modo de edição e limpa os campos"""
        self.editing_task_id = None
        self.entry_task.delete(0, tk.END)
        self.var_urgent.set(False)
        self.var_important.set(False)
        self.btn_save.config(text="Adicionar Tarefa", bg="#4CAF50")
        self.btn_cancel.pack_forget()

    def delete_task(self, task_id):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta tarefa?"):
            self.tasks = [t for t in self.tasks if t['id'] != task_id]
            # Se estiver editando a tarefa que foi deletada, cancela a edição
            if self.editing_task_id == task_id:
                self.cancel_edit()
            self.refresh_ui()

    def refresh_ui(self):
        """Limpa e redesenha todas as tarefas nos quadrantes corretos"""
        # Limpar todos os quadrantes
        for widget in self.q1_frame.winfo_children(): widget.destroy()
        for widget in self.q2_frame.winfo_children(): widget.destroy()
        for widget in self.q3_frame.winfo_children(): widget.destroy()
        for widget in self.q4_frame.winfo_children(): widget.destroy()

        # Distribuir tarefas
        for task in self.tasks:
            target_frame = None
            
            # Lógica da Matriz
            if task['urgent'] and task['important']:
                target_frame = self.q1_frame
            elif not task['urgent'] and task['important']:
                target_frame = self.q2_frame
            elif task['urgent'] and not task['important']:
                target_frame = self.q3_frame
            else:
                target_frame = self.q4_frame

            self.draw_task_card(target_frame, task)

    def draw_task_card(self, parent, task):
        """Desenha o 'card' da tarefa dentro do quadrante"""
        card = tk.Frame(parent, bg="white", bd=1, relief="solid")
        card.pack(fill="x", pady=2, padx=2)

        lbl = tk.Label(card, text=task['title'], bg="white", anchor="w")
        lbl.pack(side="left", fill="x", expand=True, padx=5)

        # Botão Editar (ícone textual simples)
        btn_edit = tk.Button(card, text="✎", font=("Arial", 8), command=lambda t=task: self.edit_task(t))
        btn_edit.pack(side="right", padx=2)

        # Botão Excluir
        btn_del = tk.Button(card, text="✕", font=("Arial", 8), fg="red", command=lambda tid=task['id']: self.delete_task(tid))
        btn_del.pack(side="right", padx=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = EisenhowerApp(root)
    root.mainloop()