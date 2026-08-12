from pathlib import Path
from html import escape
import re

import streamlit as st


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="ShamIn Store",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# DATA
# ============================================================

PRODUCTS = (
    {
        "id": 1,
        "name": "Golden Mirror",
        "price": 120,
        "cat": "Mirrors",
        "stock": 5,
        "desc": "Luxury wall mirror with refined golden brass frame.",
        "img": "eswara.png",
    },
    {
        "id": 2,
        "name": "LED Ambient Lamp",
        "price": 45,
        "cat": "Lighting",
        "stock": 8,
        "desc": "Soft ambient lighting designed for cozy evenings.",
        "img": "eswara.png",
    },
    {
        "id": 3,
        "name": "Ceramic Vase",
        "price": 30,
        "cat": "Vases",
        "stock": 12,
        "desc": "Modern minimalist decor vase for floral arrangements.",
        "img": "eswara.png",
    },
    {
        "id": 4,
        "name": "Aroma Candle",
        "price": 18,
        "cat": "Candles",
        "stock": 20,
        "desc": "Relaxing scented soy wax candle in matte glass.",
        "img": "eswara.png",
    },
    {
        "id": 5,
        "name": "Wall Frames Set",
        "price": 60,
        "cat": "Frames",
        "stock": 7,
        "desc": "Curated gallery art frame set for living spaces.",
        "img": "eswara.png",
    },
    {
        "id": 6,
        "name": "Boho Carpet",
        "price": 90,
        "cat": "Textiles",
        "stock": 4,
        "desc": "Soft boho rug with intricate geometric patterns.",
        "img": "eswara.png",
    },
    {
        "id": 7,
        "name": "Crystal Pendant Lamp",
        "price": 150,
        "cat": "Lighting",
        "stock": 3,
        "desc": "Luxury crystal lamp reflecting warm golden light.",
        "img": "eswara.png",
    },
    {
        "id": 8,
        "name": "Minimalist Desk Lamp",
        "price": 35,
        "cat": "Lighting",
        "stock": 10,
        "desc": "Adjustable study desk lamp with sleek metal finish.",
        "img": "eswara.png",
    },
)


PAGES = {
    "Home",
    "Cart",
    "Checkout",
}


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "inventory" not in st.session_state:
    st.session_state.inventory = {
        product["id"]: product["stock"]
        for product in PRODUCTS
    }

if "order_confirmed" not in st.session_state:
    st.session_state.order_confirmed = False


# ============================================================
# HELPERS
# ============================================================

def find_product(product_id):
    """Return a product by ID."""
    return next(
        (
            product
            for product in PRODUCTS
            if product["id"] == product_id
        ),
        None,
    )


def format_price(value):
    """Return a consistent currency format."""
    return f"${value:,.2f}"


def image_exists(path):
    """Safely check whether an image exists."""
    return Path(path).is_file()


def cart_count():
    """Return total number of products in cart."""
    return sum(
        quantity
        for quantity in st.session_state.cart.values()
        if isinstance(quantity, int) and quantity > 0
    )


def total_price():
    """Calculate cart total."""
    total = 0.0

    for product_id, quantity in st.session_state.cart.items():
        product = find_product(product_id)

        if product is None:
            continue

        if not isinstance(quantity, int) or quantity < 1:
            continue

        total += product["price"] * quantity

    return total


def go_to(page):
    """Navigate to a valid page."""
    if page not in PAGES:
        return

    st.session_state.page = page
    st.session_state.order_confirmed = False


def add_to_cart(product_id, quantity):
    """Reserve inventory and add a product to the cart."""
    product = find_product(product_id)

    if product is None:
        st.error("This product is no longer available.")
        return False

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        st.error("Invalid quantity.")
        return False

    if quantity < 1:
        st.error("Quantity must be at least 1.")
        return False

    available = st.session_state.inventory.get(
        product_id,
        0,
    )

    if quantity > available:
        st.error(
            f"Only {available} unit(s) of "
            f"{product['name']} are available."
        )
        return False

    st.session_state.inventory[product_id] = (
        available - quantity
    )

    st.session_state.cart[product_id] = (
        st.session_state.cart.get(product_id, 0)
        + quantity
    )

    return True


def remove_from_cart(product_id):
    """Remove a product and release its reserved stock."""
    quantity = st.session_state.cart.pop(
        product_id,
        0,
    )

    if quantity > 0:
        st.session_state.inventory[product_id] = (
            st.session_state.inventory.get(product_id, 0)
            + quantity
        )


def update_cart_quantity(product_id, new_quantity):
    """Safely update quantity while maintaining inventory."""
    product = find_product(product_id)

    if product is None:
        st.error("This product is no longer available.")
        return False

    current_quantity = st.session_state.cart.get(
        product_id,
        0,
    )

    try:
        new_quantity = int(new_quantity)
    except (TypeError, ValueError):
        st.error("Invalid quantity.")
        return False

    if current_quantity < 1:
        return False

    if new_quantity < 1:
        remove_from_cart(product_id)
        return True

    difference = new_quantity - current_quantity

    if difference > 0:
        available = st.session_state.inventory.get(
            product_id,
            0,
        )

        if difference > available:
            st.error(
                f"Only {available} additional "
                f"unit(s) are available."
            )
            return False

        st.session_state.inventory[product_id] = (
            available - difference
        )

    elif difference < 0:
        st.session_state.inventory[product_id] = (
            st.session_state.inventory.get(
                product_id,
                0,
            )
            + abs(difference)
        )

    st.session_state.cart[product_id] = new_quantity

    return True


def normalize_phone(phone):
    """Keep phone validation intentionally simple."""
    return re.sub(r"[^\d+]", "", phone)


def valid_email(email):
    """Basic email validation."""
    if not email:
        return True

    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email,
        )
    )


# ============================================================
# DESIGN SYSTEM
# ============================================================

st.markdown(
    """
<style>

:root {
    --bg: #f7f7f5;
    --surface: #ffffff;
    --surface-soft: #f1f1ee;

    --text: #18181b;
    --text-secondary: #52525b;
    --text-muted: #71717a;

    --border: #e4e4e7;
    --border-strong: #d4d4d8;

    --primary: #18181b;
    --primary-hover: #27272a;

    --success: #166534;
    --warning: #92400e;
    --danger: #b91c1c;

    --radius-sm: 10px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-xl: 28px;

    --shadow-sm: 0 4px 16px rgba(24, 24, 27, 0.05);
    --shadow-md: 0 12px 32px rgba(24, 24, 27, 0.07);
    --shadow-lg: 0 20px 50px rgba(24, 24, 27, 0.10);
}

html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

.block-container {
    width: 100%;
    max-width: 1240px;
    padding-top: 1rem;
    padding-bottom: 4rem;
}

#MainMenu, footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}

.nav-shell {
    position: sticky;
    top: 0.5rem;
    z-index: 100;
    display: flex;
    align-items: center;
    min-height: 66px;
    margin-bottom: 14px;
    padding: 10px 14px;
    border: 1px solid rgba(228, 228, 231, 0.95);
    border-radius: var(--radius-lg);
    background: rgba(255, 255, 255, 0.96);
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(18px);
}

.brand {
    display: flex;
    align-items: center;
    gap: 11px;
}

.brand-mark {
    width: 40px;
    height: 40px;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    border-radius: 12px;
    background: var(--primary);
    color: white;
    font-size: 1rem;
    font-weight: 800;
}

.brand-name {
    font-size: 1rem;
    font-weight: 800;
    line-height: 1.2;
}

.nav-caption {
    color: var(--text-muted);
    font-size: 0.75rem;
    line-height: 1.4;
}

.nav-cart {
    margin-left: auto;
    padding: 8px 12px;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: var(--surface-soft);
    color: var(--text-secondary);
    font-size: 0.78rem;
    font-weight: 700;
}

.nav-buttons {
    margin-bottom: 34px;
}

.stButton > button {
    min-height: 44px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    font-size: 0.88rem;
    font-weight: 700;
    transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease, background 0.16s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    border-color: var(--border-strong);
    box-shadow: 0 7px 18px rgba(24, 24, 27, 0.09);
}

.hero {
    position: relative;
    overflow: hidden;
    padding: clamp(34px, 6vw, 58px) clamp(24px, 5vw, 48px);
    margin-bottom: 42px;
    border-radius: var(--radius-xl);
    background: radial-gradient(circle at 85% 20%, rgba(255,255,255,.12), transparent 25%), linear-gradient(120deg, #111113, #29292c);
    color: white;
    box-shadow: var(--shadow-lg);
}

.hero-eyebrow {
    margin-bottom: 13px;
    color: #d4d4d8;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.hero h1 {
    max-width: 800px;
    margin: 0;
    color: white;
    font-size: clamp(2.4rem, 7vw, 4.8rem);
    line-height: 0.98;
    letter-spacing: -0.055em;
}

.hero p {
    max-width: 650px;
    margin: 20px 0 0;
    color: #d4d4d8;
    font-size: 1rem;
    line-height: 1.7;
}

.hero-cta-text {
    display: inline-flex;
    margin-top: 26px;
    padding: 9px 13px;
    border: 1px solid rgba(255,255,255,.18);
    border-radius: 999px;
    background: rgba(255,255,255,.08);
    color: #f4f4f5;
    font-size: 0.8rem;
    font-weight: 700;
}

.section-title {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 18px;
}

.section-title h2 {
    margin: 0;
    color: var(--text);
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.035em;
}

.section-title span {
    color: var(--text-muted);
    font-size: 0.82rem;
}

.product-name {
    margin-top: 14px;
    color: var(--text);
    font-size: 1.02rem;
    font-weight: 800;
    line-height: 1.3;
}

.category {
    display: inline-flex;
    margin-top: 7px;
    padding: 4px 9px;
    border-radius: 999px;
    background: var(--surface-soft);
    color: var(--text-secondary);
    font-size: 0.7rem;
    font-weight: 800;
}

.price {
    margin-top: 12px;
    color: var(--text);
    font-size: 1.15rem;
    font-weight: 800;
}

.product-desc {
    min-height: 43px;
    margin: 9px 0 12px;
    color: var(--text-muted);
    font-size: 0.83rem;
    line-height: 1.55;
}

.stock {
    margin-bottom: 10px;
    color: var(--text-secondary);
    font-size: 0.76rem;
    font-weight: 600;
}

.stock.low {
    color: var(--warning);
    font-weight: 800;
}

.stock.out {
    color: var(--danger);
    font-weight: 800;
}

.page-title {
    margin-bottom: 28px;
}

.page-title h2 {
    margin: 0;
    color: var(--text);
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.04em;
}

.page-title p {
    margin: 7px 0 0;
    color: var(--text-muted);
    font-size: 0.88rem;
    line-height: 1.5;
}

.card-heading {
    margin: 0;
    color: var(--text);
    font-size: 1.15rem;
    font-weight: 800;
}

.card-description {
    margin: 5px 0 20px;
    color: var(--text-muted);
    font-size: 0.82rem;
    line-height: 1.5;
}

.cart-item {
    padding: 17px 0;
    border-bottom: 1px solid #f0f0f2;
}

.item-name {
    color: var(--text);
    font-size: 0.94rem;
    font-weight: 800;
}

.item-meta {
    margin-top: 5px;
    color: var(--text-muted);
    font-size: 0.78rem;
    line-height: 1.5;
}

.total-line {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    margin-top: 18px;
    padding-top: 18px;
    border-top: 2px solid var(--border);
    color: var(--text);
    font-size: 1.2rem;
    font-weight: 800;
}

.trust {
    margin-top: 18px;
    padding: 15px;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    background: #fafafa;
}

.trust-title {
    color: var(--text);
    font-size: 0.83rem;
    font-weight: 800;
}

.trust-text {
    margin-top: 5px;
    color: var(--text-muted);
    font-size: 0.76rem;
    line-height: 1.55;
}

.payment-note {
    margin-top: 14px;
    padding: 12px 14px;
    border-radius: var(--radius-md);
    background: var(--surface-soft);
    color: var(--text-muted);
    font-size: 0.76rem;
    line-height: 1.55;
}

.empty-state, .success-state {
    padding: 42px 24px;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface);
    text-align: center;
    box-shadow: var(--shadow-sm);
}

.footer {
    margin-top: 60px;
    padding: 25px 0 5px;
    border-top: 1px solid var(--border);
    color: var(--text-muted);
    text-align: center;
    font-size: 0.76rem;
    line-height: 1.7;
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION HEADER
# ============================================================

current_cart_count = cart_count()

st.markdown(
    f"""
    <header class="nav-shell">
        <div class="brand">
            <div class="brand-mark">S</div>
            <div>
                <div class="brand-name">ShamIn Store</div>
                <div class="nav-caption">Curated Home Decor</div>
            </div>
        </div>
        <div class="nav-cart">
            🛒 {current_cart_count} item(s)
        </div>
    </header>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MAIN NAVIGATION
# ============================================================

nav_home, nav_cart, nav_checkout = st.columns(
    [1, 1, 1],
    gap="small",
)

with nav_home:
    if st.button(
        "🏠 Home",
        key="nav_home",
        use_container_width=True,
    ):
        go_to("Home")
        st.rerun()

with nav_cart:
    if st.button(
        f"🛒 Cart · {current_cart_count}",
        key="nav_cart",
        use_container_width=True,
    ):
        go_to("Cart")
        st.rerun()

with nav_checkout:
    if st.button(
        "Checkout →",
        key="nav_checkout",
        use_container_width=True,
        type="primary",
        disabled=not st.session_state.cart,
    ):
        go_to("Checkout")
        st.rerun()

st.markdown(
    '<div class="nav-buttons"></div>',
    unsafe_allow_html=True,
)


# ============================================================
# HOME
# ============================================================

if st.session_state.page == "Home":

    st.markdown(
        """
        <section class="hero">
            <div class="hero-eyebrow">
                Curated Home Collection
            </div>
            <h1>
                Make your space<br>
                feel like home.
            </h1>
            <p>
                Discover elegant decor pieces designed to bring
                warmth, character, and a refined touch to every room.
            </p>
            <div class="hero-cta-text">
                ↓ Explore the collection below
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-title">
            <h2>Featured Collection</h2>
            <span>Thoughtfully selected for your home</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    search_col, category_col = st.columns(
        [2, 1],
        gap="medium",
    )

    with search_col:
        search = st.text_input(
            "Search products",
            placeholder="🔎 Search by name, category, or description...",
            label_visibility="collapsed",
            key="product_search",
        )

    categories = ["All"] + sorted(
        {
            product["cat"]
            for product in PRODUCTS
        }
    )

    with category_col:
        selected_category = st.selectbox(
            "Category",
            categories,
            label_visibility="collapsed",
            key="product_category",
        )

    query = search.strip().lower()
    filtered_products = []

    for product in PRODUCTS:
        searchable_text = " ".join(
            [
                product["name"],
                product["cat"],
                product["desc"],
            ]
        ).lower()

        matches_search = (
            not query
            or query in searchable_text
        )

        matches_category = (
            selected_category == "All"
            or product["cat"] == selected_category
        )

        if matches_search and matches_category:
            filtered_products.append(product)

    if not filtered_products:
        st.info(
            "No products found. "
            "Try another search or category."
        )
    else:
        st.caption(
            f"{len(filtered_products)} product(s) found"
        )

        for start in range(
            0,
            len(filtered_products),
            4,
        ):
            row = filtered_products[start:start + 4]
            columns = st.columns(
                len(row),
                gap="medium",
            )

            for column, product in zip(columns, row):
                with column:
                    # FIXED: Removed unsupported `key` parameter from st.container()
                    with st.container(border=True):

                        image_path = product["img"]

                        if image_exists(image_path):
                            # FIXED: Replaced invalid `width="stretch"` with `use_container_width=True`
                            st.image(
                                image_path,
                                use_container_width=True,
                            )
                        else:
                            st.markdown(
                                """
                                <div class="image-placeholder" style="width:100%; min-height:190px; display:grid; place-items:center; border-radius:14px; background:#f1f1ee; color:#71717a; text-align:center; font-size:0.82rem;">
                                    🖼️<br>Product image unavailable
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        st.markdown(
                            f"""
                            <div class="product-name">
                                {escape(product["name"])}
                            </div>
                            <span class="category">
                                {escape(product["cat"])}
                            </span>
                            <div class="price">
                                {format_price(product["price"])}
                            </div>
                            <div class="product-desc">
                                {escape(product["desc"])}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        available = st.session_state.inventory.get(
                            product["id"],
                            0,
                        )

                        if available <= 0:
                            stock_class = "out"
                            stock_text = "Sold out"
                        elif available <= 4:
                            stock_class = "low"
                            stock_text = f"Only {available} unit(s) left"
                        else:
                            stock_class = ""
                            stock_text = f"{available} unit(s) available"

                        st.markdown(
                            f"""
                            <div class="stock {stock_class}">
                                📦 {stock_text}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if available > 0:
                            quantity = st.number_input(
                                "Quantity",
                                min_value=1,
                                max_value=available,
                                value=1,
                                step=1,
                                key=f"quantity_{product['id']}",
                            )
                        else:
                            quantity = 1
                            st.number_input(
                                "Quantity",
                                min_value=1,
                                max_value=1,
                                value=1,
                                disabled=True,
                                key=f"quantity_{product['id']}",
                            )

                        if st.button(
                            "Add to Cart · 🛒",
                            key=f"add_to_cart_{product['id']}",
                            use_container_width=True,
                            type="primary",
                            disabled=available <= 0,
                        ):
                            if add_to_cart(product["id"], quantity):
                                st.toast(
                                    f"{product['name']} added to your cart.",
                                    icon="✅",
                                )
                                st.rerun()


# ============================================================
# CART
# ============================================================

elif st.session_state.page == "Cart":

    st.markdown(
        """
        <div class="page-title">
            <h2>Your Shopping Cart</h2>
            <p>Review your selected pieces before continuing.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.cart:
        st.markdown(
            """
            <section class="empty-state">
                <h3>Your cart is empty.</h3>
                <p>Browse the collection and add something you like.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button(
            "← Browse Collection",
            key="browse_collection_empty",
            type="primary",
        ):
            go_to("Home")
            st.rerun()

    else:
        # FIXED: Removed unsupported `key` parameter from st.container()
        with st.container(border=True):

            invalid_products = [
                product_id
                for product_id in st.session_state.cart
                if find_product(product_id) is None
            ]

            for product_id in invalid_products:
                st.session_state.cart.pop(product_id, None)

            for product_id, quantity in list(st.session_state.cart.items()):
                product = find_product(product_id)
                if product is None:
                    continue

                subtotal = product["price"] * quantity

                st.markdown(
                    f"""
                    <div class="cart-item">
                        <div class="item-name">
                            {escape(product["name"])}
                        </div>
                        <div class="item-meta">
                            {escape(product["cat"])} · {format_price(product["price"])} each
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                quantity_col, total_col, remove_col = st.columns(
                    [2, 1, 1],
                    gap="small",
                )

                with quantity_col:
                    available_to_add = st.session_state.inventory.get(product_id, 0)
                    max_quantity = quantity + available_to_add

                    new_quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        max_value=max_quantity,
                        value=quantity,
                        step=1,
                        key=f"cart_quantity_{product_id}",
                    )

                    if new_quantity != quantity:
                        if update_cart_quantity(product_id, new_quantity):
                            st.rerun()

                with total_col:
                    st.markdown(
                        f"""
                        <div style="padding-top: 8px; font-weight: 800;">
                            {format_price(subtotal)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with remove_col:
                    if st.button(
                        "Remove",
                        key=f"remove_{product_id}",
                        use_container_width=True,
                    ):
                        remove_from_cart(product_id)
                        st.rerun()

            st.markdown(
                f"""
                <div class="total-line">
                    <span>Total</span>
                    <span>{format_price(total_price())}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")

        action_left, action_right = st.columns(2, gap="medium")

        with action_left:
            if st.button(
                "← Continue Shopping",
                key="continue_shopping",
                use_container_width=True,
            ):
                go_to("Home")
                st.rerun()

        with action_right:
            if st.button(
                "Continue to Checkout →",
                key="continue_checkout",
                use_container_width=True,
                type="primary",
            ):
                go_to("Checkout")
                st.rerun()


# ============================================================
# CHECKOUT
# ============================================================

elif st.session_state.page == "Checkout":

    st.markdown(
        """
        <div class="page-title">
            <h2>Complete Your Order</h2>
            <p>Enter your contact and delivery information.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.order_confirmed:
        st.markdown(
            """
            <section class="success-state">
                <h3>Order request received 🎉</h3>
                <p>Your order information has been recorded for this demo.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button(
            "← Continue Shopping",
            key="success_continue",
            type="primary",
        ):
            go_to("Home")
            st.rerun()

    elif not st.session_state.cart:
        st.info("Your cart is empty. Add a product before checkout.")
        if st.button(
            "Browse Collection",
            key="checkout_browse",
            type="primary",
        ):
            go_to("Home")
            st.rerun()

    else:
        left, right = st.columns([1.25, 1], gap="large")

        with left:
            # FIXED: Removed unsupported `key` parameter from st.container()
            with st.container(border=True):
                st.markdown(
                    """
                    <div class="card-heading">Order Summary</div>
                    <div class="card-description">A clear breakdown of your order.</div>
                    """,
                    unsafe_allow_html=True,
                )

                for product_id, quantity in st.session_state.cart.items():
                    product = find_product(product_id)
                    if product is None:
                        continue

                    subtotal = product["price"] * quantity

                    st.markdown(
                        f"""
                        <div class="cart-item">
                            <div class="item-name">{escape(product["name"])}</div>
                            <div class="item-meta">{quantity} × {format_price(product["price"])}</div>
                            <div class="item-total">{format_price(subtotal)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"""
                    <div class="total-line">
                        <span>Final Total</span>
                        <span>{format_price(total_price())}</span>
                    </div>
                    <div class="trust">
                        <div class="trust-title">📦 Order & Delivery</div>
                        <div class="trust-text">
                            Delivery details will be confirmed with you after the order request.
                        </div>
                    </div>
                    <div class="payment-note">
                        Payment is not processed by this demo. No card details are collected.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with right:
            # FIXED: Removed unsupported `key` parameter from st.container()
            with st.container(border=True):
                st.markdown(
                    """
                    <div class="card-heading">Customer Details</div>
                    <div class="card-description">Enter the information required for your order.</div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.form("checkout_form", clear_on_submit=False):
                    name = st.text_input("Full Name *", placeholder="Your full name")
                    phone = st.text_input("Phone Number *", placeholder="Your phone number")
                    email = st.text_input("Email Address", placeholder="you@example.com")
                    address = st.text_area("Delivery Address *", placeholder="Your complete delivery address", height=120)

                    st.markdown(
                        """
                        <div class="trust">
                            <div class="trust-title">💬 Need help?</div>
                            <div class="trust-text">
                                Make sure your contact and delivery information is correct before submitting.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    submitted = st.form_submit_button(
                        "Place Order Request →",
                        use_container_width=True,
                        type="primary",
                    )

                if submitted:
                    clean_name = name.strip()
                    clean_phone = normalize_phone(phone.strip())
                    clean_email = email.strip()
                    clean_address = address.strip()

                    errors = []

                    if not clean_name:
                        errors.append("Full name is required.")
                    if not clean_phone:
                        errors.append("Phone number is required.")
                    elif len(clean_phone) < 7 or len(clean_phone) > 16:
                        errors.append("Please enter a valid phone number.")
                    if not clean_address:
                        errors.append("Delivery address is required.")
                    if not valid_email(clean_email):
                        errors.append("Please enter a valid email address.")

                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        st.session_state.cart = {}
                        st.session_state.order_confirmed = True
                        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <footer class="footer">
        © 2026 ShamIn Store · Curated Home Decor
        <br>
        Simple shopping experience for the demo.
        <br>
        Made by BoZaher (rateb).
    </footer>
    """,
    unsafe_allow_html=True,
)
