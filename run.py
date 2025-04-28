from app import create_app, socketio
import os


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
