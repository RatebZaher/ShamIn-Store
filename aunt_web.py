import streamlit as st

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="ShamIn Store", layout="wide")

# ======================
# STYLE
# ======================
st.markdown("""
<style>

.card {
    background:#1a1d25;
    padding:15px;
    border-radius:18px;
    transition:0.3s;
    margin-bottom:15px;
}

/* hover للكرت */
.card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow:0 12px 35px rgba(0,0,0,0.6);
    border:1px solid #4ade80;
}

/* hover للصور */
img {
    border-radius:12px;
    transition:0.3s;
}

img:hover {
    transform: scale(1.03);
    filter: brightness(1.1);
}

/* hover للزر */
.stButton > button {
    background:#4ade80;
    color:black;
    border-radius:10px;
    transition:0.3s;
    font-weight:bold;
}

.stButton > button:hover {
    background:#22c55e;
    transform: scale(1.03);
    box-shadow:0 5px 15px rgba(34,197,94,0.3);
}

</style>
""", unsafe_allow_html=True)

# ======================
# DATA
# ======================
products = [
    {"id":1,"name":"Golden Mirror","price":120,"cat":"Mirrors","stock":5,"desc":"Luxury wall mirror","img":"eswara.png"},
    {"id":2,"name":"LED Lamp","price":45,"cat":"Lighting","stock":8,"desc":"Soft ambient lighting","img":"eswara.png"},
    {"id":3,"name":"Ceramic Vase","price":30,"cat":"Vases","stock":12,"desc":"Modern decor vase","img":"eswara.png"},
    {"id":4,"name":"Aroma Candle","price":18,"cat":"Candles","stock":20,"desc":"Relaxing scent candle","img":"eswara.png"},
    {"id":5,"name":"Wall Frames","price":60,"cat":"Frames","stock":7,"desc":"Art frame set","img":"eswara.png"},
    {"id":6,"name":"Boho Carpet","price":90,"cat":"Textiles","stock":4,"desc":"Soft boho rug","img":"eswara.png"},
    {"id":7,"name":"Crystal Lamp","price":150,"cat":"Lighting","stock":3,"desc":"Luxury crystal lamp","img":"eswara.png"},
    {"id":8,"name":"Desk Lamp","price":35,"cat":"Lighting","stock":10,"desc":"Study desk lamp","img":"eswara.png"},
]

# ======================
# STATE
# ======================
if "cart" not in st.session_state:
    st.session_state.cart = {}

def add_to_cart(pid, qty=1):
    st.session_state.cart[pid] = st.session_state.cart.get(pid, 0) + qty

def total_price():
    total = 0
    for pid, qty in st.session_state.cart.items():
        p = next(x for x in products if x["id"] == pid)
        total += p["price"] * qty
    return total

# ======================
# NAV
# ======================
page = st.sidebar.radio("Menu", ["Home", "Cart", "Checkout"])

# ======================
# HEADER
# ======================
st.markdown('<div class="title">ShamIn Store 🏠</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Luxury Decor Marketplace</div>', unsafe_allow_html=True)

# ======================
# HOME
# ======================
if page == "Home":

    search = st.sidebar.text_input("Search products")

    filtered = products
    if search:
        filtered = [p for p in products if search.lower() in p["name"].lower()]

    for i in range(0, len(filtered), 2):

        col1, col2 = st.columns(2)

        for col, product in zip([col1, col2], filtered[i:i + 2]):

            with col:

                st.markdown('<div class="card">', unsafe_allow_html=True)

                # IMAGE
                st.image("eswara.png", width=200)

                # INFO
                st.markdown(f"### {product['name']}")
                st.markdown(f"""
                💰 **Price:** ${product['price']}  
                📦 **Stock left:** {product['stock']}  
                🏷️ {product['cat']}
                """)

                st.write(product["desc"])

                qty = st.number_input("Qty", 1, 10, key=f"q_{product['id']}")

                # FIXED BUTTON
                if st.button("Add to Cart 🛒", key=f"add_{product['id']}"):

                    if product["stock"] >= qty:

                        product["stock"] -= qty

                        st.session_state.cart[product["id"]] = st.session_state.cart.get(product["id"], 0) + qty

                        st.session_state[f"msg_{product['id']}"] = "✅ تمّت الإضافة"

                        st.rerun()

                    else:
                        st.session_state[f"msg_{product['id']}"] = "❌ Not enough stock"
                        st.rerun()



                st.markdown('</div>', unsafe_allow_html=True)

# ======================
# CART
# ======================
elif page == "Cart":

    st.subheader("🛒 Your Cart")

    if not st.session_state.cart:
        st.info("Cart is empty")

    else:
        for pid, qty in st.session_state.cart.items():
            p = next(x for x in products if x["id"] == pid)

            col1, col2, col3 = st.columns([3,1,1])

            with col1:
                st.write(p["name"])

            with col2:
                st.write(f"x{qty}")

            with col3:
                st.write(f"${p['price'] * qty}")

        st.markdown("---")
        st.write(f"### Total: ${total_price()}")

        if st.button("🧹 Clear Cart"):
            st.session_state.cart = {}
            st.success("Cart cleared!")
            st.rerun()

# ======================
# CHECKOUT
# ======================
elif page == "Checkout":

    st.subheader("💳 Checkout")

    if not st.session_state.cart:
        st.warning("Cart empty")

    else:
        for pid, qty in st.session_state.cart.items():
            p = next(x for x in products if x["id"] == pid)
            st.write(f"- {p['name']} x{qty}")

        st.write(f"### Total: ${total_price()}")

        name = st.text_input("Full Name")
        address = st.text_area("Address")

        if st.button("Confirm Order"):
            if name and address:
                st.success("Order placed 🎉")
                st.session_state.cart = {}
            else:
                st.error("Fill all fields")