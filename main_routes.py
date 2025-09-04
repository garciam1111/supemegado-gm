from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.producto import Producto
from app.models.categoria import Categoria
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
from app.models.cliente import Usuario

bp = Blueprint('main', __name__)

# Página principal
@bp.route('/')
def index():
    return render_template('index.html')

# Listar productos
@bp.route('/productos')
def productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)

# Crear producto
@bp.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
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

# Editar producto
@bp.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
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

# Eliminar producto
@bp.route('/productos/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado con éxito', 'success')
    except Exception as e:
        flash(f'Error al eliminar el producto: {str(e)}', 'error')
        db.session.rollback()
    return redirect(url_for('main.productos'))

# Listar categorías
@bp.route('/categorias')
def categorias():
    categorias = Categoria.query.all()
    return render_template('categorias.html', categorias=categorias)

# Crear categoría
@bp.route('/categorias/nuevo', methods=['GET', 'POST'])
def nueva_categoria():
    if request.method == 'POST':
            nombre = request.form['nombre']
            descripcion = request.form.get('descripcion', '')
            categoria = Categoria(nombre=nombre, descripcion=descripcion)
            db.session.add(categoria)
            db.session.commit