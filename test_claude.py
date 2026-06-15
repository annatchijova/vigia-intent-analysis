from anthropic import AnthropicVertex

project_id = "vigia-497422"
region = "global"

client = AnthropicVertex(project_id=project_id, region=region)

message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Hey Claude!"}
    ],
)
print(message)
