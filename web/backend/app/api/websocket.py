"""
AI教师Agent Web后端 - WebSocket 频道处理器
实现多教师多学生实时授课功能
"""
import json
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.security import decode_access_token

router = APIRouter(tags=["WebSocket"])


class ChannelManager:
    """
    频道连接管理器
    维护所有活跃频道的 WebSocket 连接
    """

    def __init__(self):
        # channel_id -> Set[WebSocket]
        self.channel_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> user info
        self.ws_user: Dict[WebSocket, dict] = {}

    async def connect(self, channel_id: str, websocket: WebSocket, user_info: dict):
        """客户端连接到频道"""
        await websocket.accept()

        if channel_id not in self.channel_connections:
            self.channel_connections[channel_id] = set()

        self.channel_connections[channel_id].add(websocket)
        self.ws_user[websocket] = {**user_info, "channel_id": channel_id}

        # 通知其他成员有新用户加入
        await self.broadcast(channel_id, {
            "type": "member_join",
            "data": {
                "user_id": user_info["user_id"],
                "name": user_info.get("name", "未知用户"),
                "role": user_info.get("role", "student"),
            }
        }, exclude=websocket)

    def disconnect(self, websocket: WebSocket):
        """客户端断开连接"""
        user_info = self.ws_user.pop(websocket, {})
        channel_id = user_info.get("channel_id")

        if channel_id and channel_id in self.channel_connections:
            self.channel_connections[channel_id].discard(websocket)
            if not self.channel_connections[channel_id]:
                del self.channel_connections[channel_id]

        return user_info

    async def broadcast(
        self,
        channel_id: str,
        message: dict,
        exclude: WebSocket = None
    ):
        """向频道内所有连接广播消息"""
        if channel_id not in self.channel_connections:
            return

        dead_connections = set()
        data = json.dumps(message, ensure_ascii=False)

        for ws in self.channel_connections[channel_id]:
            if ws == exclude:
                continue
            try:
                await ws.send_text(data)
            except Exception:
                dead_connections.add(ws)

        # 清理死连接
        for ws in dead_connections:
            self.disconnect(ws)

    def get_channel_members(self, channel_id: str) -> list:
        """获取频道当前成员列表"""
        members = []
        for ws, info in self.ws_user.items():
            if info.get("channel_id") == channel_id:
                members.append({
                    "user_id": info["user_id"],
                    "name": info.get("name", "未知"),
                    "role": info.get("role", "student"),
                })
        return members


# 全局频道管理器
channel_manager = ChannelManager()


@router.websocket("/ws/channel/{channel_id}")
async def websocket_channel(
    websocket: WebSocket,
    channel_id: str,
    token: str = Query(...),
):
    """
    WebSocket 频道端点
    教师和学生通过此端点连接到实时授课频道

    消息协议：
    发送：{"type": "page_sync", "data": {"page": 0}}
    接收：{"type": "member_join", "data": {"user_id": 1, "name": "张老师", "role": "teacher"}}
    """
    # 验证 token
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="无效的令牌")
        return

    user_info = {
        "user_id": int(payload.get("sub")),
        "role": payload.get("role", "student"),
        "name": payload.get("name", "用户"),
    }

    await channel_manager.connect(channel_id, websocket, user_info)

    # 发送当前频道成员列表给新连接的用户
    members = channel_manager.get_channel_members(channel_id)
    await websocket.send_text(json.dumps({
        "type": "channel_state",
        "data": {
            "members": members,
            "channel_id": channel_id,
        }
    }, ensure_ascii=False))

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")
            msg_data = msg.get("data", {})

            # 处理不同类型消息
            if msg_type == "page_sync":
                # 教师同步课件页码给所有学生
                await channel_manager.broadcast(channel_id, {
                    "type": "page_sync",
                    "data": {
                        "page": msg_data.get("page", 0),
                        "sender_id": user_info["user_id"],
                    }
                }, exclude=websocket)

            elif msg_type == "chat":
                # 聊天消息广播给所有人
                await channel_manager.broadcast(channel_id, {
                    "type": "chat",
                    "data": {
                        "content": msg_data.get("content", ""),
                        "sender_id": user_info["user_id"],
                        "sender_name": user_info.get("name", "用户"),
                        "sender_role": user_info["role"],
                    }
                })

            elif msg_type == "quiz_start":
                # 教师发起随堂测试
                if user_info["role"] in ("teacher", "admin"):
                    await channel_manager.broadcast(channel_id, {
                        "type": "quiz_start",
                        "data": {
                            "exercise_id": msg_data.get("exercise_id"),
                            "teacher_id": user_info["user_id"],
                        }
                    }, exclude=websocket)

            elif msg_type == "quiz_answer":
                # 学生提交答案，通知教师端统计
                await channel_manager.broadcast(channel_id, {
                    "type": "quiz_answer",
                    "data": {
                        "student_id": user_info["user_id"],
                        "exercise_id": msg_data.get("exercise_id"),
                        "answer": msg_data.get("answer"),
                    }
                })

            elif msg_type == "ping":
                # 心跳保活
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        user_info = channel_manager.disconnect(websocket)
        # 通知其他成员有用户离开
        await channel_manager.broadcast(channel_id, {
            "type": "member_leave",
            "data": {
                "user_id": user_info.get("user_id"),
                "name": user_info.get("name", "未知用户"),
            }
        })
    except Exception as e:
        channel_manager.disconnect(websocket)
