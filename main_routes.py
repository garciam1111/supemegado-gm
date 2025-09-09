from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.producto import Producto
from app.models.categoria import Categoria
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Usuario.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('main.index'))
        flash('Correo o contraseña incorrectos', 'error')
    return render_template('login.html')

@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            password = request.form['password']
            if Usuario.query.filter_by(email=email).first():
                flash('El correo ya está registrado', 'error')
                return redirect(url_for('main.registro'))
            user = Usuario(
                nombre=nombre,
                email=email,
                password_hash=generate_password_hash(password),
                rol='cliente'
            )
            db.session.add(user)
            db.session.commit()
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            flash(f'Error al registrarse: {str(e)}', 'error')
            db.session.rollback()
    return render_template('registro.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'success')
    return redirect(url_for('main.index'))

@bp.route('/productos')
def productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)

@bp.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    if current_user.rol != 'admin':
        flash('Acceso denegado: Solo administradores pueden crear productos.', 'error')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            precio = float(request.form['precio'])
            stock = int(request.form['stock'])
            categoria_id = int(request.form['categoria_id'])
            descripcion = request.form.get('descripcion', '')
            producto = Producto(
                nombre=nombre,
                precio=precio,
                stock=stock,
                categoria_id=categoria_id,
                descripcion=descripcion
            )
            db.session.add(producto)
            db.session.commit()
            flash('Producto creado con éxito', 'success')
            return redirect(url_for('main.productos'))
        except ValueError as e:
            flash('Error en los datos ingresados. Verifica los campos.', 'error')
        except Exception as e:
            flash(f'Error al crear el producto: {str(e)}', 'error')
            db.session.rollback()
    categorias = Categoria.query.all()
    return render_template('nuevo_producto.html', categorias=categorias)

@bp.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    if current_user.rol != 'admin':
        flash('Acceso denegado: Solo administradores pueden editar productos.', 'error')
        return redirect(url_for('main.index'))
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        try:
            producto.nombre = request.form['nombre']
            producto.precio = float(request.form['precio'])
            producto.stock = int(request.form['stock'])
            producto.categoria_id = int(request.form['categoria_id'])
            producto.descripcion = request.form.get('descripcion', '')
            db.session.commit()
            flash('Producto actualizado con éxito', 'success')
            return redirect(url_for('main.productos'))
        except ValueError as e:
            flash('Error en los datos ingresados. Verifica los campos.', 'error')
        except Exception as e:
            flash(f'Error al actualizar el producto: {str(e)}', 'error')
            db.session.rollback()
    categorias = Categoria.query.all()
    return render_template('editar_producto.html', producto=producto, categorias=categorias)

@bp.route('/productos/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    if current_user.rol != 'admin':
        flash('Acceso denegado: Solo administradores pueden eliminar productos.', 'error')
        return redirect(url_for('main.index'))
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado con éxito', 'success')
    except Exception as e:
        flash(f'Error al eliminar el producto: {str(e)}', 'error')
        db.session.rollback()
    return redirect(url_for('main.productos'))

@bp.route('/categorias')
def categorias():
    categorias = Categoria.query.all()
    return render_template('categorias.html', categorias=categorias)

@bp.route('/categorias/nuevo', methods=['GET', 'POST'])
@login_required
def nueva_categoria():
    if current_user.rol != 'admin':
        flash('Acceso denegado: Solo administradores pueden crear categorías.', 'error')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form.get('descripcion', '')
            categoria = Categoria(nombre=nombre, descripcion=descripcion)
            db.session.add(categoria)
            db.session.commit()
            flash('Categoría creada con éxito', 'success')
            return redirect(url_for('main.categorias'))
        except Exception as e:
            flash(f'Error al crear la categoría: {str(e)}', 'error')
            db.session.rollback()
    return render_template('nueva_categoria.html')

@bp.route('/pedidos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_pedido():
    if request.method == 'POST':
        try:
            productos_ids = request.form.getlist('producto_id')
            cantidades = request.form.getlist('cantidad')
            if not productos_ids or not cantidades:
                flash('Debes seleccionar al menos un producto.', 'error')
                return redirect(url_for('main.nuevo_pedido'))
            pedido = Pedido(usuario_id=current_user.id, total=0.0)
            db.session.add(pedido)
            db.session.flush()
            total = 0.0
            for prod_id, cantidad in zip(productos_ids, cantidades):
                producto = Producto.query.get(int(prod_id))
                if not producto:
                    flash(f'Producto con ID {prod_id} no encontrado.', 'error')
                    db.session.rollback()
                    return redirect(url_for('main.nuevo_pedido'))
                if int(cantidad) <= 0 or int(cantidad) > producto.stock:
                    flash(f'Cantidad inválida para {producto.nombre}. Stock disponible: {producto.stock}.', 'error')
                    db.session.rollback()
                    return redirect(url_for('main.nuevo_pedido'))
                item = ItemPedido(
                    pedido_id=pedido.id,
                    producto_id=prod_id,
                    cantidad=int(cantidad),
                    precio_unitario=producto.precio
                )
                total += producto.precio * int(cantidad)
                producto.stock -= int(cantidad)
                db.session.add(item)
            pedido.total = total
            db.session.commit()
            flash('Pedido creado con éxito', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f'Error al crear el pedido: {str(e)}', 'error')
            db.session.rollback()
    productos = Producto.query.all()
    return render_template('nuevo_pedido.html', productos=productos)

@bp.route('/pedidos')
@login_required
def pedidos():
    pedidos = Pedido.query.filter_by(usuario_id=current_user.id).all()
    return render_template('pedidos.html', pedidos=pedidos)