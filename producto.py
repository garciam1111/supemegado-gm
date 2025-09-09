from app import db

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

    # Relación con Categoría
    categoria = db.relationship('Categoria', backref=db.backref('productos', lazy=True))

    def __repr__(self):
        return f'<Producto {self.nombre}>'