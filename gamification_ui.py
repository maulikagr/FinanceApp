import tkinter as tk
from tkinter import ttk, messagebox
from gamification import GamificationSystem, CharacterClass, CharacterLevel
import json
from datetime import datetime

class GamificationUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Finance App Gamification")
        self.root.geometry("800x600")
        
        # Initialize gamification system
        self.gamification = GamificationSystem()
        
        # Create main container
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.character_tab = ttk.Frame(self.notebook)
        self.missions_tab = ttk.Frame(self.notebook)
        self.challenges_tab = ttk.Frame(self.notebook)
        self.shop_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.character_tab, text="Character")
        self.notebook.add(self.missions_tab, text="Missions")
        self.notebook.add(self.challenges_tab, text="Challenges")
        self.notebook.add(self.shop_tab, text="Shop")
        
        # Initialize tabs
        self._setup_character_tab()
        self._setup_missions_tab()
        self._setup_challenges_tab()
        self._setup_shop_tab()
        
        # Load state if exists
        try:
            self.gamification.load_state("gamification_state.json")
        except:
            pass
    
    def _setup_character_tab(self):
        # Character creation frame
        create_frame = ttk.LabelFrame(self.character_tab, text="Create Character", padding="10")
        create_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(create_frame, text="User ID:").grid(row=0, column=0, padx=5, pady=5)
        self.user_id_entry = ttk.Entry(create_frame)
        self.user_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(create_frame, text="Character Name:").grid(row=1, column=0, padx=5, pady=5)
        self.character_name_entry = ttk.Entry(create_frame)
        self.character_name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(create_frame, text="Character Class:").grid(row=2, column=0, padx=5, pady=5)
        self.character_class_var = tk.StringVar()
        self.character_class_combo = ttk.Combobox(create_frame, textvariable=self.character_class_var)
        self.character_class_combo['values'] = [c.value for c in CharacterClass]
        self.character_class_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(create_frame, text="Create Character", command=self.create_character).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Character stats frame
        stats_frame = ttk.LabelFrame(self.character_tab, text="Character Stats", padding="10")
        stats_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.stats_labels = {}
        stats = ["Level", "Experience", "Coins", "Streak"]
        for i, stat in enumerate(stats):
            ttk.Label(stats_frame, text="{}:".format(stat)).grid(row=i, column=0, padx=5, pady=5)
            self.stats_labels[stat] = ttk.Label(stats_frame, text="0")
            self.stats_labels[stat].grid(row=i, column=1, padx=5, pady=5)
    
    def _setup_missions_tab(self):
        # Missions list frame
        missions_frame = ttk.LabelFrame(self.missions_tab, text="Active Missions", padding="10")
        missions_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create treeview for missions
        columns = ("Title", "Description", "Type", "Progress")
        self.missions_tree = ttk.Treeview(missions_frame, columns=columns, show="headings")
        
        for col in columns:
            self.missions_tree.heading(col, text=col)
            self.missions_tree.column(col, width=150)
        
        self.missions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(missions_frame, orient=tk.VERTICAL, command=self.missions_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.missions_tree.configure(yscrollcommand=scrollbar.set)
        
        # Assign missions button
        ttk.Button(self.missions_tab, text="Assign New Missions", command=self.assign_missions).grid(row=1, column=0, pady=10)
    
    def _setup_challenges_tab(self):
        # Challenges list frame
        challenges_frame = ttk.LabelFrame(self.challenges_tab, text="Active Challenges", padding="10")
        challenges_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create treeview for challenges
        columns = ("Title", "Description", "Type", "Progress", "Difficulty")
        self.challenges_tree = ttk.Treeview(challenges_frame, columns=columns, show="headings")
        
        for col in columns:
            self.challenges_tree.heading(col, text=col)
            self.challenges_tree.column(col, width=120)
        
        self.challenges_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(challenges_frame, orient=tk.VERTICAL, command=self.challenges_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.challenges_tree.configure(yscrollcommand=scrollbar.set)
        
        # Assign challenge button
        ttk.Button(self.challenges_tab, text="Assign New Challenge", command=self.assign_challenge).grid(row=1, column=0, pady=10)
    
    def _setup_shop_tab(self):
        # Shop items frame
        shop_frame = ttk.LabelFrame(self.shop_tab, text="Available Items", padding="10")
        shop_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create treeview for shop items
        columns = ("Item", "Type", "Cost")
        self.shop_tree = ttk.Treeview(shop_frame, columns=columns, show="headings")
        
        for col in columns:
            self.shop_tree.heading(col, text=col)
            self.shop_tree.column(col, width=150)
        
        self.shop_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(shop_frame, orient=tk.VERTICAL, command=self.shop_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.shop_tree.configure(yscrollcommand=scrollbar.set)
        
        # Purchase button
        ttk.Button(self.shop_tab, text="Purchase Selected Item", command=self.purchase_item).grid(row=1, column=0, pady=10)
    
    def create_character(self):
        user_id = self.user_id_entry.get()
        name = self.character_name_entry.get()
        character_class = CharacterClass(self.character_class_var.get())
        
        if not all([user_id, name, character_class]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        character = self.gamification.create_character(user_id, name, character_class)
        self.update_character_stats(character)
        messagebox.showinfo("Success", "Character {} created successfully!".format(name))
    
    def update_character_stats(self, character):
        self.stats_labels["Level"].config(text=character.level.name)
        self.stats_labels["Experience"].config(text=str(character.experience))
        self.stats_labels["Coins"].config(text=str(character.coins))
        self.stats_labels["Streak"].config(text=str(character.streak))
    
    def assign_missions(self):
        user_id = self.user_id_entry.get()
        if not user_id:
            messagebox.showerror("Error", "Please create a character first")
            return
        
        missions = self.gamification.assign_missions(user_id)
        self.update_missions_list(user_id)
        messagebox.showinfo("Success", "Assigned {} new missions!".format(len(missions)))
    
    def update_missions_list(self, user_id):
        # Clear existing items
        for item in self.missions_tree.get_children():
            self.missions_tree.delete(item)
        
        # Add new items
        missions = self.gamification.get_active_missions(user_id)
        for mission in missions:
            self.missions_tree.insert("", "end", values=(
                mission.title,
                mission.description,
                mission.mission_type.value,
                "Completed" if mission.is_completed else "In Progress"
            ))
    
    def assign_challenge(self):
        user_id = self.user_id_entry.get()
        if not user_id:
            messagebox.showerror("Error", "Please create a character first")
            return
        
        challenge = self.gamification.assign_challenge(user_id)
        if challenge:
            self.update_challenges_list(user_id)
            messagebox.showinfo("Success", "Assigned new challenge: {}".format(challenge.title))
        else:
            messagebox.showinfo("Info", "No new challenges available")
    
    def update_challenges_list(self, user_id):
        # Clear existing items
        for item in self.challenges_tree.get_children():
            self.challenges_tree.delete(item)
        
        # Add new items
        challenges = self.gamification.get_active_challenges(user_id)
        for challenge in challenges:
            self.challenges_tree.insert("", "end", values=(
                challenge.title,
                challenge.description,
                challenge.challenge_type.value,
                "{:.1f}%".format(challenge.progress),
                challenge.difficulty
            ))
    
    def purchase_item(self):
        user_id = self.user_id_entry.get()
        if not user_id:
            messagebox.showerror("Error", "Please create a character first")
            return
        
        selected_item = self.shop_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to purchase")
            return
        
        # Get item details from the tree
        item_values = self.shop_tree.item(selected_item[0])['values']
        item_id = item_values[0]
        item_type = item_values[1]
        cost = int(item_values[2])
        
        if self.gamification.purchase_item(user_id, item_type, item_id, cost):
            messagebox.showinfo("Success", "Successfully purchased {}!".format(item_id))
            self.update_character_stats(self.gamification.get_character(user_id))
        else:
            messagebox.showerror("Error", "Not enough coins to purchase this item")

def main():
    root = tk.Tk()
    app = GamificationUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 