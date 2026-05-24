from typing import Dict, Set, Optional, Any
from fastapi import WebSocket
from uuid import UUID
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # user_id -> websocket
        self.role_rooms: Dict[str, Set[str]] = {  # role -> set of user_ids
            "admin": set(),
            "warehouse_manager": set(),
            "vendor": set(),
            "delivery_personnel": set(),
        }
        self.broadcast_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, user_id: str, role: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        if role in self.role_rooms:
            self.role_rooms[role].add(user_id)
        self.broadcast_connections.add(websocket)

    def disconnect(self, user_id: str, role: str):
        ws = self.active_connections.pop(user_id, None)
        if role in self.role_rooms:
            self.role_rooms[role].discard(user_id)
        if ws in self.broadcast_connections:
            self.broadcast_connections.discard(ws)

    async def send_to_user(self, user_id: str, message: dict):
        ws = self.active_connections.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception:
                self.active_connections.pop(user_id, None)

    async def send_to_role(self, role: str, message: dict):
        user_ids = self.role_rooms.get(role, set())
        for user_id in user_ids:
            await self.send_to_user(user_id, message)

    async def broadcast(self, message: dict):
        for ws in list(self.broadcast_connections):
            try:
                await ws.send_json(message)
            except Exception:
                pass

    async def broadcast_shipment_update(self, shipment_id: str, status: str, tracking_number: str, location: Optional[str] = None):
        message = {
            "type": "shipment_update",
            "data": {
                "shipment_id": shipment_id,
                "tracking_number": tracking_number,
                "status": status,
                "location": location,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.broadcast(message)
        await self.send_to_role("admin", message)
        await self.send_to_role("delivery_personnel", message)

    async def broadcast_inventory_alert(self, product_id: str, product_name: str, current_stock: float, min_level: float):
        message = {
            "type": "inventory_alert",
            "data": {
                "product_id": product_id,
                "product_name": product_name,
                "current_stock": current_stock,
                "min_stock_level": min_level,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.send_to_role("admin", message)
        await self.send_to_role("warehouse_manager", message)

    async def broadcast_order_update(self, order_id: str, order_number: str, status: str):
        message = {
            "type": "order_update",
            "data": {
                "order_id": order_id,
                "order_number": order_number,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.broadcast(message)

    async def send_notification(self, user_id: str, notification: dict):
        message = {
            "type": "notification",
            "data": notification
        }
        await self.send_to_user(user_id, message)

    async def broadcast_dashboard_update(self, widget: str, data: Any):
        message = {
            "type": "dashboard_update",
            "data": {
                "widget": widget,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.send_to_role("admin", message)

manager = ConnectionManager()
