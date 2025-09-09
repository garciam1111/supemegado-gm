from app import create_app, db
from app.models.producto import Producto
from app.models.categoria import Categoria
app = create_app()
with app.app_context():
    categoria = Categoria(nombre='Alimentos', descripcion='Productos comestibles')
    db.session.add(categoria)
    db.session.commit()

    producto = Producto(nombre='Leche', precio=2.5, stock=100, categoria_id=categoria.id)
    db.session.add(producto)
    db.session.commit()