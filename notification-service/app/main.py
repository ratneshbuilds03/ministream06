import os
from flask import Flask, request, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"ok",
                    "service":"notification-service",
                    "port":5001
                    })
    

@app.route("/notify/new-content",methods=["POST"])
def notify_new_content():
    data = request.get_json()
    creator_name = data.get("creator_name")
    content_title = data.get("content_title")
    subscribers= data.get("subscribers",[])
    
    logger.info(f"NEW CONTENT NOTIFICATION")
    logger.info(f"Creator:{creator_name}")
    logger.info(f"Content:{content_title}")
    logger.info(f"Notifying {len(subscribers)} subscribers")
    
    for email in subscribers:
        logger.info(f" -> Email sent to: {email}")
        
    return jsonify({
        "message":"Notifications sent",
        "notified_count":len(subscribers)
    }),200
    

@app.route("/notify/new-follower",methods=["POST"])
def notify_new_follower():
    data = request.get_json()
    follower_name = data.get("follower_name")
    creator_email = data.get("creator_email")
    
    logger.info(f"NEW FOLLOWER: {follower_name} -> {creator_email}")
    return jsonify({"message":"Notification sent "}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT",5001))
    app.run(host="0.0.0.0", port=5001, debug=False)