from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.orchestrator import LiveDebateOrchestrator
from core.message_queue import MessageQueue
import asyncio
import json

router = APIRouter()

_active_sessions: dict[str, dict] = {}


@router.websocket("/ws/debate/{session_id}")
async def websocket_debate(websocket: WebSocket, session_id: str):
    await websocket.accept()

    stop_event = asyncio.Event()
    message_queue = MessageQueue(session_id)
    _active_sessions[session_id] = {
        "stop_event": stop_event,
        "message_queue": message_queue,
    }

    orchestrator = LiveDebateOrchestrator()

    try:
        # First message from client contains the prompt
        data = await websocket.receive_text()
        data_json = json.loads(data)
        prompt = data_json.get("prompt", "")

        async def stream_to_ws(
            agent_name: str,
            chunk: str,
            is_synthesis: bool = False,
            is_status: bool = False,
        ):
            try:
                if is_status:
                    await websocket.send_text(
                        json.dumps({"type": "status", "message": chunk})
                    )
                    return
                msg_type = "synthesis_chunk" if is_synthesis else "agent_chunk"
                await websocket.send_text(
                    json.dumps({"type": msg_type, "agent": agent_name, "content": chunk})
                )
            except Exception:
                pass

        await websocket.send_text(
            json.dumps({"type": "status", "message": "Debate starting..."})
        )

        # Run the infinite debate loop as a background task
        debate_task = asyncio.create_task(
            orchestrator.run_debate(
                session_id,
                prompt,
                ws_callback=stream_to_ws,
                stop_event=stop_event,
                message_queue=message_queue,
            )
        )

        # Listen for client commands: stop, user_message, correction
        async def listen_for_client():
            while not stop_event.is_set():
                try:
                    raw = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                    msg = json.loads(raw)

                    if msg.get("type") == "stop":
                        stop_event.set()
                        break

                    elif msg.get("type") == "user_message":
                        # User sent a question or comment mid-debate
                        content = msg.get("content", "").strip()
                        if content:
                            await message_queue.user_injection_queue.put({
                                "content": content,
                                "is_correction": False,
                            })

                    elif msg.get("type") == "correction":
                        # User is correcting a previous agent response
                        content = msg.get("content", "").strip()
                        if content:
                            await message_queue.user_injection_queue.put({
                                "content": content,
                                "is_correction": True,
                            })

                    elif msg.get("type") == "export":
                        # Client requests full conversation text
                        all_msgs = await message_queue.get_all()
                        export_text = "\n\n".join(
                            [f"[{m.agent_name}]: {m.content}" for m in all_msgs]
                        )
                        await websocket.send_text(
                            json.dumps({"type": "export_data", "content": export_text})
                        )

                except asyncio.TimeoutError:
                    continue
                except Exception:
                    break

        listener_task = asyncio.create_task(listen_for_client())

        result = await debate_task
        listener_task.cancel()

        # Send full conversation for the copy feature on completion
        all_msgs = await message_queue.get_all()
        full_text = "\n\n".join([f"[{m.agent_name}]: {m.content}" for m in all_msgs])

        await websocket.send_text(
            json.dumps({
                "type": "complete",
                "rounds": result.get("rounds_completed", 0),
                "status": result.get("status", "stopped"),
                "full_conversation": full_text,
            })
        )

    except WebSocketDisconnect:
        stop_event.set()
        print(f"[Session {session_id}] Client disconnected — debate stopped.")
    except Exception as e:
        stop_event.set()
        print(f"[Session {session_id}] Error: {e}")
        try:
            await websocket.send_text(
                json.dumps({"type": "error", "message": str(e)})
            )
        except Exception:
            pass
    finally:
        _active_sessions.pop(session_id, None)
