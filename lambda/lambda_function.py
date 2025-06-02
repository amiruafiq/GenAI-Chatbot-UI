import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client('bedrock-agent-runtime')

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    # ✅ Handle CORS preflight
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'message': 'CORS preflight OK'})
        }

    try:
        # Parse input
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)

        user_input = body.get("question", "")
        logger.info(f"Original user input: {user_input}")

        # ✅ Add tone instruction (this helps humanize the output)
        friendly_input = f"Reply in a friendly and casual tone, like a customer support agent chatting on WhatsApp: {user_input}"
        logger.info(f"Modified input for Bedrock: {friendly_input}")

        # Call Bedrock with modified input
        response = bedrock.retrieve_and_generate(
            input={"text": friendly_input},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": "W9P1ZJVX9P",
                    "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0"
                }
            }
        )

        raw_answer = response.get("output", {}).get("text", "No answer returned")
        logger.info(f"Raw model answer: {raw_answer}")

        # ✅ Optional post-process: Make sure reply ends friendly
        if not raw_answer.strip().endswith(("!", ".", "?")):
            raw_answer = raw_answer.strip() + " 🙂"

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'answer': raw_answer})
        }

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'error': str(e)})
        }
