import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

class Character:
    def __init__(self, name, birth=None, death=None, gender=None, hair=None, height=None, race=None, realm=None, spouse=None):
        self.name = name
        self.birth = birth
        self.death = death
        self.gender = gender
        self.hair = hair
        self.height = height
        self.race = race
        self.realm = realm
        self.spouse = spouse

    def info(self):
        spouse_name = self.spouse.name if isinstance(self.spouse, Character) else self.spouse
        return {
            "birth": self.birth or "",
            "death": self.death or "",
            "gender": self.gender or "",
            "hair": self.hair or "",
            "height": self.height or "",
            "name": self.name,
            "race": self.race or "",
            "realm": self.realm or "",
            "spouse": spouse_name or ""
        }

def load_characters(csv_file):
    df = pd.read_csv(csv_file, sep='\t')
    characters = {}
    for _, row in df.iterrows():
        name = row.get('name')
        if not name:
            continue
        char = Character(
            name=name,
            birth=row.get('birth'),
            death=row.get('death'),
            gender=row.get('gender'),
            hair=row.get('hair'),
            height=row.get('height'),
            race=row.get('race'),
            realm=row.get('realm'),
            spouse=row.get('spouse')
        )
        characters[name] = char

    for char in characters.values():
        spouse_name = char.spouse
        if spouse_name and spouse_name in characters:
            char.spouse = characters[spouse_name]
    return characters

def save_characters_to_csv(characters, csv_file):
    data = []
    for char in characters.values():
        data.append(char.info())
    df = pd.DataFrame(data)
    df.to_csv(csv_file, sep='\t', index=False)

class CharacterApp:
    def __init__(self, root, csv_file):
        self.root = root
        self.root.title("Middle-earth Characters")
        self.csv_file = csv_file
        self.characters = load_characters(csv_file)
        self.filtered_names = list(self.characters.keys())

        self.setup_ui()
        self.refresh_listbox()

    def setup_ui(self):
        # Left frame for list and search
        left_frame = ttk.Frame(self.root)
        left_frame.grid(row=0, column=0, sticky="ns")

        ttk.Label(left_frame, text="Search:").pack(anchor='w', padx=5, pady=2)
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.filter_characters)
        search_entry = ttk.Entry(left_frame, textvariable=self.search_var)
        search_entry.pack(fill='x', padx=5)

        self.listbox = tk.Listbox(left_frame, width=30, height=20)
        self.listbox.pack(side='left', fill='y', padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        scrollbar = ttk.Scrollbar(left_frame, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Right frame for details form
        right_frame = ttk.Frame(self.root, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        # Make right_frame stretchable
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Form fields
        self.fields = {}
        labels = ["Name", "Birth", "Death", "Gender", "Hair", "Height", "Race", "Realm", "Spouse"]
        for i, label in enumerate(labels):
            ttk.Label(right_frame, text=label+":").grid(row=i, column=0, sticky="e", pady=3)
        
        self.name_var = tk.StringVar()
        self.fields["name"] = ttk.Entry(right_frame, textvariable=self.name_var)
        self.fields["name"].grid(row=0, column=1, sticky="ew", pady=3)

        self.birth_var = tk.StringVar()
        self.fields["birth"] = ttk.Entry(right_frame, textvariable=self.birth_var)
        self.fields["birth"].grid(row=1, column=1, sticky="ew", pady=3)

        self.death_var = tk.StringVar()
        self.fields["death"] = ttk.Entry(right_frame, textvariable=self.death_var)
        self.fields["death"].grid(row=2, column=1, sticky="ew", pady=3)

        self.gender_var = tk.StringVar()
        self.fields["gender"] = ttk.Entry(right_frame, textvariable=self.gender_var)
        self.fields["gender"].grid(row=3, column=1, sticky="ew", pady=3)

        self.hair_var = tk.StringVar()
        self.fields["hair"] = ttk.Entry(right_frame, textvariable=self.hair_var)
        self.fields["hair"].grid(row=4, column=1, sticky="ew", pady=3)

        self.height_var = tk.StringVar()
        self.fields["height"] = ttk.Entry(right_frame, textvariable=self.height_var)
        self.fields["height"].grid(row=5, column=1, sticky="ew", pady=3)

        self.race_var = tk.StringVar()
        self.fields["race"] = ttk.Entry(right_frame, textvariable=self.race_var)
        self.fields["race"].grid(row=6, column=1, sticky="ew", pady=3)

        self.realm_var = tk.StringVar()
        self.fields["realm"] = ttk.Entry(right_frame, textvariable=self.realm_var)
        self.fields["realm"].grid(row=7, column=1, sticky="ew", pady=3)

        # Spouse Combobox with autocomplete
        self.spouse_var = tk.StringVar()
        self.fields["spouse"] = ttk.Combobox(right_frame, textvariable=self.spouse_var)
        self.fields["spouse"]['values'] = sorted(self.characters.keys())
        self.fields["spouse"].grid(row=8, column=1, sticky="ew", pady=3)

        right_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=10)

        self.add_btn = ttk.Button(btn_frame, text="Add New", command=self.add_character)
        self.add_btn.grid(row=0, column=0, padx=5)

        self.update_btn = ttk.Button(btn_frame, text="Update", command=self.update_character)
        self.update_btn.grid(row=0, column=1, padx=5)

        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete_character)
        self.delete_btn.grid(row=0, column=2, padx=5)

        self.save_btn = ttk.Button(btn_frame, text="Save to CSV", command=self.save_characters)
        self.save_btn.grid(row=0, column=3, padx=5)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for name in sorted(self.filtered_names):
            self.listbox.insert(tk.END, name)
        self.fields["spouse"]['values'] = sorted(self.characters.keys())

    def filter_characters(self, *args):
        search = self.search_var.get().lower()
        self.filtered_names = [name for name in self.characters if search in name.lower()]
        self.refresh_listbox()

    def on_select(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        name = self.listbox.get(selection)
        char = self.characters.get(name)
        if not char:
            return
        # Fill form with character data
        self.name_var.set(char.name)
        self.birth_var.set(char.birth or "")
        self.death_var.set(char.death or "")
        self.gender_var.set(char.gender or "")
        self.hair_var.set(char.hair or "")
        self.height_var.set(char.height or "")
        self.race_var.set(char.race or "")
        self.realm_var.set(char.realm or "")
        spouse_name = char.spouse.name if isinstance(char.spouse, Character) else char.spouse or ""
        self.spouse_var.set(spouse_name)

    def clear_form(self):
        for var in [self.name_var, self.birth_var, self.death_var, self.gender_var, self.hair_var,
                    self.height_var, self.race_var, self.realm_var, self.spouse_var]:
            var.set("")

    def add_character(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        if name in self.characters:
            messagebox.showerror("Error", f"Character '{name}' already exists.")
            return
        spouse_name = self.spouse_var.get().strip()
        spouse = self.characters.get(spouse_name, spouse_name if spouse_name else None)

        new_char = Character(
            name=name,
            birth=self.birth_var.get().strip() or None,
            death=self.death_var.get().strip() or None,
            gender=self.gender_var.get().strip() or None,
            hair=self.hair_var.get().strip() or None,
            height=self.height_var.get().strip() or None,
            race=self.race_var.get().strip() or None,
            realm=self.realm_var.get().strip() or None,
            spouse=spouse
        )
        self.characters[name] = new_char
        self.filtered_names.append(name)
        self.refresh_listbox()
        messagebox.showinfo("Success", f"Character '{name}' added!")
        self.clear_form()

    def update_character(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Select a character to update.")
            return
        old_name = self.listbox.get(selection)
        char = self.characters.get(old_name)
        if not char:
            return

        new_name = self.name_var.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return
        if new_name != old_name and new_name in self.characters:
            messagebox.showerror("Error", f"Name '{new_name}' already exists.")
            return

        spouse_name = self.spouse_var.get().strip()
        spouse = self.characters.get(spouse_name, spouse_name if spouse_name else None)

        # Update character attributes
        char.name = new_name
        char.birth = self.birth_var.get().strip() or None
        char.death = self.death_var.get().strip() or None
        char.gender = self.gender_var.get().strip() or None
        char.hair = self.hair_var.get().strip() or None
        char.height = self.height_var.get().strip() or None
        char.race = self.race_var.get().strip() or None
        char.realm = self.realm_var.get().strip() or None
        char.spouse = spouse

        if new_name != old_name:
            # Rename key in dictionary
            self.characters[new_name] = char
            del self.characters[old_name]
            self.filtered_names = [new_name if n == old_name else n for n in self.filtered_names]

        self.refresh_listbox()
        self.clear_form()
        messagebox.showinfo("Success", f"Character '{new_name}' updated!")

    def delete_character(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Select a character to delete.")
            return
        name = self.listbox.get(selection)
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            del self.characters[name]
            self.filtered_names = [n for n in self.filtered_names if n != name]
            # Remove spouse refs
            for c in self.characters.values():
                if isinstance(c.spouse, Character) and c.spouse.name == name:
                    c.spouse = None
            self.refresh_listbox()
            self.clear_form()

    def save_characters(self):
        save_characters_to_csv(self.characters, self.csv_file)
        messagebox.showinfo("Saved", f"Data saved to {self.csv_file}")

if __name__ == "__main__":
    csv_file = "lotr.csv"  # update this to your actual CSV file path
    root = tk.Tk()
    app = CharacterApp(root, csv_file)
    root.mainloop()
