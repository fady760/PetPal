from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def get_utc_now():
    return datetime.now(timezone.utc)


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)  # e.g., "Dog", "Cat", etc.
    age = Column(Integer, nullable=False)
    is_adopted = Column(Boolean, default=False, nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    def __repr__(self):
        return f"<Pet(id={self.id}, name='{self.name}', species='{self.species}', adopted={self.is_adopted})>"

    @property
    def display_image(self) -> str:
        """Returns the pet's image URL or a curated high-quality placeholder based on species."""
        if self.image_url and self.image_url.strip():
            return self.image_url.strip()
        
        species_lower = (self.species or "").lower()
        if "cat" in species_lower:
            return "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=600&q=80"
        elif "rabbit" in species_lower or "bunny" in species_lower:
            return "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?auto=format&fit=crop&w=600&q=80"
        elif "bird" in species_lower:
            return "https://images.unsplash.com/photo-1552728089-57bdde30beb3?auto=format&fit=crop&w=600&q=80"
        else:
            # Default to adorable dog
            return "https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=600&q=80"
