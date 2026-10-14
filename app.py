import os
import pandas as pd
import streamlit as st

# Data files setup
PRODUCTS_FILE = "products.csv"
SALES_FILE = "sales.csv"


def init_files():
  if not os.path.exists(PRODUCTS_FILE):
    df_prod = pd.DataFrame(
        columns=[
            "ProductID",
            "ProductName",
            "Category",
            "Price",
            "StockQuantity",
        ]
    )
    df_prod.to_csv(PRODUCTS_FILE, index=False)

  if not os.path.exists(SALES_FILE):
    df_sales = pd.DataFrame(
        columns=[
            "TransactionID",
            "ProductID",
            "ProductName",
            "QuantitySold",
            "TotalPrice",
            "Date",
        ]
    )
    df_sales.to_csv(SALES_FILE, index=False)


init_files()

# Page Layout
st.set_page_config(
    page_title="GreenLeaf Grocers Management System", layout="wide"
)

st.title("🌿 GreenLeaf Grocers - Inventory & Sales Management System")
st.markdown("---")

# Sidebar Menu
menu = st.sidebar.selectbox(
    "Navigation Menu",
    [
        "Analytics Dashboard",
        "Product Management",
        "Billing / POS",
        "View Sales History",
    ],
)

df_products = pd.read_csv(PRODUCTS_FILE)
df_sales = pd.read_csv(SALES_FILE)

# 1. ANALYTICS DASHBOARD
if menu == "Analytics Dashboard":
  st.header("📊 Business Analytics Dashboard")

  if df_sales.empty:
    st.info(
        "No sales data available yet. Pehle 'Billing / POS' se kuch items sell"
        " karein!"
    )
  else:
    total_revenue = df_sales["TotalPrice"].sum()
    total_items_sold = df_sales["QuantitySold"].sum()
    total_transactions = len(df_sales)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"₹ {total_revenue:,.2f}")
    col2.metric("Total Items Sold", total_items_sold)
    col3.metric("Total Transactions", total_transactions)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
      st.subheader("Top Selling Products")
      top_products = (
          df_sales.groupby("ProductName")["QuantitySold"].sum().reset_index()
      )
      if not top_products.empty:
        st.bar_chart(
            top_products.set_index("ProductName")["QuantitySold"],
            color="#2ecc71",
        )

    with col_b:
      st.subheader("Low Stock Alerts")
      if not df_products.empty:
        low_stock = df_products[df_products["StockQuantity"] < 10]
        if not low_stock.empty:
          st.warning("Yeh products khatam hone wale hain (Stock < 10):")
          st.dataframe(low_stock, hide_index=True)
        else:
          st.success("Sabhi products ka stock sufficient hai!")

# 2. PRODUCT MANAGEMENT
elif menu == "Product Management":
  st.header("📦 Product Inventory Management")

  tab1, tab2 = st.tabs(["Add New Product", "View All Products"])

  with tab1:
    st.subheader("Naya Product Add Karein")
    with st.form("add_prod"):
      p_id = st.text_input(
          "Product ID", value=f"P{len(df_products) + 1:03d}"
      )
      p_name = st.text_input("Product Name (e.g., Fresh Milk)")
      category = st.selectbox(
          "Category",
          ["Vegetables", "Fruits", "Dairy", "Bakery", "Beverages", "Snacks"],
      )
      price = st.number_input("Price per Unit (₹)", min_value=1.0, value=40.0)
      stock = st.number_input(
          "Stock Quantity", min_value=1, value=100, step=1
      )

      submitted = st.form_submit_button("Save Product")
      if submitted:
        if p_name.strip() == "":
          st.error("Product nameali nahi ho sakta!")
        else:
          new_row = pd.DataFrame(
              [[p_id, p_name, category, price, stock]],
              columns=df_products.columns,
          )
          df_products = pd.concat([df_products, new_row], ignore_index=True)
          df_products.to_csv(PRODUCTS_FILE, index=False)
          st.success(f"Product '{p_name}' successfully add ho gaya!")
          st.rerun()

  with tab2:
    st.subheader("Current Inventory List")
    if df_products.empty:
      st.info("Abhi koi product add nahi kiya gaya hai.")
    else:
      st.dataframe(df_products, use_container_width=True, hide_index=True)

# 3. BILLING / POS SYSTEM
elif menu == "Billing / POS":
  st.header("🛒 Point of Sale (Billing Counter)")

  if df_products.empty:
    st.warning("Pehle 'Product Management' me jaakar kuch products add karein.")
  else:
    selected_product = st.selectbox(
        "Product Chuniye", df_products["ProductName"].tolist()
    )

    p_row = df_products[df_products["ProductName"] == selected_product].iloc[0]
    avail_stock = p_row["StockQuantity"]
    unit_price = p_row["Price"]

    st.write(
        f"**Available Stock:** {avail_stock} units | **Price:** ₹ {unit_price}"
        " per unit"
    )

    qty = st.number_input(
        "Kitni quantity chahiye?", min_value=1, max_value=int(avail_stock), value=1
    )
    total_bill = qty * unit_price
    st.info(f"**Total Bill Amount:** ₹ {total_bill:.2f}")

    if st.button("Complete Sale & Print Bill"):
      # Update Stock
      df_products.loc[
          df_products["ProductName"] == selected_product, "StockQuantity"
      ] -= qty
      df_products.to_csv(PRODUCTS_FILE, index=False)

      # Save Transaction
      new_trx = pd.DataFrame(
          [[
              f"TRX{len(df_sales) + 1:04d}",
              p_row["ProductID"],
              selected_product,
              qty,
              total_bill,
              pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
          ]],
          columns=df_sales.columns,
      )
      df_sales = pd.concat([df_sales, new_trx], ignore_index=True)
      df_sales.to_csv(SALES_FILE, index=False)

      st.success("Sale successful! Inventory update ho gayi hai.")
      st.balloons()

# 4. VIEW SALES HISTORY
elif menu == "View Sales History":
  st.header("📜 Sales Transaction History")
  if df_sales.empty:
    st.info("Abhi tak koi sale record nahi hai.")
  else:
    st.dataframe(df_sales, use_container_width=True, hide_index=True)