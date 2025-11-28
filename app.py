from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

# Configuración de MongoDB
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://peraltabautistaanalicbtis272_db_user:admin12345@glamour.diwxvux.mongodb.net/glamour")

try:
    client = MongoClient(MONGO_URI)
    db = client.glamourlife
    print("✅ Conexión establecida con MongoDB")
except Exception as e:
    print(f"❌ Error al conectar con MongoDB: {e}")
    db = None

# Configuración para subir imágenes
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'avif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Crear datos de ejemplo si la base de datos está vacía
def create_sample_data():
    if db is None:
        return
    
    # Verificar si ya existen productos
    if db.productos.count_documents({}) == 0:
        sample_products = [
            {
                "nombre": "Shampoo Hidratante Pantene",
                "descripcion": "Shampoo con consistencia cremosa, fragancia agradable y capacidad de limpieza profunda sin resecar",
                "precio": 103.05,
                "categoria": "cabello",
                "imagen": "shampoo-pantene.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Acondicionador Reparador",
                "descripcion": "Acondicionador que repara puntas abiertas y da brillo al cabello",
                "precio": 95.50,
                "categoria": "cabello",
                "imagen": "acondicionador-reparador.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Crema para Peinar",
                "descripcion": "Crema que facilita el peinado y controla el frizz",
                "precio": 120.00,
                "categoria": "cabello",
                "imagen": "crema-peinar.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Mascarilla Capilar",
                "descripcion": "Tratamiento intensivo para cabello dañado",
                "precio": 150.75,
                "categoria": "cabello",
                "imagen": "mascarilla-capilar.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Base de Maquillaje Líquida",
                "descripcion": "Base de larga duración con acabado natural",
                "precio": 245.00,
                "categoria": "maquillaje",
                "imagen": "base-maquillaje.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Paleta de Sombras",
                "descripcion": "Paleta con 12 tonos mates y brillantes",
                "precio": 320.50,
                "categoria": "maquillaje",
                "imagen": "paleta-sombras.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Labial Líquido Mate",
                "descripcion": "Labial de larga duración con acabado mate",
                "precio": 180.00,
                "categoria": "maquillaje",
                "imagen": "labial-mate.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Rímel a Prueba de Agua",
                "descripcion": "Rímel que no se corre con el agua",
                "precio": 135.25,
                "categoria": "maquillaje",
                "imagen": "rimel-agua.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Crema Hidratante Facial",
                "descripcion": "Hidratante diaria para todo tipo de piel",
                "precio": 280.00,
                "categoria": "piel",
                "imagen": "crema-facial.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Protector Solar FPS 50",
                "descripcion": "Protección solar de amplio espectro",
                "precio": 195.75,
                "categoria": "piel",
                "imagen": "protector-solar.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Serum Antiedad",
                "descripcion": "Serum con retinol para reducir líneas de expresión",
                "precio": 420.00,
                "categoria": "piel",
                "imagen": "serum-antiedad.jpg",
                "fecha_creacion": datetime.now()
            },
            {
                "nombre": "Limpiador Facial",
                "descripcion": "Gel limpiador que remueve impurezas",
                "precio": 160.50,
                "categoria": "piel",
                "imagen": "limpiador-facial.jpg",
                "fecha_creacion": datetime.now()
            }
        ]
        
        db.productos.insert_many(sample_products)
        print("✅ Datos de ejemplo creados")

# Rutas de la aplicación
@app.route("/")
def index():
    if db is not None:
        productos_destacados = list(db.productos.find().limit(4))
    else:
        productos_destacados = []
    
    return render_template("index.html", productos_destacados=productos_destacados)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        telefono = request.form.get("telefono", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not all([nombre, email, telefono, password, confirm_password]):
            flash("Completa todos los campos.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for("register"))

        if db is not None:
            if db.usuarios.find_one({"email": email}):
                flash("Este correo electrónico ya está registrado.", "danger")
                return redirect(url_for("register"))

            db.usuarios.insert_one({
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "password": generate_password_hash(password),
                "fecha_registro": datetime.now()
            })
            flash("✅ Registro exitoso. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
        else:
            flash("❌ Error: Base de datos no conectada.", "danger")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Completa todos los campos.", "danger")
            return redirect(url_for("login"))

        if db is not None:
            usuario = db.usuarios.find_one({"email": email})
            if usuario and check_password_hash(usuario["password"], password):
                session["user_id"] = str(usuario["_id"])
                session["user_name"] = usuario["nombre"]
                flash(f"👋 Bienvenido/a {usuario['nombre']}", "success")
                return redirect(url_for("products"))
            else:
                flash("❌ Credenciales incorrectas.", "danger")
        else:
            flash("❌ Error: Base de datos no conectada.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("🔒 Sesión cerrada correctamente.", "info")
    return redirect(url_for("index"))

@app.route("/products")
def products():
    categoria = request.args.get("categoria", "")
    
    if db is not None:
        filtro = {}
        if categoria:
            filtro = {"categoria": categoria}
        
        productos = list(db.productos.find(filtro))
    else:
        productos = []
        flash("❌ Error: Base de datos no conectada.", "danger")
    
    return render_template("products.html", productos=productos, categoria=categoria)

@app.route("/product/<id>")
def product_detail(id):
    if db is None:
        flash("❌ Error: Base de datos no conectada.", "danger")
        return redirect(url_for("products"))
    
    producto = db.productos.find_one({"_id": ObjectId(id)})
    if not producto:
        flash("⚠️ Producto no encontrado.", "warning")
        return redirect(url_for("products"))
    
    return render_template("product_detail.html", producto=producto)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión"})
    
    product_id = request.form.get("product_id")
    cantidad = int(request.form.get("cantidad", 1))
    
    if db is None:
        return jsonify({"success": False, "message": "Error de base de datos"})
    
    producto = db.productos.find_one({"_id": ObjectId(product_id)})
    if not producto:
        return jsonify({"success": False, "message": "Producto no encontrado"})
    
    if "cart" not in session:
        session["cart"] = {}
    
    cart = session["cart"]
    
    if product_id in cart:
        cart[product_id]["cantidad"] += cantidad
    else:
        cart[product_id] = {
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "imagen": producto.get("imagen", ""),
            "cantidad": cantidad
        }
    
    session["cart"] = cart
    session.modified = True
    
    return jsonify({
        "success": True, 
        "message": "🛒 Producto agregado al carrito",
        "cart_count": sum(item["cantidad"] for item in cart.values())
    })

@app.route("/update_cart", methods=["POST"])
def update_cart():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión"})
    
    product_id = request.form.get("product_id")
    cantidad = int(request.form.get("cantidad", 1))
    
    if "cart" not in session:
        return jsonify({"success": False, "message": "Carrito vacío"})
    
    cart = session["cart"]
    
    if product_id in cart:
        if cantidad <= 0:
            del cart[product_id]
        else:
            cart[product_id]["cantidad"] = cantidad
        
        session["cart"] = cart
        session.modified = True
        
        return jsonify({
            "success": True, 
            "message": "Carrito actualizado",
            "cart_count": sum(item["cantidad"] for item in cart.values())
        })
    else:
        return jsonify({"success": False, "message": "Producto no encontrado en el carrito"})

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión"})
    
    product_id = request.form.get("product_id")
    
    if "cart" not in session:
        return jsonify({"success": False, "message": "Carrito vacío"})
    
    cart = session["cart"]
    
    if product_id in cart:
        del cart[product_id]
        session["cart"] = cart
        session.modified = True
        
        return jsonify({
            "success": True, 
            "message": "🗑️ Producto eliminado del carrito",
            "cart_count": sum(item["cantidad"] for item in cart.values())
        })
    else:
        return jsonify({"success": False, "message": "Producto no encontrado en el carrito"})

@app.route("/cart")
def cart():
    if "user_id" not in session:
        flash("🔒 Debes iniciar sesión para ver el carrito.", "warning")
        return redirect(url_for("login"))
    
    cart_items = []
    total = 0
    
    if "cart" in session:
        for product_id, item in session["cart"].items():
            if db is not None:
                producto = db.productos.find_one({"_id": ObjectId(product_id)})
                if producto:
                    subtotal = item["precio"] * item["cantidad"]
                    total += subtotal
                    
                    cart_items.append({
                        "id": product_id,
                        "nombre": item["nombre"],
                        "precio": item["precio"],
                        "imagen": item["imagen"],
                        "cantidad": item["cantidad"],
                        "subtotal": subtotal
                    })
    
    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route("/checkout")
def checkout():
    if "user_id" not in session:
        flash("🔒 Debes iniciar sesión para realizar una compra.", "warning")
        return redirect(url_for("login"))
    
    if "cart" not in session or not session["cart"]:
        flash("🛒 Tu carrito está vacío.", "warning")
        return redirect(url_for("products"))
    
    total = 0
    if "cart" in session:
        for item in session["cart"].values():
            total += item["precio"] * item["cantidad"]
    
    return render_template("checkout.html", total=total)

@app.route("/payment", methods=["POST"])
def payment():
    if "user_id" not in session:
        flash("🔒 Debes iniciar sesión para realizar una compra.", "warning")
        return redirect(url_for("login"))
    
    if "cart" not in session or not session["cart"]:
        flash("🛒 Tu carrito está vacío.", "warning")
        return redirect(url_for("products"))
    
    # Procesar el pago (simulado)
    if db is not None:
        cart_items = []
        total = 0
        
        for product_id, item in session["cart"].items():
            subtotal = item["precio"] * item["cantidad"]
            total += subtotal
            
            cart_items.append({
                "producto_id": ObjectId(product_id),
                "nombre": item["nombre"],
                "precio": item["precio"],
                "cantidad": item["cantidad"],
                "subtotal": subtotal
            })
        
        pedido = {
            "usuario_id": ObjectId(session["user_id"]),
            "items": cart_items,
            "total": total,
            "fecha": datetime.now(),
            "estado": "completado"
        }
        
        db.pedidos.insert_one(pedido)
        
        # Vaciar carrito
        session["cart"] = {}
        session.modified = True
        
        return render_template("payment.html")
    else:
        flash("❌ Error: Base de datos no conectada.", "danger")
        return redirect(url_for("cart"))

# Rutas de administración
@app.route("/admin/products")
def admin_products():
    if "user_id" not in session:
        flash("🔒 Debes iniciar sesión para acceder al panel de administración.", "warning")
        return redirect(url_for("login"))
    
    if db is None:
        flash("❌ Error: Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    
    productos = list(db.productos.find())
    return render_template("admin_products.html", productos=productos)

@app.route("/admin/product/new", methods=["GET", "POST"])
def admin_new_product():
    if "user_id" not in session:
        flash("🔒 Debes iniciar sesión para acceder al panel de administración.", "warning")
        return redirect(url_for("login"))
    
    if db is None:
        flash("❌ Error: Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        precio = float(request.form.get("precio", 0))
        categoria = request.form.get("categoria", "").strip()
        
        if not nombre or not descripcion or precio <= 0 or not categoria:
            flash("❌ Completa todos los campos correctamente.", "danger")
            return redirect(url_for("admin_new_product"))
        
        # Manejar la imagen
        imagen = ""
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                imagen = unique_filename
        
        producto = {
            "nombre": nombre,
            "descripcion": descripcion,
            "precio": precio,
            "categoria": categoria,
            "imagen": imagen,
            "fecha_creacion": datetime.now()
        }
        
        db.productos.insert_one(producto)
        flash("✅ Producto creado correctamente.", "success")
        return redirect(url_for("admin_products"))
    
    return render_template("admin_product_form.html", producto=None)

@app.route("/admin/product/edit/<id>", methods=["GET", "POST"])
def admin_edit_product(id):
    if "user_id" not in session:
        flash("🔒 Debes iniciar sesión para acceder al panel de administración.", "warning")
        return redirect(url_for("login"))
    
    if db is None:
        flash("❌ Error: Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    
    producto = db.productos.find_one({"_id": ObjectId(id)})
    if not producto:
        flash("⚠️ Producto no encontrado.", "warning")
        return redirect(url_for("admin_products"))
    
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        precio = float(request.form.get("precio", 0))
        categoria = request.form.get("categoria", "").strip()
        
        if not nombre or not descripcion or precio <= 0 or not categoria:
            flash("❌ Completa todos los campos correctamente.", "danger")
            return redirect(url_for("admin_edit_product", id=id))
        
        # Manejar la imagen
        imagen = producto.get("imagen", "")
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                # Eliminar imagen anterior si existe
                if imagen and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], imagen)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], imagen))
                
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                imagen = unique_filename
        
        db.productos.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": precio,
                "categoria": categoria,
                "imagen": imagen
            }}
        )
        flash("✅ Producto actualizado correctamente.", "success")
        return redirect(url_for("admin_products"))
    
    return render_template("admin_product_form.html", producto=producto)

@app.route("/admin/product/delete/<id>", methods=["POST"])
def admin_delete_product(id):
    if "user_id" not in session:
        flash("🔒 Debes iniciar sesión para acceder al panel de administración.", "warning")
        return redirect(url_for("login"))
    
    if db is None:
        flash("❌ Error: Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    
    producto = db.productos.find_one({"_id": ObjectId(id)})
    if producto:
        # Eliminar imagen si existe
        if producto.get("imagen") and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], producto["imagen"])):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], producto["imagen"]))
        
        db.productos.delete_one({"_id": ObjectId(id)})
        flash("🗑️ Producto eliminado correctamente.", "success")
    else:
        flash("⚠️ Producto no encontrado.", "warning")
    
    return redirect(url_for("admin_products"))

# API para obtener información del carrito
@app.route("/api/cart_count")
def api_cart_count():
    count = 0
    if "cart" in session:
        count = sum(item["cantidad"] for item in session["cart"].values())
    return jsonify({"count": count})

if __name__ == "__main__":
    # Crear carpeta de uploads si no existe
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Crear datos de ejemplo
    create_sample_data()
    

    app.run(debug=True)
