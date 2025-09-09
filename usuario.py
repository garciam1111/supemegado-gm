from app import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), default='cliente')  # Ej.: 'cliente', 'admin'

    # Relación con Pedidos
    pedidos = db.relationship('Pedido', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'
    

    