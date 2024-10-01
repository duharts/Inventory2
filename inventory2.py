import sqlite3
import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# Set page config
st.set_page_config(page_title="Pantry Inventory", page_icon=":shopping_bags:")

# Database file path
DB_FILENAME = Path(__file__).parent / "pantry_inventory.db"

# Function to connect to SQLite database
def connect_db():
    conn = sqlite3.connect(DB_FILENAME)
    return conn

# Function to create the inventory table if not exists
def initialize_db(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                quantity INTEGER,
                reorder_point INTEGER
            )
        """)

# Function to load data from the SQLite database
def load_data(conn):
    return pd.read_sql("SELECT * FROM inventory", conn)

# Function to insert a new item into the inventory
def add_item(conn, item_name, quantity, reorder_point):
    with conn:
        conn.execute(
            "INSERT INTO inventory (item_name, quantity, reorder_point) VALUES (?, ?, ?)",
            (item_name, quantity, reorder_point),
        )

# Function to update an item in the inventory after selling
def sell_item(conn, item_name, quantity_sold):
    with conn:
        conn.execute(
            "UPDATE inventory SET quantity = quantity - ? WHERE item_name = ?",
            (quantity_sold, item_name),
        )

# Initialize database and connect
conn = connect_db()
initialize_db(conn)

# Display current inventory
st.title("Pantry Inventory Tracker")
st.write("Track and manage your pantry inventory:")

# Load the data
df = load_data(conn)

# Display the current inventory
st.subheader("Current Inventory")
st.table(df)

# Form to sell an item
st.subheader("Sell an Item")
item_to_sell = st.selectbox("Select Item", df["item_name"])
quantity_sold = st.number_input("Quantity Sold", min_value=0)

# Update the quantity of the sold item
if st.button("Sell Item"):
    sell_item(conn, item_to_sell, quantity_sold)
    st.success(f"Sold {quantity_sold} units of {item_to_sell}!")
    df = load_data(conn)  # Reload data to show updated inventory
    st.table(df)

# Function to show reorder alert
def reorder_alert(df):
    need_to_reorder = df[df["quantity"] < df["reorder_point"]].loc[:, "item_name"]
    if len(need_to_reorder) > 0:
        items = "\n".join(f"* {name}" for name in need_to_reorder)
        st.warning(f"Reorder needed for the following items:\n {items}")

# Check for reorder alerts
reorder_alert(df)

# Add new item form
st.subheader("Add New Item")
new_item = st.text_input("Item Name")
new_quantity = st.number_input("Quantity", min_value=0)
new_reorder_point = st.number_input("Reorder Point", min_value=0)

if st.button("Add Item"):
    add_item(conn, new_item, new_quantity, new_reorder_point)
    st.success(f"{new_item} added to the pantry!")
    df = load_data(conn)  # Reload data to show updated inventory
    st.table(df)

# Sample pantry items to populate the database
st.subheader("Sample New Inventory List")
if st.button("Add Sample Inventory"):
    sample_items = [
        ("Flour", 100, 20),
        ("Sugar", 50, 10),
        ("Olive Oil", 25, 5),
        ("Canned Tomatoes", 150, 30),
        ("Spaghetti", 200, 50),
        ("Rice", 300, 60)
    ]
    with conn:
        conn.executemany(
            "INSERT INTO inventory (item_name, quantity, reorder_point) VALUES (?, ?, ?)",
            sample_items
        )
    st.success("Sample items added to the pantry!")
    df = load_data(conn)  # Reload data to show updated inventory
    st.table(df)

# Option to download inventory as CSV
@st.cache
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(df)
st.download_button(label="Download Inventory as CSV", data=csv, file_name='pantry_inventory.csv', mime='text/csv')

# Inventory chart
st.subheader("Inventory Levels")
if not df.empty:
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("item_name", sort="-y"),
        y="quantity",
        color="item_name"
    )
    st.altair_chart(chart, use_container_width=True)
