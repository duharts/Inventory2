import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Pantry Inventory", page_icon=":shopping_bags:")

# Sample data for pantry inventory
data = {
    'Item': ['Rice', 'Pasta', 'Canned Beans', 'Cereal', 'Peanut Butter'],
    'Quantity': [100, 50, 200, 80, 30],
    'Reorder Point': [20, 10, 50, 15, 5]
}

# Create DataFrame
df = pd.DataFrame(data)

# Display inventory
st.title("Pantry Inventory Tracker")
st.write("Track and manage your pantry inventory:")

# Function to display reorder alert
def reorder_alert(df):
    need_to_reorder = df[df["Quantity"] < df["Reorder Point"]].loc[:, "Item"]
    if len(need_to_reorder) > 0:
        items = "\n".join(f"* {name}" for name in need_to_reorder)
        st.warning(f"Reorder needed for the following items:\n {items}")

# Display inventory
st.subheader("Current Inventory")
st.table(df)

# Sell item form
st.subheader("Sell an Item")
item_to_sell = st.selectbox("Select Item", df["Item"])
quantity_sold = st.number_input("Quantity Sold", min_value=0)

# Sell item button
if st.button("Sell Item"):
    df.loc[df["Item"] == item_to_sell, "Quantity"] -= quantity_sold
    st.success(f"Sold {quantity_sold} units of {item_to_sell}!")
    st.write("Updated Inventory:")
    st.table(df)

# Check for reorder alerts
reorder_alert(df)

# Add new item form
st.subheader("Add New Item")
new_item = st.text_input("Item Name")
new_quantity = st.number_input("Quantity", min_value=0)
new_reorder_point = st.number_input("Reorder Point", min_value=0)

if st.button("Add Item"):
    new_data = {'Item': new_item, 'Quantity': new_quantity, 'Reorder Point': new_reorder_point}
    df = df.append(new_data, ignore_index=True)
    st.success(f"{new_item} added to the pantry!")
    st.write("Updated Inventory:")
    st.table(df)

# Option to download inventory as CSV
@st.cache
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(df)
st.download_button(label="Download Inventory as CSV", data=csv, file_name='pantry_inventory.csv', mime='text/csv')
