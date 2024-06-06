import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import firebase_admin
from firebase_admin import credentials, firestore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DatabaseVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GraphDBViewer")
        self.root.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        self.title_label = tk.Label(self.root, text="GraphDBViewer", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        self.db_type_label = tk.Label(self.root, text="Database Type:")
        self.db_type_label.pack(pady=5)
        self.db_type_var = tk.StringVar(value="mongodb")
        self.db_type_mongo = tk.Radiobutton(self.root, text="MongoDB", variable=self.db_type_var, value="mongodb")
        self.db_type_firebase = tk.Radiobutton(self.root, text="Firebase", variable=self.db_type_var, value="firebase")
        self.db_type_mongo.pack(pady=5)
        self.db_type_firebase.pack(pady=5)

        self.mongo_label = tk.Label(self.root, text="MongoDB Connection URI:")
        self.mongo_label.pack(pady=5)
        self.mongo_entry = tk.Entry(self.root, width=50)
        self.mongo_entry.pack(pady=5)

        self.db_label = tk.Label(self.root, text="Database Name:")
        self.db_label.pack(pady=5)
        self.db_entry = tk.Entry(self.root, width=50)
        self.db_entry.pack(pady=5)

        self.collection_label = tk.Label(self.root, text="Collection Name:")
        self.collection_label.pack(pady=5)
        self.collection_entry = tk.Entry(self.root, width=50)
        self.collection_entry.pack(pady=5)

        self.firebase_cred_label = tk.Label(self.root, text="Firebase Credentials JSON Path:")
        self.firebase_cred_label.pack(pady=5)
        self.firebase_cred_entry = tk.Entry(self.root, width=50)
        self.firebase_cred_entry.pack(pady=5)

        self.firebase_collection_label = tk.Label(self.root, text="Firebase Collection Name:")
        self.firebase_collection_label.pack(pady=5)
        self.firebase_collection_entry = tk.Entry(self.root, width=50)
        self.firebase_collection_entry.pack(pady=5)

        self.fetch_button = tk.Button(self.root, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.pack(pady=20)

        self.figure_frame = tk.Frame(self.root)
        self.figure_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    def fetch_data(self):
        db_type = self.db_type_var.get()

        if db_type == "mongodb":
            mongo_uri = self.mongo_entry.get()
            db_name = self.db_entry.get()
            collection_name = self.collection_entry.get()

            if not mongo_uri or not db_name or not collection_name:
                messagebox.showerror("Input Error", "Please enter the MongoDB URI, database name, and collection name.")
                return

            try:
                client = MongoClient(mongo_uri)
                db = client[db_name]
                collection = db[collection_name]
                users = list(collection.find())

                if not users:
                    messagebox.showinfo("No Data", "No data found in the specified collection.")
                    return

                self.plot_user_data(users)
            except Exception as e:
                messagebox.showerror("Error Fetching Data", str(e))
        
        elif db_type == "firebase":
            cred_path = self.firebase_cred_entry.get()
            collection_name = self.firebase_collection_entry.get()

            if not cred_path or not collection_name:
                messagebox.showerror("Input Error", "Please enter the Firebase credentials JSON path and collection name.")
                return

            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                collection = db.collection(collection_name)
                users = [doc.to_dict() for doc in collection.stream()]

                if not users:
                    messagebox.showinfo("No Data", "No data found in the specified collection.")
                    return

                self.plot_user_data(users)
            except Exception as e:
                messagebox.showerror("Error Fetching Data", str(e))

    def plot_user_data(self, users):
        fig, axs = plt.subplots(1, 1, figsize=(10, 8))

        for widget in self.figure_frame.winfo_children():
            widget.destroy()

        usernames = [user['username'] for user in users]
        ages = [user['age'] for user in users]
        axs.bar(usernames, ages)
        axs.set_title('User Data')
        axs.set_xlabel('Username')
        axs.set_ylabel('Age')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.figure_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseVisualizerApp(root)
    root.mainloop()