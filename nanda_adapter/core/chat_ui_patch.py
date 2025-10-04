"""
Chat UI Patch for python_a2a
Adds a working /tasks/send GET endpoint with a chat interface
"""

CHAT_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat with Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 800px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 20px 20px 0 0;
        }

        .header h1 { font-size: 2em; margin-bottom: 10px; }

        .chat {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
            background: #f8fafc;
        }

        .welcome {
            text-align: center;
            padding: 40px 20px;
            color: #64748b;
        }

        .message {
            margin-bottom: 20px;
            animation: slideIn 0.3s;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
        }

        .message-content {
            padding: 15px 20px;
            border-radius: 15px;
            max-width: 80%;
            line-height: 1.6;
        }

        .message.user { display: flex; justify-content: flex-end; }
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .message.agent { display: flex; justify-content: flex-start; }
        .message.agent .message-content {
            background: white;
            border: 2px solid #e2e8f0;
            white-space: pre-wrap;
        }

        .input-area {
            padding: 20px 30px;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 15px;
        }

        input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e2e8f0;
            border-radius: 25px;
            font-size: 1em;
            outline: none;
        }
        input:focus { border-color: #667eea; }

        button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            font-weight: 600;
        }
        button:hover { opacity: 0.9; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }

        .error {
            background: #fee2e2;
            color: #dc2626;
            padding: 15px;
            border-radius: 10px;
            margin: 15px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 Chat with Agent</h1>
            <p>Send messages and get responses</p>
        </div>

        <div class="chat" id="chat">
            <div class="welcome">
                <h2>Welcome!</h2>
                <p>Type your message below to start chatting...</p>
            </div>
        </div>

        <div class="input-area">
            <input type="text" id="input" placeholder="Type your message...">
            <button id="send">Send</button>
        </div>
    </div>

    <script>
        const API = '/a2a';
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');
        const sendBtn = document.getElementById('send');

        async function send() {
            const msg = input.value.trim();
            if (!msg) return;

            input.value = '';
            addMsg('user', msg);

            sendBtn.disabled = true;
            input.disabled = true;

            try {
                const res = await fetch(API, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        parts: [{ type: 'text', text: msg }],
                        role: 'user'
                    })
                });

                const data = await res.json();
                const text = data.parts?.[0]?.text || 'No response';

                // Remove [AGENT default] prefix if present
                const cleanText = text.replace(/^\\[AGENT default\\]\\s*/, '');
                addMsg('agent', cleanText);
            } catch (e) {
                addMsg('agent', 'Error: ' + e.message);
            }

            sendBtn.disabled = false;
            input.disabled = false;
            input.focus();
        }

        function addMsg(role, text) {
            const div = document.createElement('div');
            div.className = `message ${role}`;
            div.innerHTML = `<div class="message-content">${escapeHtml(text)}</div>`;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        sendBtn.onclick = send;
        input.onkeypress = e => e.key === 'Enter' && send();
        input.focus();
    </script>
</body>
</html>
"""


def add_chat_ui_route(app):
    """
    Add a GET handler for /tasks/send that shows a chat UI

    Call this function after creating the Flask app to patch in the chat UI
    """
    from flask import Response

    @app.route("/tasks/send", methods=["GET"])
    def send_task_ui():
        """Render the chat UI"""
        return Response(CHAT_UI_HTML, mimetype='text/html')

    print("✅ Added /tasks/send GET handler with chat UI")
    return app
