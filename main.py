from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Simple CRUD API")


# ---------- Schemas ----------
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class Item(ItemCreate):
    id: int


# ---------- In-memory "database" ----------
db: dict[int, Item] = {}
next_id = 1


# ---------- CREATE ----------
@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate):
    global next_id
    item = Item(id=next_id, **payload.model_dump())
    db[next_id] = item
    next_id += 1
    return item


# ---------- READ ----------
@app.get("/items", response_model=list[Item])
def list_items():
    return list(db.values())


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    return db[item_id]


# ---------- UPDATE ----------
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, payload: ItemUpdate):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = db[item_id].model_copy(update=payload.model_dump(exclude_unset=True))
    db[item_id] = updated
    return updated


# ---------- DELETE ----------
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    del db[item_id]
