
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="CI Demo API", version="1.0.0")


# In-memory store (for demo purposes)
items: dict[int, dict] = {}
_next_id = 1


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    in_stock: bool = True


class ItemResponse(Item):
    id: int


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI CI Demo", "status": "healthy"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/items", response_model=list[ItemResponse])
def list_items():
    return [ItemResponse(id=k, **v) for k, v in items.items()]


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(id=item_id, **items[item_id])


@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: Item):
    global _next_id
    item_data = item.model_dump()
    items[_next_id] = item_data
    response = ItemResponse(id=_next_id, **item_data)
    _next_id += 1
    return response


@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: Item):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = item.model_dump()
    return ItemResponse(id=item_id, **items[item_id])


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return {"message": f"Item {item_id} deleted"}
