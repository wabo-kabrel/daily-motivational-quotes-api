from app import db

class Quote(db.Model):
    __tablename__ = "quotes"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Quote {self.id} - {self.author}>"
