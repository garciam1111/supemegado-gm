from app import db

class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

    # Relación con Producto
    producto = db.relationship('Producto', backref=db.backref('items_pedido', lazy=True))

    def __repr__(self):
        return f'<ItemPedido {self.producto.nombre} - Cantidad: {self.cantidad}>'